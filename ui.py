# ui.py — Streamlit frontend for MPI-based Blockchain Voting System
import streamlit as st
import requests
import json
from datetime import datetime

# --- Node Config ---
NODES = [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:5001",
    "http://127.0.0.1:5002",
    "http://127.0.0.1:5003",
]

CANDIDATES = ["Alice", "Bob", "Carol"]

st.set_page_config(page_title="Blockchain Voting System", page_icon="🗳", layout="centered")

st.title("🗳 Secure Distributed Voting System")
st.subheader("Cast your vote on the live blockchain network")

# --- Select Node ---
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
            response = requests.post(f"{selected_node}/vote", json=vote)
            if response.status_code == 200:
                st.success(f"✅ Vote for {choice} submitted successfully to {selected_node}")
            else:
                st.error(f"❌ Failed to submit vote: {response.text}")
        except requests.exceptions.RequestException:
            st.error(f"🚫 Could not connect to {selected_node}. Make sure the node is running.")

st.divider()
st.subheader("🌐 View Blockchain Data")

if st.button("Fetch Blockchain Data"):
    try:
        chains = []
        for node in NODES:
            try:
                resp = requests.get(f"{node}/chain", timeout=2)
                if resp.status_code == 200:
                    chain_data = resp.json()
                    chains.append((node, len(chain_data)))
            except:
                continue
        if chains:
            st.success("✅ Connected nodes:")
            for node, blocks in chains:
                st.write(f"- {node} → {blocks} blocks")
        else:
            st.warning("⚠️ No nodes reachable right now.")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
