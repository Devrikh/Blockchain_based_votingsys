import hashlib
import datetime

class Block:
    def __init__(self, index, prev_hash, votes, proposer, timestamp=None):
        self.index = index
        self.prev_hash = prev_hash
        self.votes = votes  # list of dicts: {"voter": "V0", "choice": "Alice"}
        self.proposer = proposer
        self.timestamp = timestamp or str(datetime.datetime.now())
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        vote_str = str(self.votes)
        block_str = f"{self.index}{self.prev_hash}{vote_str}{self.proposer}{self.timestamp}"
        return hashlib.sha256(block_str.encode()).hexdigest()

    def __repr__(self):
        return f"<Block {self.index} proposer={self.proposer} votes={len(self.votes)}>"

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        # Use fixed timestamp and proposer so every node starts identical
        return Block(
            index=0,
            prev_hash="0",
            votes=[],
            proposer="Genesis",
            timestamp="2025-01-01 00:00:00"
        )

    def add_block(self, block):
        self.chain.append(block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            curr = self.chain[i]
            prev = self.chain[i - 1]
            if curr.prev_hash != prev.hash:
                return False
            if curr.hash != curr.calculate_hash():
                return False
        return True

    def count_votes(self):
        results = {}
        for block in self.chain[1:]:  # skip genesis block
            for vote in block.votes:
                choice = vote["choice"]
                results[choice] = results.get(choice, 0) + 1
        return results

    def print_results(self):
        results = self.count_votes()
        print("\n=== Final Voting Results ===")
        for candidate, count in results.items():
            print(f"{candidate}: {count} vote(s)")
