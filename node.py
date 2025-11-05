# node.py — Live Blockchain Node (with Flask RPC + MPI)
from flask import Flask, request, jsonify
from mpi4py import MPI
from blockchain import Blockchain, Block
import threading
import time
import json
import os
import signal
import sys

# ------------------------------
# MPI + Flask Setup
# ------------------------------
app = Flask(__name__)
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

# Global state
chain = Blockchain()
pending_votes = []
running = True


# ------------------------------
# Flask Endpoints (RPC)
# ------------------------------
@app.route('/vote', methods=['POST'])
def receive_vote():
    """Receive new vote via REST"""
    vote_data = request.get_json()
    pending_votes.append(vote_data)
    print(f"[Node {rank}] Received vote: {vote_data}")
    return jsonify({"status": "Vote received", "node": rank}), 200


@app.route('/chain', methods=['GET'])
def get_chain():
    """Return blockchain"""
    return jsonify([b.__dict__ for b in chain.chain]), 200


@app.route('/pending', methods=['GET'])
def get_pending():
    """Return pending votes"""
    return jsonify(pending_votes), 200


# ------------------------------
# Consensus Loop (Rotating Leader)
# ------------------------------
def consensus_loop():
    global running
    print(f"[Node {rank}] Consensus loop started")

    while running:
        leader = int(time.time() // 10) % size  # Rotate leader every 10 seconds
        time.sleep(1)

        # ---- Leader node proposes block ----
        if rank == leader and pending_votes:
            print(f"\n[Leader {rank}] Pr    oposing block with {len(pending_votes)} votes...")

            new_block = Block(
                index=len(chain.chain),
                prev_hash=chain.chain[-1].hash,
                votes=pending_votes.copy(),
                proposer=rank
            )
            pending_votes.clear()

            comm.bcast(new_block.__dict__, root=leader)
            chain.add_block(new_block)
            print(f"[Leader {rank}] Broadcasted and added Block #{new_block.index}")

        # ---- Non-leader nodes receive block ----
        else:
            proposal = comm.bcast(None, root=leader)
            if proposal:
                new_block = Block(
                    index=proposal['index'],
                    prev_hash=proposal['prev_hash'],
                    votes=proposal['votes'],
                    proposer=proposal['proposer']
                )
                if new_block.prev_hash == chain.chain[-1].hash:
                    chain.add_block(new_block)
                    print(f"[Node {rank}] Added Block #{new_block.index} from leader {leader}")

        # ---- Save periodically ----
        if int(time.time()) % 10 == 0:
            os.makedirs("chain_rank_json", exist_ok=True)
            with open(f"chain_rank_json/chain_rank_{rank}.json", "w") as f:
                json.dump([b.__dict__ for b in chain.chain], f, indent=4)


# ------------------------------
# Threading & Shutdown
# ------------------------------
def start_flask():
    app.run(host='0.0.0.0', port=5000 + rank, debug=False, use_reloader=False)


def signal_handler(sig, frame):
    global running
    print(f"\n[Node {rank}] Shutting down...")
    running = False
    sys.exit(0)


# ------------------------------
# Main
# ------------------------------
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    # Run Flask server in background thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Give Flask time to start
    time.sleep(2)

    print(f"[Node {rank}] Started on port {5000 + rank}")
    print(f"[Node {rank}] Listening for incoming votes...")

    # Start consensus loop
    consensus_loop()
