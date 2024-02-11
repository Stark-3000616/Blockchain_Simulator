import uuid
from transaction import Coinbase

class Block:
    def __init__(self, prev_hash, mine_time, miner_id, index, prev_blk_id):
        self.blk_id=uuid.uuid4()
        self.prev_hash=prev_hash
        self.mine_time=mine_time
        self.index=index
        self.transactions=[]
        coinbase=Coinbase(miner_id)
        self.transactions.append(coinbase)
        self.balance=[]
        self.prev_blk_id=prev_blk_id
        self.miner_id = miner_id  # Added miner_id attribute

    def add_transaction(self, txn):
        self.transactions.append(txn)