# TODO: Add docstrings

import networkx as nx   # For creating Graph object
import pandas as pd     # For reading CSV data
import json             # For saving/loading name-ID maps

def get_network_from_file(file_path, relabel_names=True):
    """
    Load a network from a CSV file into a NetworkX graph, utilizing name 
    and ID maps.

    Parameters:
    ----------
    file_path : str
        Path to the CSV file containing the network data. Assumes that:
        - File has at least columns ['source', 'target', 'weight'];
        - The 'source' and 'target' values are strings corresponding to settlement names;
        - There exist the corresponding name-ID maps as JSON files within the same directory.

    Returns:
    -------
    G : networkx.DiGraph
        A directed graph constructed from the CSV data.
    """
    # Read raw data into DataFrame
    df = pd.read_csv(file_path)
    
    # Create weighted DiGraph from data
    G = create_network(df)

    if relabel_names :
        # Load name-to-ID mapping
        file_path_noext = file_path.split('.')[0]
        with open(file_path_noext + "_name_to_id.json", 'r') as f:
            name_to_id = json.load(f)

        # Relabel network using mapping
        G = nx.relabel_nodes(G, name_to_id)

        # Save settlement name as node attribute
        nx.set_node_attributes(
            G, 
            {id : n for n, id in name_to_id.items()}, 
            'settlement_name'
        )
        # TODO: Do we want to do this? Or better to keep file on disk as objective mapping?

    return G

def create_network(df) :
   """
   Converts a DataFrame with source nodes, target nodes and edge weights
   into a directed NetworkX graph.

   Parameters:
   ----------
   df : pandas.DataFrame
       A DataFrame with the following columns:
       - 'source': Source node (str or int)
       - 'target': Target node (str or int)
       - 'weight': Weight of the directed edge (float)

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
       G.add_edge(source, target, weight=float(weight))    # In case of duplcate edges this will overwrite weight

   return G