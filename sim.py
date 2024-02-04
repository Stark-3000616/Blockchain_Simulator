# Created by Shamik Kumar De & Sayantan Biswas
# Import necessary libraries
import random
import numpy as np
import networkx as nx
import heapq  # For heapq-based priority queue

class Event:
    def __init__(self, time, event_type, peer, data=None):
        self.time = time
        self.event_type = event_type
        self.peer = peer
        self.data = data  # Additional data associated with the event

    def __lt__(self, other):
        # Comparison method for the priority queue
        return self.time < other.time

class Peer:
    def __init__(self, peer_id, is_slow, is_low_cpu, mean_transaction_time):
        self.peer_id = peer_id
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.balance = 100  # Initial balance for each peer
        self.mean_transaction_time = mean_transaction_time
        self.time_since_last_transaction = np.random.exponential(scale=self.mean_transaction_time)
        self.all_peers = []
        self.neighbours = []
        self.blockchain = Blockchain()

    def generate_transaction(self, current_time):
        if current_time - self.time_since_last_transaction >= 0:
            transaction = self.create_transaction()
            self.time_since_last_transaction = current_time + np.random.exponential(scale=self.mean_transaction_time)
            return transaction
        else:
            return None

    def create_transaction(self):
        recipient_id = random.choice([peer.peer_id for peer in self.all_peers if peer.peer_id != self.peer_id])
        amount = random.randint(1, self.balance)
        transaction = f"TxnID: {self.peer_id} pays {recipient_id} {amount} coins"
        self.balance -= amount
        return transaction

    def get_all_peers(self, peers):
        self.all_peers = peers

    def simulate_latency(self, destination_peer):
        speed_of_light_delay = random.uniform(10e-3, 500e-3)
        link_speed = 100e6 if not (self.is_slow or destination_peer.is_slow) else 5e6
        queuing_delay = np.random.exponential(scale=96e3 / link_speed)
        message_length = 1024 * 8  # Assuming message size is 1 KB

        total_latency = speed_of_light_delay + (message_length / link_speed) + queuing_delay
        return total_latency

    def send_block(self, destination_peer, block):
        latency = self.simulate_latency(destination_peer)
        event_time = current_time + latency
        simulation.schedule_event(event_time, 'receive_block', destination_peer, data={'block': block})

    def mine_block(self):
        # Simulate PoW mining logic
        # ...

        # Assuming new_block is the mined block
        new_block = Block()  # Replace with actual block creation logic
        self.blockchain.add_block(new_block)

        # Schedule events related to block creation (e.g., future block creation, block propagation)
        for neighbor in self.neighbours:
            self.send_block(neighbor, new_block)

class Blockchain:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        # Implement logic to add a block to the blockchain
        self.blocks.append(block)

class Block:
    def __init__(self):
        # Implement block attributes and structure as needed
        pass

class Simulation:

    def __init__(self, num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration):
        self.peers = []
        self.graph = nx.Graph()
        self.simulation_duration = simulation_duration
        self.event_queue = []  # Priority queue for events

    def schedule_event(self, time, event_type, peer, data=None):
        event = Event(time, event_type, peer, data)
        heapq.heappush(self.event_queue, event)

    def initialize_peers(self):
        for peer_id in range(1, num_peers + 1):
            is_slow = random.random() < (slow_percentage / 100)
            is_low_cpu = random.random() < (low_cpu_percentage / 100)
            peer = Peer(peer_id, is_slow, is_low_cpu, mean_transaction_time)
            self.peers.append(peer)
        peer_id=[peer.peer_id for peer in self.peers]
        for peer in self.peers:
            peer.get_all_peers(peer_id)
            # peer.neighbours = random.sample([neighbour for neighbour in self.peers if neighbour != peer], random.randint(3, 6))

    def generate_random_topology(self):
        self.graph = nx.Graph()

        # Add nodes to the graph
        self.graph.add_nodes_from(self.peers)

        for peer in self.peers:
            # Determine the number of connections for the current peer (between 3 and 6)
            num_connections = random.randint(3, 6)

            # Ensure the peer has at least 1 connection
            num_connections = min(num_connections, len(self.peers) - 1)

            # Select random peers to connect to
            peers_to_connect = random.sample([other_peer for other_peer in self.peers if other_peer != peer], num_connections)

            # Add edges to the graph
            self.graph.add_edges_from([(peer, connected_peer) for connected_peer in peers_to_connect])

    def is_connected_graph(self):
        return nx.is_connected(self.graph)

    def recreate_graph(self):
        self.generate_random_topology()
        while not self.is_connected_graph():
            self.generate_random_topology()

    def run_simulation(self):
        current_time = 0
        while current_time < self.simulation_duration and self.event_queue:
            current_event = heapq.heappop(self.event_queue)
            current_time = current_event.time

            if current_event.event_type == 'transaction_generation':
                transactions = self.simulate_transaction_generation(current_time)
                # Schedule future events related to transactions (e.g., block creation)
                for transaction in transactions:
                    self.schedule_event(current_time, 'mine_block', current_event.peer, data={'transaction': transaction})

            elif current_event.event_type == 'mine_block':
                current_event.peer.mine_block()

            elif current_event.event_type == 'receive_block':
                block = current_event.data['block']
                current_event.peer.blockchain.add_block(block)

    def simulate_transaction_generation(self, current_time):
        transactions = []
        for peer in self.peers:
            transaction = peer.generate_transaction(current_time)
            if transaction:
                transactions.append(transaction)
        return transactions

if __name__ == "__main__":
    num_peers = 100
    slow_percentage = 20
    low_cpu_percentage = 30
    mean_transaction_time = 10
    simulation_duration = 1000  # Set your simulation duration

    simulation = Simulation(num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration)

    simulation.initialize_peers()
    simulation.generate_random_topology()
    while not simulation.is_connected_graph():
        simulation.recreate_graph()

    # Initial events (e.g., transaction generation)
    event_time=0
    while event_time <= simulation_duration:
        peer = random.choice([node for node in simulation.peers])
        simulation.schedule_event(event_time, 'transaction_generation', peer)
        event_time+=np.random.exponential(mean_transaction_time)

    simulation.run_simulation()