"""
Reduce the number of paths in each output file by taking the first N paths.
"""

import json, glob, os

N = 100

if not os.path.exists('out/sim_output_reduced') :
    os.makedirs('out/sim_output_reduced')

for json_file in glob.glob('out/sim_output/*.json') :
    with open(json_file, 'r') as f :
        data = json.load(f)

        data_new = {}
        for target, paths in data.items() :
            data_new[target] = paths[:N]

        with open(f"out/sim_output_reduced/{json_file.split('/')[-1]}", 'w') as f :
            json.dump(data_new, f)