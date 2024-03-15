# CS765 Spring 2023 Semester, Project Part-1
# Simulation of a P2P Cryptocurrency Network

## Overview
This project is a discrete-event simulator to study blockchain networks. It simulates the behavior of peers in the network, their interactions, transaction generation, block mining, and block propagation.

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

## Requirements
- Python 3.10.12
- NetworkX
- NumPy
- Matplotlib

## Files
- sim.py
- peer.py
- blockchain.py
- transaction.py
- event.py
- block.py
- Workflow.png
- Report.pdf

## Usage
1. Set the desired parameters in the `main` function of `sim.py`.
2. Run the simulation script:
   
   python3 sim.py n z0 z1 T I t
   
   where
   n -network size 
   z0-percentage of slow nodes 
   z1-percentage of nodes with low CPU power
   T -transaction interarrival time 
   I -mean block generation time
   t -simulation duration. 
   
3. The simulation results and visualization will be saved in the project directory.

## Simulation Parameters
- Number of peers
- Percentage of slow peers
- Percentage of low-CPU peers
- Mean transaction time
- Mean block generation time
- Simulation duration

## Visualization
The simulation includes visualization of the blockchain tree using NetworkX and Matplotlib. The visualization shows the structure of the blockchain, including blocks and their relationships.

## Contributors
- Sayantan Biswas
- Shamik Kumar De

