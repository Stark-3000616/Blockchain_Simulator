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

    def __init__(self, peer_id, is_slow, is_low_cpu, speed_of_light_delay):
        self.peer_id=peer_id
        self.is_slow=is_slow
        self.is_low_cpu=is_low_cpu
        self.balance=100
        self.all_peers = []
        self.neighbours = []
        self.transactions = []
        self.speed_of_light_delay=speed_of_light_delay
    
    def store_all_peers(self, all_peer_ids):
        self.all_peers=all_peer_ids

    def generate_transaction(self, current_time):
        receiver_id=random.choice([peer_id for peer_id in self.all_peers if peer_id != self.peer_id])
        amount = random.randint(0, self.balance)
        txn=Transaction(self.peer_id, receiver_id, amount)
        self.balance-=amount
        self.receive_transaction(txn, current_time)
    
    def find_transactions(self, txn):
        for transaction in self.transactions:
            if(transaction.txn_id == txn.txn_id):
                return True
        return False

    def receive_transaction(self, txn, current_time):
        if self.find_transactions(txn):
            return
        if txn.receiver == self.peer_id:
            self.balance+=txn.amount
        self.transactions.append(txn)
        m = sys.getsizeof(txn)*8
        for neighbour in self.neighbours:
            c=0
            if not self.is_slow and not neighbour[1]:
                c=5000000
            else:
                c=100000000
            d = np.random.exponential(96000/c)
            time_delta = self.speed_of_light_delay + (m/c) + d
            new_event= Event(current_time+time_delta, 'txn_receive', neighbour[0], txn)
            heapq.heappush(event_queue, new_event)

class Transaction:
    def __init__(self, peer_id1, peer_id2, amount):
        self.txn_id=uuid.uuid4()
        self.sender=peer_id1
        self.receiver=peer_id2
        self.amount=amount
        self.statement=f"{self.txn_id}:{self.sender} pays {self.receiver} {amount} coins"

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

    def initialize_peers(self, speed_of_light_delay):
        all_peer_ids=[]
        for i in range(0, self.num_peers):
            is_slow = random.random() < (self.slow_percentage / 100)
            is_low_cpu = random.random() < (self.low_cpu_percentage / 100)
            peer_id = uuid.uuid4()
            all_peer_ids.append(peer_id)
            peer = Peer(peer_id, is_slow, is_low_cpu, speed_of_light_delay)
            self.peers.append(peer)
        for peer in self.peers:
            peer.store_all_peers(all_peer_ids)

    def generate_random_topology(self):
        self.graph.add_nodes_from(self.peers)
        for peer in self.peers:
            num_connections = random.randint(3,6) - self.graph.degree[peer]
            num_connections = max(0, num_connections)
            peers_to_connect = random.sample([other_peer for other_peer in self.peers if other_peer != peer and other_peer not in peer.neighbours], num_connections)
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

if __name__=="__main__":
    if(len(sys.argv)<6):
        print(f"Usage: {sys.argv[0]} <num_peers> <slow_%> <low_cpu_%> <mean_txn_time> <duration>")
        sys.exit(1)

    num_peers = int(sys.argv[1])
    slow_percentage = int(sys.argv[2])
    low_cpu_percentage = int(sys.argv[3])
    mean_transaction_time = int(sys.argv[4])
    simulation_duration = int(sys.argv[5])

    # Creating an object of Simulation Class
    simulation= Simulation(num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration)

    speed_of_light_delay=random.uniform(0.01, 0.5)

    print("Creating peers...")
    simulation.initialize_peers(speed_of_light_delay)
    print("Creating network...")
    simulation.generate_random_topology()
    while not simulation.is_connected_graph():
        recreate_graph()
    print("Adding Events to the Queue...")
    simulation.initialize_events(simulation_duration, mean_transaction_time)
    ## print(len(event_queue))
    print("Running Simulation...")
    simulation.run_simulation(simulation_duration)
    simulation.display_network()
