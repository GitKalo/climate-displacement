"""
Reduce the number of paths in each output file by taking the first N paths.
"""

import json, glob, os

N = 100     # Number of paths to keep

if not os.path.exists('out/sim_output_reduced') :
    os.makedirs('out/sim_output_reduced')

full_output_files = glob.glob('out/sim_output/*.json')
if full_output_files :
    for json_file in full_output_files :
        with open(json_file, 'r') as f :
            data = json.load(f)

            data_new = {}
            for target, paths in data.items() :
                data_new[target] = paths[:N]

            with open(f"out/sim_output_reduced/{json_file.split('/')[-1]}", 'w') as f :
                json.dump(data_new, f)
else :
    print("No output files found in 'out/sim_output'.")