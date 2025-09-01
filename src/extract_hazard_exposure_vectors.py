"""
Compute the "exposure vectors" for each settlement. That is, the distribution of 
the number of Internally Displaced Persons (IDPs) for each hazard type. These
represent the probability of encountering a specific hazard at each settlement.

The script first preprocesses the data in `data/settlements_corrected_1-2.csv`
and saves the simplified dataset to `data/hazards_displacements.csv`.

Additionally relies on the files `data/hazards_set.txt` (for the list of 
hazard types) and `data/Weighted_network_data_3_name_to_id.json` (for the 
mapping of settlement names to their IDs in the network). 

The main output is the file `data/settlement_IDPs.txt`, which is in the format
of a 2D matrix, where:
- rows correspond to settlements (ordered by the keys in the mapping);
- columns correspond to hazard types (ordered according to the hazards set); and
- values represent the number of IDPs.
"""

import json
import numpy as np
import pandas as pd

################# Clean datasets for use in hazard analysis ####################

# Load raw data
file_path = 'data/settlements_corrected_1-2.csv'
df = pd.read_csv(file_path)

# Filter the df to keep only columns relevant for hazard analysis
df_hazards = df.filter(items=['Settlement Name', 'Total new arrivals since last week', 'Number of Males (18 and above) since last week', 'Number of Females (18 and above) since last week', 'Number of Children under 18 since last week', 'Final destination of the new arrivals', 'Reason of Displacement', 'Somalia Location of Origin (Corrected)'])

# Consolidate Other values
df_hazards['Reason of Displacement'] = \
    df_hazards['Reason of Displacement'].replace({'Other Natural Hazards': 'Other'})

# Simplify column names
df_hazards = df_hazards.rename(columns={
    'Settlement Name': 'arrival_settlement',
    'Total new arrivals since last week': 'arrivals_total',
    'Number of Males (18 and above) since last week': 'arrivals_males',
    'Number of Females (18 and above) since last week': 'arrivals_females',
    'Number of Children under 18 since last week': 'arrivals_children',
    'Final destination of the new arrivals': 'final_destination',
    'Reason of Displacement': 'origin_hazard',
    'Somalia Location of Origin (Corrected)': 'origin_settlement'
})

# Convert final destination question to bool type
df_hazards['final_destination'] = \
    df_hazards['final_destination'].map(lambda x: True if x == 'Yes' else False)

# Keep only final destination flows
df_hazards = df_hazards[df_hazards['final_destination'] == True]

# Print final dataset format
print(df_hazards.head())

# Save hazards dataset
df_hazards.to_csv('data/hazards_displacements.csv', index=False)

# Extract and save set of hazards
hazards_list = df_hazards['origin_hazard'].unique().tolist()
with open('data/hazards_set.txt', 'w') as f: f.write(hazards_list.__repr__())

################# Calculate exposure vectors for each hazard ###################

# Get name to ID mapping
with open('data/Weighted_network_data_3_name_to_id.json', 'r') as f : 
    name_to_id = json.load(f)

# Collect IDP counts indexed by settlement ID in network and hazard index
settlement_IDPs = np.zeros((len(name_to_id.keys()), len(hazards_list)), dtype=int)
for idx, row in list(df_hazards.iterrows()) :
    hazard = row['origin_hazard']
    hazard_idx = hazards_list.index(hazard)
    origin = row['origin_settlement']
    try :
        origin_idx = name_to_id[origin]
    except KeyError:
        # If settlement not in mapping, i.e. node not in network, ignore
        pass
    settlement_IDPs[origin_idx, hazard_idx] += row['arrivals_total']

print(f"Number of datapoints with missing origin hazards: {df_hazards['origin_hazard'].isna().sum()}")

# Save IDPs data
np.savetxt('data/settlement_IDPs.txt', settlement_IDPs, fmt='%d')

#####
# df_nwk = pd.read_csv('Weighted_network_data_3.csv')
# print(len(df_nwk['source'].unique()))
# print(len(df_nwk['target'].unique()))
# all_nodes_nwk = set(df_nwk['source'].unique()).union(set(df_nwk['target'].unique()))
# # print(all_nodes_nwk)
# print(len(all_nodes_nwk))

# df_hazards = df_hazards[df_hazards['final_destination'] == True]
# all_names_df = set(df_hazards['origin_settlement'].unique()).union(set(df_hazards['arrival_settlement'].unique()))
# print(len(all_names_df))

# print(all_names_df - all_nodes_nwk)
# print(len(all_names_df - all_nodes_nwk))
# # print(all_nodes_nwk - all_names_df)

# print(len(np.where(settlement_IDPs.sum(axis=1) == 0)[0]))