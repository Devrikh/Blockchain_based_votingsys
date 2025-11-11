# 🗳️ Blockchain-Based Voting System (Flask + MPI)

## 1. Project Overview
**Project Name:** Blockchain-Based Voting System  
**Objective:** Implement a **secure, distributed voting platform** combining **Flask (frontend API)** and **MPI (backend consensus)**.  
Each node:
- Runs a **Flask server** for receiving votes.
- Participates in the **blockchain network** using MPI for synchronization and **approval-based consensus**.

---

## 2. Technology Stack

| Layer     | Technology      | Purpose                                     |
|----------|-----------------|----------------------------------------------|
| Frontend | Flask (Python)  | Vote submission API                          |
| Backend  | MPI (mpi4py)    | Blockchain synchronization and consensus     |
| Data     | Python + JSON   | Blockchain storage and verification          |
| Optional | Streamlit       | Web UI for voting                            |
| Optional | Colorama        | CLI color formatting                         |

---

## 3. System Architecture

### Components:
1. **`ui.py` (Frontend)**
   - Web interface for casting votes.
   - Sends votes to selected node via Flask API.
2. **`node.py` (Backend Node)**
   - Each MPI process launches a Flask app.
   - Collects votes in `pending_votes`.
   - Uses MPI two-phase approval to synchronize blockchain across nodes.
3. **`blockchain.py`**
   - Defines `Block` and `Blockchain` classes.
   - Handles hashing, linking, and validation logic.
4. **`requirements.txt`**
   - Lists required dependencies.

---

## 4. System Flow

### Step 1. Vote Collection (Frontend → Flask)
Users submit votes via Streamlit UI:
```bash
streamlit run ui.py
```
Votes are sent to the selected node's `/vote` endpoint.

### Step 2. Block Proposal (Leader Node via MPI)
- Current leader collects `pending_votes` and proposes a new block.
- Block includes `index`, `prev_hash`, `votes`, `proposer`, `timestamp`, and `hash`.

### Step 3. Approval-Based Consensus
- All nodes verify:
  - `prev_hash` continuity
  - Hash integrity (`recomputed_hash` == stored hash)
- Nodes send **YES/NO approvals** to leader.
- Leader commits the block **only if majority approval** is reached.
- Commit/abort decision is broadcast to all nodes for consistent blockchain updates.

### Step 4. Synchronization
- All nodes maintain identical blockchain copies after committed proposals.

### Step 5. Results Display
- `/results` endpoint provides:
  - Vote tally
  - Latest block info
  - Total votes and blocks
- Each node saves blockchain in `chain_rank_json/chain_rank_<rank>.json`.

---

## 5. Project Structure
```
Blockchain_Voting_System/
│
├─ blockchain.py           # Blockchain and Block logic
├─ node.py                 # MPI + Flask backend
├─ ui.py                   # Streamlit frontend
├─ chain_rank_json/        # JSON blockchain outputs per node
│   ├─ chain_rank_0.json
│   ├─ chain_rank_1.json
│   └─ ...
├─ requirements.txt        # Python dependencies
└─ README.md               # Documentation
```

---

## 6. How to Run

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the MPI Nodes
Start N nodes (example: 3 nodes):
```bash
mpiexec -n 3 python node.py
```
Each node’s Flask server runs on:
```
Node 0 → localhost:5000
Node 1 → localhost:5001
Node 2 → localhost:5002
```

### Step 3: Run the UI
```bash
streamlit run ui.py
```
Submit votes through the web interface.

### Step 4: Observe Logs
Example output:
```
[Leader 1] Proposal broadcasted — awaiting approvals...
[Node 0] Sent YES to Leader 1
[Node 2] Sent YES to Leader 1
[Leader 1] Block committed locally as #1
[Node 0] Added Block #1 from Leader 1
[Node 2] Added Block #1 from Leader 1
```

### Step 5: Check Results
Query `/results` endpoint:
```bash
curl http://localhost:5000/results
```
Output:
```json
{
  "node": 0,
  "blocks": 2,
  "votes_total": 3,
  "tally": {"Alice": 2, "Bob": 1},
  "latest_block": {...}
}
```

Check JSON snapshots:
```
chain_rank_json/chain_rank_0.json
```

---

## 7. `requirements.txt` Example
```txt
mpi4py
flask
streamlit
colorama
```

---

## 8. Advantages
- Distributed ledger with approval-based commit
- Fault-tolerant consensus
- Modular and extendable design
- Real-time voting via web UI

---

## 9. Future Enhancements
- Digital signatures for secure vote verification
- Web dashboard to visualize blockchain states
- Leader re-election & fault recovery
- Persistent storage (DB instead of JSON)
- Encryption for voter anonymity

