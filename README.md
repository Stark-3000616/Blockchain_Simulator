# CS765 Spring 2023 Semester, Project Part-1
# Simulation of a P2P Cryptocurrency Network with Double Selfish Mining Attack

## Overview
This project is a Python-based discrete-event simulation of a peer-to-peer blockchain network, including the behavior of peers generating transactions, mining blocks, and propagating them across the network. It explores the dynamics of blockchain consensus algorithms and the effects of various network parameters on the system's performance. Morover it simulates the attack of two selfish miners for visualization and analysis.

## Features
- Generates a network of peers with customizable characteristics (speed, CPU power).
- Simulates transaction generation and propagation among peers.
- Implements block mining with proof-of-work.
- Validates blocks and ensures the integrity of the blockchain.
- Visualizes the blockchain tree using NetworkX and Matplotlib.
- Supports customizable parameters.
- Provides event-driven simulation of transaction generation, block mining, and block propagation are scheduled.
- Validates transactions and blocks according to predefined rules to ensure the consistency and security of the blockchain network.
- Enables the study of various network topologies and their impact on blockchain performance.
- Simulates attacks by two different selfish miners acting individually with diffrent hashing powers.

## Requirements
- Python 3.10.12
- NetworkX
- NumPy
- Matplotlib
- Sys
- Heapq
- shortuuid

## Files
- sim.py
- peer.py
- blockchain.py
- transaction.py
- event.py
- block.py

## Usage
1. Set the desired parameters in the `main` function of `sim.py`.
2. Run the simulation script:
   
   python3 sim.py n z0 z1 T I t h1 h2
   
   where
   n -network size 
   z0-percentage of slow nodes 
   z1-percentage of nodes with low CPU power
   T -transaction interarrival time 
   I -mean block generation time
   t -simulation duration. 
   h1 - Hashing Power of selfish miner 1
   h2 - Hahsing Power of selfish miner 2
   
3. The simulation results and visualization will be saved in the project directory.

## Simulation Parameters
- Number of peers
- Percentage of slow peers
- Percentage of low-CPU peers
- Mean transaction time
- Mean block generation time
- Simulation duration
- Hashing Power of Selfish Miner 1
- Hashing Power of Selfish Miner 2

## Output
The simulation includes visualization of the blockchain tree using NetworkX and Matplotlib. The visualization shows the structure of the blockchain, including blocks and their relationships. Moreveor graph is generated for the demonstration of peer to peer network.
- graph.png: Visualization of the network topology.
- visuals/: Folder containing blockchain visualizations for each peer.
- block_tree_files/: Folder containing block tree files for each peer.

## Contributors
- Sayantan Biswas
- Shamik Kumar De

## Acknowledgements
- This project was developed as an assignment for CS764:Indroduction to Blockchain and Cryptocurrencies.
- Special thanks to Prof. Vinay Ribeiro for guidance and support.