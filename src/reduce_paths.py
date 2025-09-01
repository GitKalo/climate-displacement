import json, glob, os

if not os.path.exists('output_reduced'):
    os.makedirs('output_reduced')

for json_file in glob.glob('output/*.json')[:10]:
    with open(json_file, 'r') as f:
        data = json.load(f)

        data_new = {}
        for target, paths in data.items():
            data_new[target] = paths[:100]
            # for path in paths :
            #     path_string = '@'.join([str(n) for n in path])
            #     data_new[target][path_string] = data_new[target].get(path_string, 0) + 1

        # for target, paths in data_new.items():
        #     N = 0
        #     for n in paths.values() :
        #         N += n
        #     print(N)

        # for target, paths in data_new.items():
        #     with open(f"output_reduced/{json_file.split('/')[-1]}", 'w') as f:
        #         json.dump(data_new, f)
        
        with open(f"output_reduced/{json_file.split('/')[-1]}", 'w') as f:
            json.dump(data_new, f)