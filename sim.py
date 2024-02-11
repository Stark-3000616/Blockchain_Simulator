# Created by Sayantan Biswas & Shamik Kumar De

import random
import numpy as np
import networkx as nx
import heapq
import sys
import matplotlib.pyplot as plt

from event import Event
from peer import Peer

event_queue=[]

class Simulation:

    def __init__(self, num_peers, slow_percentage, low_cpu_percentage, mean_transaction_time, simulation_duration):
        self.peers= []
        self.graph= nx.Graph()
        self.num_peers=num_peers
        self.simulation_duration = simulation_duration
        self.slow_percentage = slow_percentage
        self.low_cpu_percentage = low_cpu_percentage
        self.blockchain_data = {}

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
                peer_id = current_event.peer_id
                block = current_event.data
                if peer_id not in self.blockchain_data:
                    self.blockchain_data[peer_id] = []
                self.blockchain_data[peer_id].append(block)
    
    def visualize_blockchain(self, blockchain):
        G = nx.DiGraph()

        for index, blocks in blockchain.blocks.items():
            for block in blocks:
                G.add_node(block.blk_id, label=f"Index: {block.index}\nMiner: {block.miner_id}\nMine Time: {block.mine_time}")

        for index, blocks in blockchain.blocks.items():
            for block in blocks:
                if block.prev_blk_id != -1:
                    G.add_edge(block.prev_blk_id, block.blk_id)

        pos = nx.spring_layout(G)
        labels = nx.get_node_attributes(G, 'label')
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color='skyblue', font_size=10)
        plt.title("Blockchain Visualization")
        plt.show()

    def plot_blockchain_tree(self):
        for peer in self.peers:
            self.visualize_blockchain(peer.blockchain)
    # Plot the blockchain tree for each peer
        # for peer_id, blockchain in self.blockchain_data.items():
        #     num_peers = len(self.blockchain_data)
        #     G = nx.DiGraph()
        #     labels = {}  # Dictionary to store node labels
        #     # Add information about the genesis block
        #     genesis_block = blockchain[0]
        #     genesis_label = f"Block ID: {genesis_block.blk_id}\nIndex: {genesis_block.index}\nMiner: Genesis\nTime: {genesis_block.mine_time}"
        #     G.add_node(str(genesis_block.blk_id))
        #     labels[str(genesis_block.blk_id)] = genesis_label
        #     # Add information about subsequent blocks
        #     for block in blockchain[1:]:
        #         node_label = f"Block ID: {block.blk_id}\nIndex: {block.index}\nMiner: {block.miner_id}\nTime: {block.mine_time}"
        #         G.add_node(str(block.blk_id))
        #         labels[str(block.blk_id)] = node_label
        #         if block.prev_blk_id != 0:
        #             G.add_edge(str(block.prev_blk_id), str(block.blk_id))
        #     plt.figure(figsize=(8, 6))
        #     pos = nx.spring_layout(G)
        #     nx.draw(G, pos, with_labels=False, node_size=5000, node_color='skyblue', font_size=8)
        #     nx.draw_networkx_labels(G, pos, labels, font_size=8, font_color='black', verticalalignment='center')
        #     plt.title(f"Blockchain Tree for Peer {peer_id} (Total Peers: {num_peers})")  # Include peer ID in the title
        #     plt.show()
        # pass


  
     
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
    simulation.plot_blockchain_tree()


# 1. Longest Chain selection on the basis of arrival time of the blocks
