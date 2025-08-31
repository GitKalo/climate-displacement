# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:49:25 2025

@author: mbozh
"""

import pandas as pd
import networkx as nx
import random 
import json
import os

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

def run_paths_for_targets(source, G) :
    source_paths = {}
    for target in G.nodes():
        if target != source:
            # Calculate paths for pair
            pair_paths = collect_paths(G, source, target, num_paths=300, max_steps=10**4)

            source_paths[target] = pair_paths
    
    with open("output/" + str(source) + ".json", 'w') as f:
        json.dump(source_paths, f)
        print(source)
    
    return source_paths

file_path = './Weighted_network_data_3.csv'
df = pd.read_csv(file_path)
G_s = create_network(df)

idx_to_name = {i : n for i, n in enumerate(G_s.nodes())}
name_to_idx = {n : i for i, n in enumerate(G_s.nodes())}

G = nx.relabel_nodes(G_s, name_to_idx) 

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


nonzero_out_degree_nodes = [node for node in largest_cc_subgraph.nodes if largest_cc_subgraph.out_degree(node) > 0]

source_nodes = [n for n in nonzero_out_degree_nodes if not os.path.exists(f"output/{n}.json")]
print(source_nodes)

# Remove self-loops from the largest connected component subgraph
largest_cc_subgraph.remove_edges_from(nx.selfloop_edges(largest_cc_subgraph))

if __name__ == "__main__":
    # Calculate paths, saving intermittently
    args = [(n, largest_cc_subgraph) for n in source_nodes]
    n_workers = 60
    with Pool(processes=n_workers) as pool:
        results = pool.starmap(run_paths_for_targets, args)