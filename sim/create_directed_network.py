# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 10:45:45 2025

@author: mbozh
"""
import networkx as nx
import numpy as np
import pandas as pd

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