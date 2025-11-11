from flask import Flask, request, jsonify
from mpi4py import MPI
from blockchain import Blockchain, Block
import threading
import time
import json
import os
import signal
import sys
from datetime import datetime

# MPI + Flask Setup
app = Flask(__name__)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

chain = Blockchain()
pending_votes = []
running = True
round_no = 0
MAJORITY = lambda n: (n // 2) + 1

# ------------------------------
# Flask Endpoints
# ------------------------------
@app.route('/vote', methods=['POST'])
def receive_vote():
    vote_data = request.get_json()
    if not isinstance(vote_data, dict) or "voter" not in vote_data or "choice" not in vote_data:
        return jsonify({"error": "Invalid vote format"}), 400

    if "timestamp" not in vote_data:
        vote_data["timestamp"] = str(datetime.now())

    pending_votes.append(vote_data)
    print(f"[Node {rank}] Received vote: {vote_data}", flush=True)
    return jsonify({"status": "Vote received", "node": rank}), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    return jsonify([b.__dict__ for b in chain.chain]), 200

@app.route('/pending', methods=['GET'])
def get_pending():
    return jsonify(pending_votes), 200

@app.route('/results', methods=['GET'])
def results():
    tally = chain.count_votes()
    resp = {
        "node": rank,
        "blocks": len(chain.chain),
        "votes_total": sum(tally.values()) if tally else 0,
        "tally": tally,
        "latest_block": chain.chain[-1].__dict__ if chain.chain else None
    }
    return jsonify(resp), 200

# ------------------------------
# Consensus Loop
# ------------------------------
def consensus_loop():
    global running, round_no
    print(f"[Node {rank}] Consensus loop started (size={size})", flush=True)

    while running:
        leader = round_no % size
        time.sleep(1)

        if rank == leader:
            if not pending_votes:
                comm.bcast(None, root=leader)
                round_no += 1
                continue

            timestamp = str(datetime.now())
            new_block = Block(
                index=len(chain.chain),
                prev_hash=chain.chain[-1].hash,
                votes=pending_votes.copy(),
                proposer=rank
            )
            new_block.timestamp = timestamp
            new_block.hash = new_block.calculate_hash()

            proposal_data = {
                "index": new_block.index,
                "prev_hash": new_block.prev_hash,
                "votes": new_block.votes,
                "proposer": new_block.proposer,
                "timestamp": new_block.timestamp,
                "hash": new_block.hash,
                "round": round_no
            }

            comm.bcast(proposal_data, root=leader)

            yes_count = 1
            for src in range(size):
                if src == rank:
                    continue
                try:
                    resp = comm.recv(source=src, tag=200 + round_no)
                    if isinstance(resp, dict) and resp.get("round") == round_no and resp.get("vote") == "YES":
                        yes_count += 1
                except Exception as e:
                    print(f"[Leader {rank}] Error receiving approval from {src}: {e}", flush=True)

            if yes_count >= MAJORITY(size):
                commit_payload = {"commit": True, "block": proposal_data, "round": round_no}
                chain.add_block(new_block)
                pending_votes.clear()
                print(f"[Leader {rank}] Block committed locally as #{new_block.index} (round {round_no})", flush=True)
                save_chain_to_json()
            else:
                commit_payload = {"commit": False, "reason": "not enough approvals", "round": round_no}
                print(f"[Leader {rank}] Block rejected ({yes_count}/{size} approvals) (round {round_no})", flush=True)

            comm.bcast(commit_payload, root=leader)
            round_no += 1

        else:
            proposal = comm.bcast(None, root=leader)
            if not proposal:
                round_no += 1
                continue

            valid_link = (proposal["prev_hash"] == chain.chain[-1].hash)
            candidate = Block(
                index=proposal["index"],
                prev_hash=proposal["prev_hash"],
                votes=proposal["votes"],
                proposer=proposal["proposer"]
            )
            candidate.timestamp = proposal["timestamp"]
            valid_hash = (candidate.calculate_hash() == proposal["hash"])

            vote_decision = "YES" if (valid_link and valid_hash) else "NO"
            comm.send({"round": proposal.get("round", round_no), "vote": vote_decision, "node": rank}, dest=leader, tag=200 + proposal.get("round", round_no))
            print(f"[Node {rank}] Sent {vote_decision} to Leader {leader} (round {proposal.get('round', round_no)})", flush=True)

            commit_payload = comm.bcast(None, root=leader)
            if commit_payload.get("commit"):
                blk = commit_payload["block"]
                follower_block = Block(
                    index=blk["index"],
                    prev_hash=blk["prev_hash"],
                    votes=blk["votes"],
                    proposer=blk["proposer"]
                )
                follower_block.timestamp = blk["timestamp"]
                follower_block.hash = blk["hash"]

                if follower_block.prev_hash == chain.chain[-1].hash and follower_block.hash == follower_block.calculate_hash():
                    chain.add_block(follower_block)
                    print(f"[Node {rank}] Added Block #{follower_block.index} from Leader {leader} (round {commit_payload.get('round')})", flush=True)
                    save_chain_to_json()
                else:
                    print(f"[Node {rank}] Failed to add block from Leader {leader} — validation failed", flush=True)
            else:
                print(f"[Node {rank}] Leader {leader} aborted commit (round {commit_payload.get('round')}): {commit_payload.get('reason')}", flush=True)

            round_no += 1

# ------------------------------
# Flask & Shutdown
# ------------------------------
def start_flask():
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5000 + rank, debug=False, use_reloader=False)

def signal_handler(sig, frame):
    global running
    running = False
    sys.exit(0)

def save_chain_to_json():
    os.makedirs("chain_rank_json", exist_ok=True)
    try:
        with open(f"chain_rank_json/chain_rank_{rank}.json", "w") as f:
            json.dump([b.__dict__ for b in chain.chain], f, indent=4)
        print(f"[Node {rank}] Blockchain saved to chain_rank_{rank}.json", flush=True)
    except Exception as e:
        print(f"[Node {rank}] Error saving chain JSON: {e}", flush=True)

# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(2)

    print(f"[Node {rank}] Flask server started on port {5000 + rank}", flush=True)
    consensus_loop()
