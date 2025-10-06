# Blockchain-Based Voting System

## 1. Project Overview

**Project Name:** Blockchain-Based Voting System  

**Technology Stack:**
- **MPI (Message Passing Interface):** Distributed consensus among nodes  
- **Python:** Blockchain logic and CLI interface  
- **JSON:** Export blockchain data per node  

**Project Goal:**  
To implement a secure, distributed voting system where each MPI process maintains part of the blockchain ledger. The system demonstrates a parallel and distributed application using MPI for consensus.

---

## 2. Problem Statement

- Develop a **secure voting system** that records votes in a blockchain.  
- Each MPI node acts as a participant in the network:  
  - **Leader node** proposes a block of votes.  
  - **Non-leader nodes** validate and approve/reject the block.  
- After several rounds, the blockchain is finalized and vote results are computed.  

---

## 3. Features

1. **Distributed Blockchain Ledger**  
   - Each node maintains its own copy of the blockchain.  
   - Blocks contain:
     - Index
     - Previous block hash
     - Votes in that block
     - Proposer (leader) ID
     - Timestamp
     - Hash of the block  

2. **Voting Interface**  
   - Leader node’s vote is **predefined for demo purposes**.  
   - Non-leader nodes generate **random votes automatically**.  

3. **MPI Communication & Consensus**  
   - Leaders propose blocks.  
   - Nodes approve/reject proposals.  
   - Majority approval commits a block.  

4. **CLI Output**  
   - Status messages indicate:
     - Leader proposing block
     - Block committed
     - Block rejected  

5. **JSON Export**  
   - Each node saves its blockchain to `chain_rank_json/chain_rank_<rank>.json`.  

6. **Vote Count Summary**  
   - Rank 0 prints final vote tally per candidate.  

---

## 4. Project Structure

```
Blockchain_Based_VotingSys/
│
├─ blockchain.py        # Blockchain and block definitions
├─ mpi_test.py          # For testing MPI
├─ node.py              # MPI-based voting simulation (CLI)
├─ chain_rank_json/     # Output folder for blockchain JSONs
│   ├─ chain_rank_0.json
│   ├─ chain_rank_1.json
│   └─ ...
└─ README.md            # Project documentation
```

---

## 5. How It Works

1. **Initialization**
   - `MPI.COMM_WORLD` initializes N processes (nodes).  
   - Each node creates its own blockchain instance (with genesis block).  

2. **Consensus Loop**
   - Total rounds = `NUM_ROUNDS`  
   - **Leader Node (round_no % size):**
     - Picks predefined vote for demo.  
     - Collects votes from other nodes (simulated).  
     - Broadcasts block proposal.  
     - Collects approval votes.  
     - Commits block if majority approves.  
   - **Non-Leader Nodes:**
     - Generate random vote.  
     - Send vote to leader.  
     - Receive proposal.  
     - Randomly approve/reject.  
     - Add block if approved.  

3. **Final Blockchain**
   - Rank 0 prints all blocks.  
   - Vote count per candidate is displayed.  

4. **JSON Export**
   - Each node saves its blockchain as a JSON file.  

---

## 6. Instructions to Run

### Prerequisites
- Python 3.8+
- `mpi4py` installed (`pip install mpi4py`)
- `colorama` (optional, for colors, can be skipped)
- MPI installed on Windows (MS-MPI) or Linux/Mac

### Step 1: Open Terminal
- Navigate to the project folder containing `node.py` and `blockchain.py`

### Step 2: Run Simulation
- Execute the following command for 4 nodes (processes):

```bash
mpiexec -n 4 python node.py
```

### Step 3: Observe CLI Output
- Leader proposes blocks and displays its predefined vote.  
- Non-leader nodes simulate votes and approve/reject the block.  
- Blocks committed or rejected are printed per node.  
- Rank 0 displays final blockchain and voting results.  
- All nodes save blockchain JSON files in `chain_rank_json/`.

### Step 4: Check Output JSON
- Each node will create a file:
  - `chain_rank_json/chain_rank_0.json`
  - `chain_rank_json/chain_rank_1.json`
  - ... etc.
- These contain the full blockchain stored by each node.

### Step 5: Modify Simulation Parameters (Optional)
- Change `NUM_ROUNDS` in `node.py` to increase/decrease rounds.  
- Modify `CANDIDATES` list in `node.py` to add/remove candidates.  
- Predefined leader votes can be edited in `predefined_leader_votes` list.  

---

## 7. Sample Output

```
[Leader 0] Proposing block for round 0
[Leader 0] Vote: Alice (voter ID: L0_R0)
[Node 1] Block committed!
[Node 2] Block rejected proposal from Leader 0
[Node 3] Block committed!

[Leader 0] Block committed with 3/4 approvals
...
=== Final Blockchain ===
Block 0: proposer=Genesis, votes=0
Block 1: proposer=0, votes=4
Block 2: proposer=1, votes=3

=== Final Voting Results ===
Alice: 4 vote(s)
Bob: 2 vote(s)
Carol: 1 vote(s)
```

---

## 8. Advantages
- Demonstrates **parallel processing with MPI**.  
- Shows **distributed consensus mechanism** using blockchain.  
- CLI is lightweight and easy to demo.  
- JSON export allows verification of blockchain integrity.

---

## 9. Possible Extensions
- Replace predefined votes with **real-time user input** in multi-terminal setup.  
- Add **digital signatures** to votes for security.  
- Implement **more complex consensus protocols** (PBFT, Raft).  
- Use **persistent storage** for blockchain instead of in-memory objects.
