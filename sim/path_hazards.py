import json, ast
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

settlement_IDPs = np.loadtxt('settlement_IDPs.txt', dtype=int)

print(settlement_IDPs.shape)
print(settlement_IDPs)

node_set = {0, 1, 2}
# node_set = np.random.choice(range(settlement_IDPs.shape[0]), size=10, replace=False)

with open('hazards_set.txt', 'r') as f : hazards_list = ast.literal_eval(f.read())

print(hazards_list)

def get_node_set_IDPs(node_set) :
    """
    Returns a vector of IDPs for different hazard types, aggregated over 
    the IDPs of the nodes in the node set.

    node set (list of int) : List of node indeces
    """
    IDPs_agg = np.zeros(settlement_IDPs.shape[1], dtype=int)
    for node_idx in node_set :
        IDPs_agg += settlement_IDPs[node_idx, :]
    
    return IDPs_agg

IDPs_vector = get_node_set_IDPs(node_set)
print(IDPs_vector)

def get_hazard_exposure_vector(IDPs_vector) :
    return IDPs_vector / np.sum(IDPs_vector)

print(get_hazard_exposure_vector(IDPs_vector))