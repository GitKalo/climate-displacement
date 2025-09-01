# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:49:25 2025

@author: mbozh
"""

import pandas as pd
import networkx as nx 
import numpy as np
import random 


def create_network(df):
   """
   Converts a DataFrame with source nodes, target nodes and edge weights
   into a directed NetworkX graph.

   Parameters:
   ----------
   df : pandas.DataFrame
       A DataFrame with the following columns:
       - 'source': Source node (str or int)
       - 'target': Target node (str or int)
       - 'weight': Weight of the directed edge (int or float)

   Returns:
   -------
   G : networkx.DiGraph
       A directed graph where each edge from 'source' to 'target' has an associated weight.
   """
   
   G = nx.DiGraph() # Initialize a directed graph

   # Iterate through each row to add edges with weights
   for _, row in df.iterrows():
       source = row['source']
       target = row['target']
       weight = row['weight']
       G.add_edge(source, target, weight=weight)

   return G

'''
#Generate random dataframe to check the code:
df = pd.DataFrame({
    'source': np.random.randint(0, 500, size=1000),
    'target': np.random.randint(0, 500, size=1000),
    'weight': np.random.rand(1000)
})

#Built in networkx
G = nx.from_pandas_edgelist(df, source='source', target='target', edge_attr='weight', create_using=nx.DiGraph(), edge_key=None)

#function check:
G = create_network(df) #quick enough
'''

df = pd.read_csv(r'C:\Users\mbozh\Desktop\Codes for CS72h\Weighted_network_data.csv')
G = create_network(df)

#network analysis
disconnected_edges = []
for component in nx.weakly_connected_components(G):  # for directed graph G
    subgraph = G.subgraph(component)
    if subgraph.number_of_nodes() == 2 and subgraph.number_of_edges() == 1:
        disconnected_edges.extend(subgraph.edges())

#len(disconnected_edges) #266 

largest_cc_nodes = max(nx.weakly_connected_components(G)) #5165 nodes
largest_cc_subgraph = G.subgraph(largest_cc_nodes).copy()

##### Collect the paths: 

r'''
def collect_paths(G, source, target, num_paths=1000, max_steps=100):
    """
    Perform random walks on a directed weighted graph from source to target.

    Parameters:
    ----------
    G : networkx.DiGraph
        A directed graph with edge weights used as transition probabilities.
    source : node
        Starting node for the random walk.
    target : node
        Ending node to stop the walk.
    num_paths : int
        Number of random walk paths to collect (default = 1000).
    max_steps : int
        Maximum steps per walk to avoid infinite loops (default = 100).

    Returns:
    -------
    paths : list of lists
        A list containing up to `num_paths` paths (each a list of nodes) from source to target.
    """
    paths = []

    for _ in range(num_paths):
        path = [source]
        current = source
        steps = 0

        while current != target and steps < max_steps:
            neighbors = list(G.successors(current))
            if not neighbors:
                break  # dead end
            probabilities = [G[current][nbr].get('weight', 1.0) for nbr in neighbors]
            #print(probabilities)
            current = random.choices(neighbors, weights=probabilities, k=1)[0]
            path.append(current)
            #print(path)
            steps += 1

        if path[-1] == target:
            paths.append(path)

    return paths



#check code with the directed network created in create_directed_network
paths = dict()
from tqdm import tqdm
for source in tqdm(G.nodes()):
    for target in G.nodes():
        if target!=source:
            paths[(source,target)] =  collect_paths(G, source, target, num_paths=1000, max_steps=100)
        
'''

import networkx as nx
import random
from tqdm import tqdm

def precompute_transitions(G):
    """
    Precompute neighbor lists and edge weights for all nodes in the graph.
    Returns a dictionary: node -> (neighbors, weights)
    """
    transitions = {}
    for node in G.nodes():
        neighbors = list(G._succ[node])
        if neighbors:
            weights = [G[node][nbr].get('weight', 1.0) for nbr in neighbors]
            transitions[node] = (neighbors, weights)
    return transitions

def collect_paths(G, source, target, transitions, num_paths=1000, max_steps=100, random_seed=None):
    """
    Perform random walks from source to target using precomputed transitions.

    Parameters:
    -----------
    G : networkx.DiGraph
    source : node
    target : node
    transitions : dict
        Precomputed neighbors and weights per node.
    num_paths : int
    max_steps : int
    random_seed : int or None

    Returns:
    --------
    paths : list of list of nodes
    """
    rng = random.Random(random_seed)
    paths = []

    for _ in range(num_paths):
        path = [source]
        current = source
        steps = 0

        while current != target and steps < max_steps:
            if current not in transitions:
                break  # dead end
            neighbors, weights = transitions[current]
            current = rng.choices(neighbors, weights=weights, k=1)[0]
            path.append(current)
            steps += 1

        if path[-1] == target:
            paths.append(path)

    return paths

# === Main run ===

transitions = precompute_transitions(largest_cc_subgraph)

paths = {}
for source in tqdm(largest_cc_subgraph.nodes(), desc="Processing sources"):
    for target in largest_cc_subgraph.nodes():
        if source != target and nx.has_path(largest_cc_subgraph, source, target):  # Optional: skip if unreachable
            paths[(source, target)] = collect_paths(
                largest_cc_subgraph, source, target, transitions, num_paths=1000, max_steps=100
            )

    