"""
Read json files containing a dict of path counts for individual source variables
and combine them into a single json file representing a dict of dicts.
"""

import os, json, glob
import pandas as pd

###################### Data processing approach ###########################
# The cleaned data should provide the support set of system units
# Then, using network structure to do processing (e.g. removing self-loops) 
# should be agnostic to settlement names (work on IDs only)
###########################################################################

# File path of directory with individual files
input_dir = 'out/sim_output_source_diffusion'

# If directory does not exist, terminate script
if not os.path.exists(input_dir) :
    print(f"Directory of source files '{input_dir}' does not exist.")
    exit()

reduced_output_files = glob.glob(f'{input_dir}/*.json')
if reduced_output_files :
    # Initialize new dictionary for source-keyed path counts
    path_counts_by_source = {}
    for json_file in reduced_output_files :
        # Get source ID from filename
        source_id = int(json_file.split('/')[-1].split('.')[0])
        with open(json_file, 'r') as f :
            # Load path counts and add to new dict
            path_counts = json.load(f)
            path_counts_by_source[source_id] = path_counts

    # Write new data to single json file in same directory as input
    output_filename = input_dir + '_combined.json'
    with open(output_filename, 'w') as f :
        json.dump(path_counts_by_source, f)     # No indent to reduce filesize
else :
    print(f"No json files found in '{input_dir}'.")