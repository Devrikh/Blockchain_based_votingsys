# node.py (Streamlit-only, MPI-safe, non-blocking)
from mpi4py import MPI
from blockchain import Blockchain, Block
from colorama import Fore, Style, init
import time, json, os

# Initialize color output
init(autoreset=True, convert=True)

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

chain = Blockchain()
NUM_ROUNDS = 5
VOTES_FILE = "pending_votes.json"

# Load votes from Streamlit UI
def load_ui_votes():
    if not os.path.exists(VOTES_FILE):
        return []
    try:
        with open(VOTES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

# Clear votes after processing
def clear_ui_votes():
    with open(VOTES_FILE, "w") as f:
        json.dump([], f)

# Main consensus loop
for round_no in range(NUM_ROUNDS):
    leader = round_no % size
    time.sleep(0.2)  # simulate network delay

    # ---- LEADER NODE ----
    if rank == leader:
        # Load votes
        ui_votes = load_ui_votes()
        vote_count = len(ui_votes)
        if vote_count > 0:
            print(Fore.GREEN + f"[Leader {rank}] Proposing block for round {round_no} with {vote_count} votes")
            clear_ui_votes()
        else:
            print(Fore.YELLOW + f"[Leader {rank}] No votes submitted this round {round_no}, proposing empty block")

        # Prepare proposal (can be empty)
        proposal_data = {"votes": ui_votes, "proposer": leader}

        # Broadcast proposal to non-leaders
        for i in range(size):
            if i != rank:
                comm.send(proposal_data, dest=i, tag=100 + round_no)

        # Collect approvals from non-leaders
        yes_votes = 1  # leader auto-approves
        for i in range(size):
            if i != rank:
                resp = comm.recv(source=i, tag=200 + round_no)
                if resp == "YES":
                    yes_votes += 1

        # Commit block if majority approves and there are votes
        if vote_count > 0 and yes_votes > size // 2:
            last_block = chain.chain[-1]
            new_block = Block(index=last_block.index + 1,
                              prev_hash=last_block.hash,
                              votes=ui_votes,
                              proposer=leader)
            chain.add_block(new_block)
            print(Fore.GREEN + f"[Leader {rank}] Block committed ({yes_votes}/{size} approvals)")
        elif vote_count == 0:
            print(Fore.YELLOW + f"[Leader {rank}] No votes to commit this round")
        else:
            print(Fore.RED + f"[Leader {rank}] Block rejected ({yes_votes}/{size})")

    # ---- NON-LEADER NODES ----
    else:
        # Receive proposal
        proposal = comm.recv(source=leader, tag=100 + round_no)

        # Decide approval
        if not proposal["votes"]:
            decision = "NO"  # no votes, cannot commit
        else:
            decision = "YES"  # approve all UI votes

        # Send decision back to leader
        comm.send(decision, dest=leader, tag=200 + round_no)

        # Commit block locally if approved and votes exist
        if proposal["votes"] and decision == "YES":
            last_block = chain.chain[-1]
            new_block = Block(index=last_block.index + 1,
                              prev_hash=last_block.hash,
                              votes=proposal["votes"],
                              proposer=proposal["proposer"])
            chain.add_block(new_block)
            print(Fore.CYAN + f"[Node {rank}] Block committed")
        elif not proposal["votes"]:
            print(Fore.MAGENTA + f"[Node {rank}] No proposal votes, skipping commit")

    time.sleep(0.2)

# End of rounds
time.sleep(1)
if rank == 0:
    print(Style.BRIGHT + "\n=== Final Blockchain ===")
    for block in chain.chain:
        print(f"Block {block.index}: proposer={block.proposer}, votes={len(block.votes)}")
    chain.print_results()

# Save blockchain to JSON for each node
output_folder = "chain_rank_json"
os.makedirs(output_folder, exist_ok=True)
output_filename = os.path.join(output_folder, f"chain_rank_{rank}.json")
with open(output_filename, "w") as f:
    json.dump([b.__dict__ for b in chain.chain], f, indent=4)
print(Fore.MAGENTA + f"[Node {rank}] Blockchain saved to {output_filename}")

MPI.Finalize()
