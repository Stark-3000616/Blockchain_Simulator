# Created by Sayantan Biswas & Shamik Kumar De

import random
import numpy as np
import networkx as nx
import heapq
import sys
import uuid
import matplotlib.pyplot as plt

event_queue=[]

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
            if isinstance(txn, Coinbase):
                balance[txn.miner]+=50
            else:
                balance[txn.sender]-=txn.amount
                balance[txn.receiver]+=txn.amount

        print("Validation", balance)
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
        print("Vhggyhgy", balance)
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
        self.generate_block(current_time)
            

class Transaction:
    def __init__(self, peer_id1, peer_id2, amount):
        self.txn_id=uuid.uuid4()
        self.sender=peer_id1
        self.receiver=peer_id2
        self.amount=amount
        self.statement=f"{self.txn_id}:{self.sender} pays {self.receiver} {amount} coins"

class Coinbase:
    def __init__(self, peer_id):
        self.txn_id=uuid.uuid4()
        self.miner=peer_id
        self.statement=f"{self.txn_id}:{self.miner} mines 50 coins"

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

    def add_transaction(self, txn):
        self.transactions.append(txn)

class Blockchain:
    def __init__(self, num_peers):
        genesis=Block(0, 0, -1, 0, 0)
        genesis.balance=[50]*num_peers
        self.blocks={}
        self.blocks[0]=[genesis]
        self.last_block=genesis

    def add_block(self, block):
        if block.index not in self.blocks:
            self.blocks[block.index]=[block]
            self.last_block=block
        else:
            self.blocks[block.index].append(block)
            if block.index == self.last_block.index and block.mine_time<self.last_block.mine_time:
                self.last_block=block

                

class Event:

    def __init__(self, event_time, event_type, peer_id, data=None):
        self.event_time=event_time
        self.event_type=event_type
        self.peer_id=peer_id
        self.data=data

    def __lt__(self, other): #For Comparisons in Event Priority Queue
        return self.event_time < other.event_time

class Simulation:

    def __init__(self, num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration):
        self.peers= []
        self.graph= nx.Graph()
        self.num_peers=num_peers
        self.simulation_duration = simulation_duration
        self.slow_percentage = slow_percentage
        self.low_cpu_percentage = low_cpu_percentage

    def initialize_peers(self, speed_of_light_delay, mean_block_generation_time):
        slow=[0]*self.num_peers
        low_cpu=[0]*self.num_peers
        indices1 = random.sample(range(self.num_peers), int(self.num_peers * self.slow_percentage/ 100))
        indices2 = random.sample(range(self.num_peers), int(self.num_peers * self.low_cpu_percentage / 100))
        num_low_cpu=sum(low_cpu)
        num_high_cpu=self.num_peers-num_low_cpu
        hashing_power=1/(num_high_cpu*10 + num_low_cpu)
        for i in indices1:
            slow[i]=1
        for i in indices2:
            low_cpu[i]=1
        for i in range(0, self.num_peers):
            peer = Peer(i, slow[i], low_cpu[i], speed_of_light_delay, hashing_power, mean_block_generation_time)
            self.peers.append(peer)
        for peer in self.peers:
            peer.store_all_peers(range(0, len(self.peers)))

    def generate_random_topology(self):
        self.graph.add_nodes_from(self.peers)
        for peer in self.peers:
            num_connections = random.randint(3,6) - self.graph.degree[peer]
            num_connections = max(0, num_connections)
            peers_to_connect = random.sample([other_peer for other_peer in self.peers if other_peer != peer and peer not in other_peer.neighbours and len(other_peer.neighbours)<6], num_connections)
            self.graph.add_edges_from([(peer, connected_peer) for connected_peer in peers_to_connect])
            for connected_peer in peers_to_connect:
                peer.neighbours.append((connected_peer.peer_id, connected_peer.is_slow))

    def is_connected_graph(self):
        return nx.is_connected(self.graph)

    def recreate_graph(self):
        for peer in self.peers:
            peer.neighbours=[]
        self.generate_random_topology()

    def schedule_event(self, event_time, event_type, peer_id):
        event=Event(event_time, event_type, peer_id)
        heapq.heappush(event_queue, event)

    def initialize_events(self, simulation_duration, mean_transaction_time):
        event_time=0.0
        while event_time<= simulation_duration:
            peer = random.choice([node for node in self.peers])
            self.schedule_event(event_time, 'txn_generation', peer.peer_id)
            event_time+=np.random.exponential(mean_transaction_time)
        for peer in self.peers:
            self.schedule_event(0, 'blk_generation', peer.peer_id)
    
    def display_network(self):
        nx.draw(self.graph, node_color='skyblue', node_size=50, font_size=5)
        plt.savefig("graph.png")
        # for peer in self.peers:
        #     print(len(peer.transactions))

    def find_peer_by_id(self, id):
        for peer in self.peers:
            if peer.peer_id == id:
                return peer
        return None

    def run_simulation(self, simulation_duration):
        current_time=0.0
        while current_time <= self.simulation_duration and event_queue:
            current_event = heapq.heappop(event_queue)
            current_time = current_event.event_time

            peer = self.find_peer_by_id(current_event.peer_id)
            if current_event.event_type == 'txn_generation':
                peer.generate_transaction(current_time)
            elif current_event.event_type == 'txn_receive':
                peer.receive_transaction(current_event.data, current_time)
            elif current_event.event_type == 'blk_generation':
                peer.generate_block(current_time)
            elif current_event.event_type == 'blk_mining':
                peer.mine_block(current_time, current_event.data)
            elif current_event.event_type == 'blk_receive':
                peer.receive_block(current_time, current_event.data)
if __name__=="__main__":
    if(len(sys.argv)<7):
        print(f"Usage: {sys.argv[0]} <num_peers> <slow_%> <low_cpu_%> <mean_txn_time> <mean_blkgen_time> <duration>")
        sys.exit(1)

    num_peers = int(sys.argv[1])
    slow_percentage = int(sys.argv[2])
    low_cpu_percentage = int(sys.argv[3])
    mean_transaction_time = int(sys.argv[4])
    mean_block_generation_time = int(sys.argv[5])
    simulation_duration = int(sys.argv[6])

    # Creating an object of Simulation Class
    simulation= Simulation(num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration)

    speed_of_light_delay=random.uniform(0.01, 0.5)

    print("Creating peers...")
    simulation.initialize_peers(speed_of_light_delay, mean_block_generation_time)
    print("Creating network...")
    simulation.generate_random_topology()
    while not simulation.is_connected_graph():
        simulation.recreate_graph()
    print("Adding Events to the Queue...")
    simulation.initialize_events(simulation_duration, mean_transaction_time)
    # print(len(event_queue))
    print("Running Simulation...")
    simulation.run_simulation(simulation_duration)
    simulation.display_network()
    print("Simulation Completed")


# 1. Longest XChain selection on the basis of arrival time of the blocks
# 2. Transactions should not be repeated in a in the longest chain
