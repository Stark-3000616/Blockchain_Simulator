import random
import sys
import numpy as np
import heapq


from blockchain import Blockchain
from transaction import Transaction
from event import Event
from block import Block
from transaction import Coinbase

event_queue=[]

class Peer:

    def __init__(self, peer_id, is_slow, is_low_cpu, speed_of_light_delay, hashing_power, mean_block_generation_time, num_peers, selfish_miner=False):
        self.peer_id=peer_id
        self.is_slow=is_slow
        self.is_low_cpu=is_low_cpu
        self.all_peers = range(num_peers)
        self.neighbours = []
        self.transactions = []
        self.used_txns = []
        self.speed_of_light_delay=speed_of_light_delay
        self.blockchain=Blockchain()
        self.hashing_power=hashing_power
        if (not is_low_cpu) and (not selfish_miner):
            self.hashing_power*=10
        self.mean_block_generation_time=mean_block_generation_time
        self.file_writing_lines=['block_index,miner_id,block_id,num_of_txns,mine_time,arrival_time']

        self.selfish_miner=selfish_miner
        self.private_chain=Blockchain()
    
    #Function to handle transaction generation event
    def generate_transaction(self, current_time):
        receiver_id=random.choice([peer_id for peer_id in self.all_peers if peer_id != self.peer_id])
        amount = random.randint(0, 5)
        txn=Transaction(self.peer_id, receiver_id, amount)
        #calling receive transaction to it self
        self.receive_transaction(txn, current_time)
    
    #Function to find transaction in the stored transactions
    def find_transactions(self, txn):
        for transaction in self.transactions:
            if(transaction.txn_id == txn.txn_id):
                return True
        return False

    #Function to handle receive transaction event
    def receive_transaction(self, txn, current_time):
        #To prevent transmitting same transactions
        #Implementation of Transaction Generation(Part 2)
        #Check to facilitate loopless transaction forwarding
        if self.find_transactions(txn):
            return
        self.transactions.append(txn)
        if self.selfish_miner:
            return
        #Simulating Latencies for transaction propagation
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
    
    #Function to start generating block by a node
    def generate_block(self, current_time):
        prev_hash=hash(self.blockchain.last_block)
        index=self.blockchain.last_block.index+1
        if self.selfish_miner:
            prev_hash=hash(self.private_chain.last_block)
            index=self.private_chain.last_block.index+1
        new_block=Block(prev_hash, self.peer_id, index, self.blockchain.last_block.blk_id)
        
        i=0
        while i < len(self.transactions) and sys.getsizeof(new_block)<1000000:
            new_block.add_transaction(self.transactions[i])
            i+=1
        print(self.mean_block_generation_time, self.hashing_power, self.mean_block_generation_time/self.hashing_power)
        Tk = np.random.exponential(self.mean_block_generation_time/self.hashing_power)
        mining = Event(current_time+Tk, 'blk_mining', self.peer_id, new_block)
        heapq.heappush(event_queue, mining)

    #Function to handle Block Mining event
    def mine_block(self, current_time, data):
        block = data
        block.mine_time=current_time
        if block.prev_blk_id!=self.private_chain.last_block.blk_id:
            self.generate_block(current_time)
        else:
            self.receive_block(current_time, block)

    #Function to validate a block and return the balance after making all transactions (for honest miners only)
    def validate_block(self, block):
        if block.index-1 in self.private_chain.blocks:
            prev_block=None
            for blk in self.private_chain.blocks[block.index-1]:
                if blk.blk_id == block.prev_blk_id:
                    prev_block=blk
                    if hash(blk) != block.prev_hash:
                        return None
            if not prev_block:
                return None
        #To invalidate receiving of future blocks
        else:
            return None
        #Validating Transactions
        balance=prev_block.balance[:]
        for txn in block.transactions:
            if isinstance(txn, Coinbase):
                balance[txn.miner]+=50
            else:
                balance[txn.sender]-=txn.amount
                balance[txn.receiver]+=txn.amount
        for i in balance:
            if i < 0:
                return None
        
        return balance

    #Function handles receive block event only for honest miners
    def receive_block(self, current_time, block):
        if self.selfish_miner:
            self.selfish_miner_receive_block(current_time, block)
            return
        if block.miner_id!=-1:
            #Check to facilitate loopless block forwarding
            if block.index in self.private_chain.blocks:
                for blk in self.private_chain.blocks[block.index]:
                    if blk.blk_id == block.blk_id:
                        return
            balance=self.validate_block(block)
            if not balance:
                return
            block.balance=balance
            self.blockchain.add_block(block)
            self.private_chain.add_block(block)
            for txn in block.transactions:
                if txn in self.transactions:
                    self.transactions.remove(txn)
                self.used_txns.append(txn)
        elif len(self.blockchain.blocks[0])>0:
            return
        else:
            self.blockchain.add_genesis(block)
            self.private_chain.add_genesis(block)
        self.add_to_file_writing(block.index, block.miner_id, block.blk_id, len(block.transactions), block.mine_time, current_time)
       
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
    
    #Function for storing logs on each block receive
    def add_to_file_writing(self,block_index,miner_id,block_id,num_of_txns,mine_time,arrival_time):
        self.file_writing_lines.append(f'\n{block_index},{miner_id},{block_id},{num_of_txns},{mine_time},{arrival_time}') 

    #Selfish Miner Receive Block
    def selfish_miner_receive_block(self, current_time, block):
        if block.miner_id == -1:
            if len(self.private_chain.blocks[0])>0:
                return
            else:
                self.blockchain.add_genesis(block)
                self.private_chain.add_genesis(block)
                self.generate_block(current_time)
        else:
            if block.index in self.private_chain.blocks:
                for blk in self.private_chain.blocks[block.index]:
                    if blk.blk_id == block.blk_id:
                        return
            balance=self.validate_block(block)
            if not balance:
                return
            block.balance=balance
            for txn in block.transactions:
                if txn in self.transactions:
                    self.transactions.remove(txn)
                self.used_txns.append(txn)
            if block.miner_id == self.peer_id:
                self.private_chain.add_block(block)
                self.generate_block(current_time)
            elif self.blockchain.last_block.index >= self.private_chain.last_block.index:
                self.private_chain.add_block(block)
                self.blockchain.add_block(block)
                #self.generate_block(current_time)
            elif self.blockchain.last_block.index == self.private_chain.last_block.index-1:
                self.broadcast_block(current_time, self.private_chain.last_block)
                self.private_chain.add_block(block)
                self.blockchain.add_block(block)
            elif self.blockchain.last_block.index == self.private_chain.last_block.index-2:
                self.broadcast_block(current_time, self.private_chain.find_block_by_id(self.private_chain.last_block.prev_blk_id))
                self.broadcast_block(current_time, self.private_chain.last_block)
                self.private_chain.add_block(block)
                self.blockchain.add_block(block)
            else:
                parallelblock=None
                for blk in self.private_chain.block[block.index]:
                    if blk.miner_id == self.peer_id:
                        parallelblock=blk
                        break
                self.broadcast_block(current_time, parallelblock)
                self.private_chain.add_block(block)
                self.blockchain.add_block(block)
            
    def broadcast_block(self, current_time, block):
        self.blockchain.add_block(block)
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


        
        
#Two peer selfish miners
# existing code 