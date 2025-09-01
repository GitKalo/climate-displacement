"""
Create "ground truth" dictionary maps between node names and node indices.

Dataset is hardcoded, but might want to make script more flexible in the future.
"""

import json
import pandas as pd

###################### Data processing approach ###########################
# The cleaned data should provide the support set of system units
# Then, using network structure to do processing (e.g. removing self-loops) 
# should be agnostic to settlement names (work on IDs only)
###########################################################################

# Load the weighted source-destination data
file_path = 'data/Weighted_network_data_3.csv'

# Create dataframe with settlement names
df_names = pd.read_csv(file_path)

# Extract unqiue settlement names and assign IDs
settlement_names = pd.unique(df_names[['source', 'target']].values.ravel())
settlement_names = sorted(settlement_names)  # Sorting maintains consistency within same dataset
name_to_idx = {n : i for i, n in enumerate(settlement_names)}
idx_to_name = {i : n for i, n in enumerate(settlement_names)}

# Save mappings betweeen names and IDs to disk (same location as dataaset)
with open(file_path.split('.')[0] + "_idx_to_name.json", 'w') as f:
    json.dump(idx_to_name, f)
with open(file_path.split('.')[0] + "_name_to_idx.json", 'w') as f:
    json.dump(name_to_idx, f)