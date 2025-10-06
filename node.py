from mpi4py import MPI
from blockchain import Blockchain, Block
from colorama import Fore, Style, init
import time
import random
import json
import os

# Initialize color output
init(autoreset=True, convert=True)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

chain = Blockchain()
NUM_ROUNDS = 5  # Number of consensus rounds
CANDIDATES = ["Alice", "Bob", "Carol"]

# Predefined votes for leaders (one per round)
predefined_leader_votes = ["Alice", "Bob", "Carol", "Alice", "Bob"]

# Folder to store blockchain JSON
output_folder = "chain_rank_json"
os.makedirs(output_folder, exist_ok=True)

def get_leader_vote(round_no):
    """
    Return a predefined vote for the leader based on the round number.
    """
    choice = predefined_leader_votes[round_no % len(predefined_leader_votes)]
    voter_id = f"L{rank}_R{round_no}"
    print(Fore.GREEN + f"[Leader {rank}] Vote: {choice} (voter ID: {voter_id})")
    return {"voter": voter_id, "choice": choice}

# Main consensus loop
for round_no in range(NUM_ROUNDS):
    leader = round_no % size
    time.sleep(random.uniform(0.2, 0.8))  # Network delay simulation

    # ---- LEADER NODE ----
    if rank == leader:
        print(Fore.GREEN + f"[Leader {rank}] Proposing block for round {round_no}")

        # Leader vote (predefined)
        votes = [get_leader_vote(round_no)]

        # Collect votes from other nodes
        collected_votes = [votes]
        for i in range(size):
            if i != rank:
                data = comm.recv(source=i, tag=round_no)
                collected_votes.append(data)

        all_votes = [vote for node_votes in collected_votes for vote in node_votes]

        # Broadcast proposal
        proposal_data = {"votes": all_votes, "proposer": leader}
        for i in range(size):
            if i != rank:
                comm.send(proposal_data, dest=i, tag=100 + round_no)

        # Collect approvals
        yes_votes = 1  # leader auto-approves
        for i in range(size):
            if i != rank:
                resp = comm.recv(source=i, tag=200 + round_no)
                if resp == "YES":
                    yes_votes += 1

        # Commit block if majority approves
        if yes_votes > size // 2:
            last_block = chain.chain[-1]
            new_block = Block(index=last_block.index + 1,
                              prev_hash=last_block.hash,
                              votes=all_votes,
                              proposer=leader)
            chain.add_block(new_block)
            print(Fore.YELLOW + f"[Leader {rank}] Block committed with {yes_votes}/{size} approvals")
        else:
            print(Fore.RED + f"[Leader {rank}] Block rejected (only {yes_votes}/{size} YES votes)")

    # ---- NON-LEADER NODES ----
    else:
        # Generate random vote for this node
        votes = [{"voter": f"V{rank}_R{round_no}", "choice": random.choice(CANDIDATES)}]
        comm.send(votes, dest=leader, tag=round_no)

        # Receive block proposal from leader
        proposal = comm.recv(source=leader, tag=100 + round_no)
        time.sleep(random.uniform(0.2, 0.5))

        # Randomly approve/reject
        decision = random.choice(["YES", "YES", "NO"])
        comm.send(decision, dest=leader, tag=200 + round_no)

        if decision == "YES":
            last_block = chain.chain[-1]
            new_block = Block(index=last_block.index + 1,
                              prev_hash=last_block.hash,
                              votes=proposal["votes"],
                              proposer=proposal["proposer"])
            chain.add_block(new_block)
            print(Fore.CYAN + f"[Node {rank}] Block committed!")
        else:
            print(Fore.MAGENTA + f"[Node {rank}] Block rejected proposal from Leader {leader}")

    time.sleep(random.uniform(0.3, 0.7))

# ---- END OF ROUNDS ----
time.sleep(1)

# Final blockchain display
if rank == 0:
    print(Style.BRIGHT + "\n=== Final Blockchain ===")
    for block in chain.chain:
        print(f"Block {block.index}: proposer={block.proposer}, votes={len(block.votes)}")

    # Print vote counts per candidate
    chain.print_results()

# Export blockchain JSON
output_filename = os.path.join(output_folder, f"chain_rank_{rank}.json")
with open(output_filename, "w") as f:
    json.dump([b.__dict__ for b in chain.chain], f, indent=4)
print(Fore.MAGENTA + f"[Node {rank}] Blockchain saved to {output_filename}")

MPI.Finalize()
