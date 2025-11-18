"""
Get nodes and edges that form the road network graph out of osm data.
"""


import pyrosm

import tempfile
import zipfile
import os



def main():
    date = '250905'

    savedir = '/data/big/fmalveiro/complexity72/'
    zipped_osm = os.path.join(savedir, 'osm_data.zip')
    zipped_elements = os.path.join(savedir, 'DEFAULT-road_network_elements.zip')

    osmfile = f"somalia-{date}-highways.osm.pbf"

    node_vars = ['id', 'geometry']
    edge_vars = ['u', 'v', 'highway', 'length', 'geometry']

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
        nodes_gdf, edges_gdf = parser.get_network(network_type='all', nodes=True)

        nodes_gdf = nodes_gdf[node_vars]
        edges_gdf = edges_gdf[edge_vars]

        print(f"There are {nodes_gdf.shape[0]} nodes and {edges_gdf.shape[0]} edges.")


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
    main()
