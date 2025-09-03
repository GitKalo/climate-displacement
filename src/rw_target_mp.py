# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:49:25 2025

@author: mbozh
"""

import networkx as nx
import random 
import json
import os, sys

from multiprocessing import Pool

# Import our own helper functions
from network_utils import get_network_from_file

def collect_paths(G, source, target, num_paths=1000, max_steps=100, uniform_rw=False):
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

        # Stop at target, sink, or max steps
        while current != target \
              and G.out_degree(current) > 0 \
              and steps < max_steps :
            neighbors = list(G.successors(current))
            if uniform_rw :         # Uniform walk
                current = random.choices(neighbors, k=1)[0]
            else :                  # Biased walk
                probabilities = [G[current][nbr].get('weight', 1.0) for nbr in neighbors]
                current = random.choices(neighbors, weights=probabilities, k=1)[0]
            path.append(current)
            steps += 1
            
        paths.append(path)

    return paths

def run_paths_for_targets(G, source, output_dir='out/output', uniform_rw=False) :
    """
    Run random walk simulations for all target nodes in G from a given source 
    node and save the results as a json file.

    Parameters:
    ----------
    G : networkx.DiGraph
        A directed graph with edge weights used as transition probabilities 
        (unless `uniform_rw` is True).
    source : node
        Starting node for the random walk.
    output_dir : str
        Directory to save the output json file with name <source>.json.
    uniform_rw : bool
        Whether to use uniform random walk instead of biasing the walk
        transition probabilities using edge weights in G. Defaults to False,
        i.e. a biased walk.

    Returns:
    -------
    paths : dict of lists
        A dictionary indexed by target node IDs containing up to `num_paths` 
        paths (lists of nodes) from the source node to the respective target.
        Note that these are "attemped" paths to target — not all paths end at 
        the desired target node, since they can get stuck in "sink" nodes.
    """
    source_paths = {}
    for target in G.nodes():
        if target != source:
            # Calculate paths for pair
            pair_paths = collect_paths(G, source, target, num_paths=300, max_steps=10**4, uniform_rw=uniform_rw)

            source_paths[target] = pair_paths

    outfile = f"{output_dir}/{source}.json"
    with open(outfile, 'w') as f:
        json.dump(source_paths, f)
        print(f"Wrote results to {outfile}")

    return source_paths

# Generate network from data
dataset_path = 'data/Weighted_network_data_3.csv'
G = get_network_from_file(dataset_path, relabel_names=True)
# TODO: Create script for network generation that saves network as 
# pickled object on disk, so we avoid generating each time?

# Keep only largest connected component of graph
largest_cc_nodes = max(nx.weakly_connected_components(G),key=len) #4765 nodes
largest_cc_subgraph = G.subgraph(largest_cc_nodes).copy()

# Remove self-loops
largest_cc_subgraph.remove_edges_from(nx.selfloop_edges(largest_cc_subgraph))

# Directory to output json files to
output_dir = 'out/sim_output_target'

# Create directory if it does not exist yet
if not os.path.exists(output_dir) : os.makedirs(output_dir)

# Get potential source nodes
nonzero_out_degree_nodes = [node for node in largest_cc_subgraph.nodes if largest_cc_subgraph.out_degree(node) > 0]

# Get list of source nodes (nonzero out degree nodes that we have not processed yet)
source_nodes = [n for n in nonzero_out_degree_nodes if not os.path.exists(f"{output_dir}/{n}.json")]

if __name__ == "__main__":
    # Print useful parameters
    print(f"Using data from '{dataset_path}'.")
    print(f"Saving results to '{output_dir}'.")

    # Get mode of simulating random walks (biased or uniform)
    try :
        mode = sys.argv[1]
        if mode == 'biased' :
            uniform_rw = False
        elif mode == 'uniform' :
            uniform_rw = True
        else :
            raise ValueError(f"Unknown mode: {mode}")
    except IndexError :
        # If no mode specified, default to biased
        uniform_rw = False
        print("No mode specified, defaulting to biased random walk.")

    # Calculate paths, saving intermittently
    args = [(largest_cc_subgraph, n, output_dir, uniform_rw) for n in source_nodes]
    n_workers = 4
    with Pool(processes=n_workers) as pool:
        results = pool.starmap(run_paths_for_targets, args)