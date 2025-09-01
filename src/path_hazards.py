"""
Use precomputed distribution of IDPs over hazards to calculate a weighted hazard
exposure vector for a path, or more generally a set of nodes. Relies on
precomputed IDP distributions in `data/settlement_IDPs.txt`.

This script is a stub — currently it implements the main function and gives an
example of running it, but is not integrated with other scripts.
"""

import ast
import numpy as np

# Load distribution of IDPs over hazards for each settlement
settlement_IDPs = np.loadtxt('data/settlement_IDPs.txt', dtype=int)

def get_node_set_IDPs(node_set) :
    """
    Returns a vector of IDPs for different hazard types, aggregated over 
    the IDPs of the nodes in the node set.

    node_set (list of int) : List of node IDs
    """
    IDPs_agg = np.zeros(settlement_IDPs.shape[1], dtype=int)
    for node_id in node_set :
        IDPs_agg += settlement_IDPs[node_id, :]
    
    return IDPs_agg

############################## Example application #############################

# Define a path (set of nodes)
node_set = {0, 1, 2}
# node_set = np.random.choice(range(settlement_IDPs.shape[0]), size=10, replace=False)
print(f"Calculating hazard exposure along path: {node_set}")

# Get aggregated IDPs vector for the node set
IDPs_vector = get_node_set_IDPs(node_set)
print(f"Aggregated IDPs over hazards: {IDPs_vector}")

# Normalize to obtain hazard exposure vector weighted by each hazard's IDPs
def get_hazard_exposure_vector(IDPs_vector) :
    return IDPs_vector / np.sum(IDPs_vector)
print(f"Final hazard exposure vector: {get_hazard_exposure_vector(IDPs_vector)}")