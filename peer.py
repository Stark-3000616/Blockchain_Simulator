import random
import sys
import numpy as np
import heapq


from blockchain import Blockchain
from transaction import Transaction
from event import Event
from block import Block
from transaction import Coinbase
from sim import event_queue

class Peer:

    def __init__(self, peer_id, is_slow, is_low_cpu, speed_of_light_delay, hashing_power, mean_block_generation_time):
        self.peer_id=peer_id
        self.is_slow=is_slow
        self.is_low_cpu=is_low_cpu
        self.all_peers = []
        self.neighbours = []
        self.transactions = []
        self.used_txns = []
        self.speed_of_light_delay=speed_of_light_delay
        self.blockchain=None
        self.hashing_power=hashing_power
        if not is_low_cpu:
            self.hashing_power*=10
        self.mean_block_generation_time=mean_block_generation_time
    
    def store_all_peers(self, all_peer_ids):
        self.all_peers=all_peer_ids
        self.blockchain=Blockchain(len(self.all_peers))

    def generate_transaction(self, current_time):
        receiver_id=random.choice([peer_id for peer_id in self.all_peers if peer_id != self.peer_id])
        amount = random.randint(0, 5)
        txn=Transaction(self.peer_id, receiver_id, amount)
        self.receive_transaction(txn, current_time)
    
    def find_transactions(self, txn):
        for transaction in self.transactions:
            if(transaction.txn_id == txn.txn_id):
                return True
        return False

    def receive_transaction(self, txn, current_time):
        if self.find_transactions(txn):
            return
        self.transactions.append(txn)
        m = sys.getsizeof(txn)*8
        for neighbour in self.neighbours:
            c=0
            if not self.is_slow and not neighbour[1]:
                c=100000000
            else:
                c=5000000
            d = np.random.exponential(96000/c)
            time_delta = self.speed_of_light_delay + (m/c) + d
            new_event= Event(current_time+time_delta, 'txn_receive', neighbour[0], txn)
            heapq.heappush(event_queue, new_event)
    
    def generate_block(self, current_time):
        prev_hash=hash(self.blockchain.last_block)
        index=self.blockchain.last_block.index+1
        new_block=Block(prev_hash, current_time, self.peer_id, index, self.blockchain.last_block.blk_id)
        
        i=0
        while i < len(self.transactions) and sys.getsizeof(new_block)<1000000:
            new_block.add_transaction(self.transactions[i])
            i+=1
        Tk = np.random.exponential(self.mean_block_generation_time/self.hashing_power)
        mining = Event(current_time+Tk, 'blk_mining', self.peer_id, new_block)
        heapq.heappush(event_queue, mining)

    def mine_block(self, current_time, data):
        block = data
        if block.prev_blk_id!=self.blockchain.last_block.blk_id:
            self.generate_block(current_time)
        else:
            self.receive_block(current_time, block)

    def validate_block(self, block):
        if block.index-1 in self.blockchain.blocks:
            prev_block=None
            for blk in self.blockchain.blocks[block.index-1]:
                if blk.blk_id == block.prev_blk_id:
                    prev_block=blk
                    if hash(blk) != block.prev_hash:
                        return None
            if not prev_block:
                return None
        else:
            return None
        balance=prev_block.balance[:]
        for txn in block.transactions:
            if txn in self.used_txns:
                return None
            if isinstance(txn, Coinbase):
                balance[txn.miner]+=50
            else:
                balance[txn.sender]-=txn.amount
                balance[txn.receiver]+=txn.amount
        for i in balance:
            if i < 0:
                return None
        
        return balance

    def receive_block(self, current_time, block):
        if block.index in self.blockchain.blocks:
            for blk in self.blockchain.blocks[block.index]:
                if blk.blk_id == block.blk_id:
                    return
        balance=self.validate_block(block)
        if not balance:
            return
        block.balance=balance
        self.blockchain.add_block(block)
        for txn in block.transactions:
            if txn in self.transactions:
                self.transactions.remove(txn)
            self.used_txns.append(txn)
        m = sys.getsizeof(block)*8
        for neighbour in self.neighbours:
            c=0
            if not self.is_slow and not neighbour[1]:
                c=100000000
            else:
                c=5000000
            d = np.random.exponential(96000/c)
            time_delta = self.speed_of_light_delay + (m/c) + d
            new_event=Event(current_time+time_delta, 'blk_receive', neighbour[0], block)
            heapq.heappush(event_queue, new_event)
        self.generate_block(current_time)
        