"""
Go from storing lists of observed paths to dictionary with counts of how many
times each path was observed.

TODO: Ideally, we would save in this format directly in the simulation script,
to avoid unnecessary memory use and data processing.
"""

import json, glob, os

if not os.path.exists('out/sim_output_counts') :
    os.makedirs('out/sim_output_counts')

for json_file in glob.glob('out/sim_output_reduced/*.json') :
    with open(json_file, 'r') as f :
        data = json.load(f)

        data_new = {}
        for target, paths in data.items() :
            data_new[target] = {}
            for path in paths :
                path_string = '@'.join([str(n) for n in path])
                data_new[target][path_string] = data_new[target].get(path_string, 0) + 1

        # for target, paths in data_new.items():
        with open(f"out/sim_output_counts/{json_file.split('/')[-1]}", 'w') as f :
            json.dump(data_new, f)