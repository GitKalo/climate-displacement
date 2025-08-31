# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:49:25 2025

@author: mbozh
"""

import pandas as pd
import networkx as nx 
import numpy as np
import random 
import math
import matplotlib.pyplot as plt
import json
from tqdm import tqdm

from multiprocessing import Pool

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
            
            # If we reach a stop/sink node (zero out degree),
            # stop current path realization
            if G.out_degree(current) == 0:
                continue

        #if path[-1] == target:
        paths.append(path)

    return paths

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

file_path = './Weighted_network_data_3.csv'
df = pd.read_csv(file_path)
G_s = create_network(df)

idx_to_name = {i : n for i, n in enumerate(G_s.nodes())}
name_to_idx = {n : i for i, n in enumerate(G_s.nodes())}

G = nx.relabel_nodes(G_s, name_to_idx) 

print(list(G_s.nodes())[:20])
print(len(set(G_s.nodes())) == len(set(G.nodes())))
print(list(G.nodes())[:20])    

#network analysis
disconnected_edges = []
for component in nx.weakly_connected_components(G):  # for directed graph G
    subgraph = G.subgraph(component)
    if subgraph.number_of_nodes() == 2 and subgraph.number_of_edges() == 1:
        disconnected_edges.extend(subgraph.edges())

#len(disconnected_edges) #252

largest_cc_nodes = max(nx.weakly_connected_components(G),key=len) #4765 nodes
largest_cc_subgraph = G.subgraph(largest_cc_nodes).copy()

zero_out_degree_nodes = [node for node in largest_cc_subgraph.nodes if largest_cc_subgraph.out_degree(node) == 0]
#1584
# in_degrees_list = []
# for node in zero_out_degree_nodes:
#     in_degrees_list.append(len(list(largest_cc_subgraph.predecessors(node))))

#plt.hist(in_degrees_list,bins=max(in_degrees_list))
#plt.xlabel('In-degree')
#plt.ylabel('Frequency')

nonzero_out_degree_nodes = [node for node in largest_cc_subgraph.nodes if largest_cc_subgraph.out_degree(node) > 0]


# Remove self-loops from the largest connected component subgraph
largest_cc_subgraph.remove_edges_from(nx.selfloop_edges(largest_cc_subgraph))

# Calculate paths, saving intermittently
# c = 0
for source in tqdm(nonzero_out_degree_nodes[:50]):
    source_paths = {}
    for target in largest_cc_subgraph.nodes():
        if target != source:
            # Calculate paths for pair
            pair_paths = collect_paths(largest_cc_subgraph, source, target, num_paths=300, max_steps=10**4)

            # Add paths to dict
            # paths[(source,target)] = pair_paths

            # Append paths to file
            # f.write({(source,target) : pair_paths}.__repr__() + "\n")

            source_paths[target] = pair_paths

            # filename = f"{source}@{target}"
            # with open("output/" + filename + "_" + str(c) + ".json", 'w') as f:
    with open("output/" + str(source) + ".json", 'w') as f:
        json.dump(source_paths, f)
    # c += 1