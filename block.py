import shortuuid
from transaction import Coinbase

#Structure of each block
class Block:
    def __init__(self, prev_hash, miner_id, index, prev_blk_id):
        self.blk_id=shortuuid.uuid()
        self.prev_hash=prev_hash
        self.mine_time=0
        self.index=index
        self.transactions=[]
        coinbase=Coinbase(miner_id)
        self.transactions.append(coinbase)
        self.balance=[]
        self.prev_blk_id=prev_blk_id
        self.miner_id = miner_id 
    #Function for adding transactions to the block
    def add_transaction(self, txn):
        self.transactions.append(txn)