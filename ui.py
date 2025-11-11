# ui.py — Streamlit frontend for MPI-based Blockchain Voting System
import streamlit as st
import requests
import json
from datetime import datetime

# --- Node Configuration ---
NODES = [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

CANDIDATES = ["Alice", "Bob", "Carol"]

st.set_page_config(page_title="Blockchain Voting System", page_icon="🗳", layout="centered")
st.title("🗳 Secure Distributed Voting System")
st.subheader("Cast your vote and view real-time blockchain status")

# --- Node Selection for Vote Submission ---
selected_node = st.selectbox("Select a node to submit your vote", NODES)

# --- Voting Section ---
voter_id = st.text_input("Enter Voter ID", placeholder="e.g. V001")
choice = st.radio("Select your candidate", CANDIDATES)

if st.button("Submit Vote"):
    if not voter_id.strip():
        st.warning("⚠️ Please enter your Voter ID.")
    else:
        vote = {
            "voter": voter_id,
            "choice": choice,
            "timestamp": str(datetime.now())
        }
        try:
            resp = requests.post(f"{selected_node}/vote", json=vote, timeout=3)
            if resp.status_code == 200:
                st.success(f"✅ Vote for {choice} submitted successfully to {selected_node}")
            else:
                st.error(f"❌ Failed to submit vote: {resp.text}")
        except requests.exceptions.RequestException:
            st.error(f"🚫 Could not connect to {selected_node}. Make sure the node is running.")

st.divider()

# --- Live Blockchain Status ---
st.subheader("🌐 Live Blockchain Status")
refresh = st.button("Refresh Blockchain Data")

if refresh:
    chains_info = []
    results_info = []

    for node in NODES:
        # --- Fetch Chain Info ---
        try:
            chain_resp = requests.get(f"{node}/chain", timeout=2)
            if chain_resp.status_code == 200:
                chain_data = chain_resp.json()
                chains_info.append((node, len(chain_data)))
        except:
            chains_info.append((node, "❌ Not reachable"))

        # --- Fetch Voting Results ---
        try:
            res_resp = requests.get(f"{node}/results", timeout=2)
            if res_resp.status_code == 200:
                res_data = res_resp.json()
                results_info.append((node, res_data))
        except:
            results_info.append((node, {"tally": "❌ Not reachable", "votes_total": 0}))

    # --- Display Node Status ---
    st.markdown("**Node Blockchain Summary:**")
    for node, blocks in chains_info:
        st.write(f"- {node} → {blocks} blocks")

    st.markdown("**Voting Results per Node:**")
    for node, data in results_info:
        st.write(f"**Node {node}**")
        if isinstance(data["tally"], dict):
            for candidate, count in data["tally"].items():
                st.write(f"  - {candidate}: {count} vote(s)")
            st.write(f"  Total votes: {data['votes_total']}")
            st.write(f"  Latest block index: {data['latest_block']['index'] if data['latest_block'] else 'N/A'}")
        else:
            st.write(f"  {data['tally']}")

st.divider()
st.caption("Data fetched live from all running nodes. Refresh to see updates.")
