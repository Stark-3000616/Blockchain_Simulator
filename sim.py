# Created by Shamik Kumar De & Sayantan Biswas

import random
import numpy as np
import networkx as nx


class Peer:
    def __init__(self, peer_id, is_slow, is_low_cpu, mean_transaction_time):
        self.peer_id = peer_id
        self.is_slow = is_slow
        self.is_low_cpu = is_low_cpu
        self.balance = 100  # Initial balance for each peer
        self.mean_transaction_time = mean_transaction_time
        self.time_since_last_transaction = np.random.exponential(scale=self.mean_transaction_time)

    def generate_transaction(self, current_time):
        if current_time - self.time_since_last_transaction >= 0:
            transaction = self.create_transaction()
            self.time_since_last_transaction = current_time + np.random.exponential(scale=self.mean_transaction_time)
            return transaction
        else:
            return None

    def create_transaction(self):
        recipient_id = random.choice([peer.peer_id for peer in Simulation.peers if peer.peer_id != self.peer_id])
        amount = random.randint(1, self.balance)
        transaction = f"TxnID: {self.peer_id} pays {recipient_id} {amount} coins"
        self.balance -= amount
        return transaction

    def receive_transaction(self, transaction):
        # Implement logic for receiving and forwarding transactions
        pass

    def receive_block(self, block):
        # Implement logic for receiving and validating blocks
        pass

    def mine_block(self):
        # Implement PoW mining logic
        pass




class Blockchain:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        # Implement logic to add a block to the blockchain
        pass

    def validate_block(self, block):
        # Implement logic to validate transactions in a block
        pass

    def resolve_forks(self):
        # Implement logic to resolve forks and find the longest chain
        pass





class Simulation:
    peers = []

    def __init__(self, num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration):
        
        self.blockchain = Blockchain()
        self.mean_transaction_time = mean_transaction_time
        self.graph = nx.Graph()
        self.simulation_duration = simulation_duration

    def initialize_peers(self):
        for peer_id in range(1, num_peers + 1):
            is_slow = random.random() < (slow_percentage / 100)
            is_low_cpu = random.random() < (low_cpu_percentage / 100)
            peer = Peer(peer_id, is_slow, is_low_cpu, self.mean_transaction_time)
            Simulation.peers.append(peer)

    def generate_random_topology(self):
        self.graph = nx.Graph()

        # Add nodes to the graph
        self.graph.add_nodes_from(Simulation.peers)

        for peer in Simulation.peers:
            # Determine the number of connections for the current peer (between 3 and 6)
            num_connections = random.randint(3, 6)

            # Ensure the peer has at least 1 connection
            num_connections = min(num_connections, len(Simulation.peers) - 1)

            # Select random peers to connect to
            peers_to_connect = random.sample([other_peer for other_peer in Simulation.peers if other_peer != peer], num_connections)

            # Add edges to the graph
            self.graph.add_edges_from([(peer, connected_peer) for connected_peer in peers_to_connect])


    def is_connected_graph(self):
        return nx.is_connected(self.graph)

    def recreate_graph(self):
        self.generate_random_topology()
        while not self.is_connected_graph():
            self.generate_random_topology()

    def simulate_transaction_generation(self, current_time):
        transactions = []
        for peer in Simulation.peers:
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

    current_time = 0
    while current_time < simulation.simulation_duration:
        transactions = simulation.simulate_transaction_generation(current_time)
        # Process transactions and perform other simulation steps
        current_time += 1
    # Other simulation steps...
