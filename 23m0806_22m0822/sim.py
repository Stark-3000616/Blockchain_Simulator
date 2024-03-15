# Created by Sayantan Biswas & Shamik Kumar De

import random
import numpy as np
import networkx as nx
import heapq
import sys
import matplotlib.pyplot as plt

from event import Event
from peer import Peer
from peer import event_queue
from block import Block


class Simulation:
    # Function to initialize the simulation environment with the specified number of peers,
    # percentages of slow and low-CPU peers, and simulation duration.
    def __init__(self, num_peers, slow_percentage, low_cpu_percentage, simulation_duration):
        self.peers= []
        self.graph= nx.Graph()
        self.num_peers=num_peers
        self.simulation_duration = simulation_duration
        self.slow_percentage = slow_percentage
        self.low_cpu_percentage = low_cpu_percentage
        self.blockchain_data = {} # 


    #Initiliazing Peers
    def initialize_peers(self, speed_of_light_delay, mean_block_generation_time):
        #Randomly selecting peers to be slow and have low cpu
        slow=[0]*self.num_peers
        low_cpu=[0]*self.num_peers
        indices1 = random.sample(range(self.num_peers), int(self.num_peers * self.slow_percentage/ 100))
        indices2 = random.sample(range(self.num_peers), int(self.num_peers * self.low_cpu_percentage / 100))
        num_low_cpu=sum(low_cpu)
        num_high_cpu=self.num_peers-num_low_cpu
        #Determing Hashing Power
        hashing_power=1/(num_high_cpu*10 + num_low_cpu)
        for i in indices1:
            slow[i]=1
        for i in indices2:
            low_cpu[i]=1
        
        #Creating Peers
        for i in range(0, self.num_peers):
            peer = Peer(i, slow[i], low_cpu[i], speed_of_light_delay, hashing_power, mean_block_generation_time, self.num_peers)
            self.peers.append(peer)
    # Function to generate a random network topology by adding nodes corresponding to peers,
    # and connecting them randomly with a degree between 3 and 6.
    def generate_random_topology(self):
        self.graph.add_nodes_from(self.peers)
        for peer in self.peers:
            num_connections = random.randint(3,6) - self.graph.degree[peer]
            num_connections = max(0, num_connections)
            peers_to_connect = random.sample([other_peer for other_peer in self.peers if other_peer != peer and peer not in other_peer.neighbours and len(other_peer.neighbours)<6], num_connections)
            self.graph.add_edges_from([(peer, connected_peer) for connected_peer in peers_to_connect])
            for connected_peer in peers_to_connect:
                peer.neighbours.append((connected_peer.peer_id, connected_peer.is_slow))
    #Function to check for graph being connected or not
    def is_connected_graph(self):
        return nx.is_connected(self.graph)

    def recreate_graph(self):
        for peer in self.peers:
            peer.neighbours=[]
        self.generate_random_topology()

    def schedule_event(self, event_time, event_type, peer_id):
        event=Event(event_time, event_type, peer_id)
        heapq.heappush(event_queue, event)
    #Function to initialize events
    def initialize_events(self, simulation_duration, mean_transaction_time):
        event_time=0.0
        while event_time<= simulation_duration:
            peer = random.choice([node for node in self.peers])
            self.schedule_event(event_time, 'txn_generation', peer.peer_id)
            event_time+=np.random.exponential(mean_transaction_time)
            
   #Function for Scheduling the event of creating genesis block and then receiving by a peer
    def genesis_block_receive(self):
        genesis=Block(0, -1, 0, -1)
        genesis.balance=[50]*self.num_peers
        peer_id = 0
        genesis_event = Event(0, 'blk_receive', peer_id, genesis)
        heapq.heappush(event_queue, genesis_event)
    
    def display_network(self):
        nx.draw(self.graph, node_color='red', node_size=60, font_size=5)
        plt.savefig("graph.png")
        plt.close()

    def find_peer_by_id(self, id):
        for peer in self.peers:
            if peer.peer_id == id:
                return peer
        return None
    
    # Function to Run the simulation for the specified duration, processing events from the event queue.
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
    
    def visualize_blockchain(self, peer):
        G = nx.DiGraph()
        plt.figure(figsize=(5,10))
        blockchain = peer.blockchain
        levels = {}
        for index, blocks in blockchain.blocks.items():
            for block in blocks:
                G.add_node(block.blk_id, label=f"{block.index}")
                if block.index not in levels:
                    levels[block.index] = []
                levels[block.index].append(block.blk_id)

        for index, blocks in blockchain.blocks.items():
            for block in blocks:
                if block.prev_blk_id != -1:
                    G.add_edge(block.prev_blk_id, block.blk_id)

        # Position nodes from top to bottom, equidistant horizontally
        pos = {}
        x_spacing = 0.1
        y_spacing = 2
        for level, nodes in levels.items():
            y = -level * y_spacing
            for i, node in enumerate(nodes):
                pos[node] = (i * x_spacing, y)

        # Draw the graph
        labels = nx.get_node_attributes(G, 'label')
        nx.draw(G, pos, with_labels=True, labels=labels, node_size=100, node_color='skyblue', font_size=3, node_shape='s')
        longest_path=nx.dag_longest_path(G)
        counter=0
        for blk_id in longest_path:
            block=self.find_block_by_id(blk_id,peer)
            if block and block.miner_id != -1:
                miner= self.find_peer_by_id(block.miner_id)
                if not miner.is_low_cpu:
                    counter+=1
        plt.text(0,0, f'Total Number of Blocks: {sum([len(lst) for lst in peer.blockchain.blocks.values()])}\nNumber of Blocks in \nLongest Chain: {max(blockchain.blocks.keys())+1}\nBlocks by High CPU: {counter}\nBlocks by Low CPU: {len(longest_path)-counter}', fontsize=10, color='black')
        plt.title("Blockchain Visualization")
        plt.savefig(f"visuals/Blockchain_{peer.peer_id}.png")
        plt.close()

    def find_block_by_id(self,blk_id,peer):
        for value in peer.blockchain.blocks.values():
            for block in value:
                if block.blk_id == blk_id:
                    return block
        return None
    
    def plot_blockchain_tree(self):
        for peer in self.peers:
            self.visualize_blockchain(peer)
            
    def write_files(self):
        for peer in self.peers:
            lines=peer.file_writing_lines
            with open(f'block_tree_files/block_tree_{peer.peer_id}','w') as file:
                file.writelines(lines)

#Main function 
if __name__=="__main__":
    if(len(sys.argv)<7):
        print(f"Usage: {sys.argv[0]} <num_peers> <slow_%> <low_cpu_%> <mean_txn_time> <mean_blkgen_time> <duration>")
        sys.exit(1)
        
        
    #Taking arguments for simulation as input
    num_peers = int(sys.argv[1])
    slow_percentage = int(sys.argv[2])
    low_cpu_percentage = int(sys.argv[3])
    mean_transaction_time = int(sys.argv[4])
    mean_block_generation_time = int(sys.argv[5])
    simulation_duration = int(sys.argv[6])

    # Creating an object of Simulation Class
    simulation= Simulation(num_peers, slow_percentage, low_cpu_percentage, simulation_duration)
    
    # Speed of Light delay while propagation of
    speed_of_light_delay=random.uniform(0.01, 0.5)

    print("Creating peers...")
    simulation.initialize_peers(speed_of_light_delay, mean_block_generation_time)
    print("Creating network...")
    simulation.generate_random_topology()
    while not simulation.is_connected_graph():
        simulation.recreate_graph()
    print("Adding Events to the Queue...")
    simulation.initialize_events(simulation_duration, mean_transaction_time)
    print("Running Simulation...")
    # simulation.send_genesis_block()
    simulation.genesis_block_receive()
    simulation.run_simulation(simulation_duration)
    simulation.display_network()
    print("Simulation Completed")
    print("Drawing Pictures for Visualisation...")
    simulation.plot_blockchain_tree()
    print("Writing the block tree files...")
    simulation.write_files()
    print("Process Completed .. 100%")    

# 1. Longest Chain selection on the basis of arrival time of the blocks
# 2. 
