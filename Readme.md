# 🗳️ Blockchain-Based Voting System (Flask + MPI)
## 1. Project Overview
**Project Name:** Blockchain-Based Voting System
**Objective:** To implement a **secure, distributed voting platform** combining **Flask (frontend API)**
and **MPI (backend consensus)**.
Each node:
- Runs a **Flask server** for receiving votes.
- Participates in the **blockchain network** using MPI for synchronization and consensus.
---
## 2. Technology Stack
| Layer | Technology | Purpose |
|-------|-------------|----------|
| Frontend | Flask (Python) | Vote submission UI |
| Backend | MPI (mpi4py) | Blockchain synchronization and consensus |
| Data | Python + JSON | Blockchain storage and verification |
| Optional | Colorama | CLI color formatting |
---
## 3. System Architecture
### Components:
1. **`ui.py` (Frontend):**
- Provides a web interface for casting votes.
- Sends votes to the corresponding node’s Flask API.
2. **`node.py` (Backend Node):**
- Each MPI process launches a Flask app.
- Collects votes locally.
- Uses MPI to synchronize blockchain across all ranks.
3. **`blockchain.py`:**
- Defines `Block` and `Blockchain` classes.
- Handles hashing, linking, and validation logic.
4. **`requirements.txt`:**
- Lists required dependencies for easy setup.
---
## 4. System Flow
### Step 1. Vote Collection (Frontend → Flask)
Users submit votes using the **UI interface** by running:
```bash
streamlit run ui.py
```
This opens a web-based voting page where users can input their voter ID and select their candidate.
---
### Step 2. Block Proposal (Leader Node via MPI)
- The current leader (based on round) gathers pending votes.
- Forms a new block and broadcasts it to all nodes.
### Step 3. Validation (Peer Nodes)
- Nodes verify:
- Hash continuity (`prev_hash` == previous block’s hash)
- Integrity (`recomputed_hash` == stored hash)
- If valid → block appended
- Else → block rejected
### Step 4. Synchronization
All nodes maintain identical blockchain copies after valid proposals.
### Step 5. Results Display
After simulation:
- Rank 0 displays the final blockchain and vote tally.
- Each node saves its blockchain in `chain_rank_json/chain_rank_.json`.
---
## 5. Project Structure
```
Blockchain_Voting_System/
│
├─ blockchain.py           # Blockchain and Block logic
├─ node.py                 # MPI + Flask integration (backend)
├─ ui.py                   # Flask web UI for voting
├─ chain_rank_json/        # JSON blockchain outputs per node
│   ├─ chain_rank_0.json
│   ├─ chain_rank_1.json
│   └─ ...
├─ requirements.txt        # Python dependencies
└─ README.md               # Project documentation
```
---
## 6. How to Run
### Step 1: Install Requirements
```bash
pip install -r requirements.txt
```
### Step 2: Run the MPI Network
Start N blockchain nodes (example: 3 nodes):
```bash
mpiexec -n 3 python node.py
```
Each node’s Flask app will run on:
```
Node 0 → localhost:5000
Node 1 → localhost:5001
Node 2 → localhost:5002
```
### Step 3: Run the UI (Frontend)
```bash
streamlit run ui.py
```
This launches the **Streamlit-based web voting interface** in your browser.
### Step 4: Observe Logs
Example console output:
```
[Leader 1] Proposing block with 2 votes...
[Leader 1] Broadcasted and added Block #1
[Node 0] Added Block #1 from Leader 1
[Node 2] Rejected block from Leader 1 (invalid link)
```
### Step 5: Check Results
Rank 0 prints:
```
=== Final Blockchain ===
Block 0: proposer=Genesis
Block 1: proposer=1, votes=2
=== Final Voting Results ===
Alice: 3 votes
Bob: 2 votes
```
Each node’s blockchain is saved in:
```
chain_rank_json/chain_rank_.json
```
---
## 7. requirements.txt Example
```txt
mpi4py
flask
streamlit
colorama
```
---
## 8. Advantages
■ Realistic hybrid design (Flask + MPI)
■ Distributed ledger replication
■ Fault-tolerant consensus model
■ Modular and extendable (easy to add UI, storage, or cryptography)
---
## 9. Future Enhancements
- Add **digital signatures** for secure vote verification
- Implement a **web dashboard** to visualize blockchain states
- Include **leader re-election** and fault recovery
- Migrate JSON storage to persistent database (SQLite, MongoDB)
- Add encryption for voter anonymity