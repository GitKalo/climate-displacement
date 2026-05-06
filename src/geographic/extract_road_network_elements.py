"""
Get nodes and edges that form the road network graph out of osm data.
"""


import pyrosm

import argparse
import tempfile
import zipfile
import sys
import os


def argparser():
    parser = argparse.ArgumentParser(
                    prog=sys.argv[0],
                    description='What the program does',
                    epilog='Text at the bottom of help'
    )

    parser.add_argument('--network_type', type=str, choices=('walking', 'cycling', 'driving', 'driving+service', 'all'), default='all')
    return parser


def main(args):    
    date = '251124'

    node_vars = ['id', 'geometry']
    edge_vars = ['u', 'v', 'highway', 'length', 'geometry']

    network_type = args.network_type
    
    
    savedir = '/data/big/fmalveiro/complexity72/'
    zipped_osm = os.path.join(savedir, 'osm_data.zip')
    zipped_elements = os.path.join(savedir, f"DEFAULT-road_network_elements-{network_type}.zip")

    osmfile = f"somalia-{date}-highways.osm.pbf"



    # zip library will write within the zipfile, not overwriting it...
    if os.path.exists(zipped_elements):
        print(f"{zipped_elements} exists. Removing...")
        os.remove(zipped_elements)

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zipped_osm, 'r') as zfile:
            zfile.extract(osmfile, tmpdir)

        loadpath = os.path.join(tmpdir, osmfile)
        
        parser = pyrosm.OSM(loadpath)      

        print('Obtaining road network elements...')
        nodes_gdf, edges_gdf = parser.get_network(network_type=network_type, nodes=True)

        nodes_gdf = nodes_gdf[node_vars]
        edges_gdf = edges_gdf[edge_vars]

        print(f"There are {nodes_gdf.shape[0]} nodes and {edges_gdf.shape[0]} edges for network_type={network_type}.")


        for element, gdf in zip(('nodes', 'edges'), (nodes_gdf, edges_gdf)):
            savefile = f"somalia-{date}-{element}.geojson"
            savepath = os.path.join(tmpdir, savefile)

            print(f"Saving {element}...")
            gdf.to_file(savepath)

        with zipfile.ZipFile(zipped_elements, 'w') as zfile:
            for element, gdf in zip(('nodes', 'edges'), (nodes_gdf, edges_gdf)):
                loadfile = f"somalia-{date}-{element}.geojson"
                loadpath = os.path.join(tmpdir, loadfile)

                print(f"Zipping {element}...")
                zfile.write(loadpath, arcname=loadfile)

    return



if __name__ == '__main__':    
    parser = argparser()
    args = parser.parse_args()
    main(args)
