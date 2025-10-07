# ui.py
import streamlit as st
import json
import os
from datetime import datetime

VOTES_FILE = "pending_votes.json"
CANDIDATES = ["Alice", "Bob", "Carol"]

# Initialize file if not exists
if not os.path.exists(VOTES_FILE):
    with open(VOTES_FILE, "w") as f:
        json.dump([], f)

st.title("🗳 Secure Distributed Voting System")
st.subheader("Cast your vote below")

voter_id = st.text_input("Enter Voter ID", placeholder="e.g. V001")
choice = st.radio("Select your candidate", CANDIDATES)

if st.button("Submit Vote"):
    if voter_id.strip() == "":
        st.warning("⚠️ Please enter your Voter ID.")
    else:
        # Save vote locally
        with open(VOTES_FILE, "r") as f:
            votes = json.load(f)

        votes.append({
            "voter": voter_id,
            "choice": choice,
            "timestamp": str(datetime.now())
        })

        with open(VOTES_FILE, "w") as f:
            json.dump(votes, f, indent=4)

        st.success(f"✅ Vote for {choice} submitted successfully!")
