import graph_tool.topology
import graph_tool as gt
import geopandas as gpd
import pandas as pd

import argparse
import tqdm
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
    network_type = args.network_type
    
    to_crs = 'epsg:20539'
    date = '251124'

    loaddir = '/data/big/fmalveiro/complexity72/'
    savedir = './data/'
    
    adjlist_file = f"geographical_neighbours-{network_type}.csv"

    adm_level = 2
    adm_file = f"gadm41_SOM_{adm_level}.json.zip"
    nodes_file = f"road_network_elements-{network_type}.zip!somalia-{date}-nodes.geojson"

    graph_file = f"somalia-road_network_graph-{network_type}.gt.gz"

    neighbours_file = f"geographical_neighbours-{network_type}.csv"
    
    print('Loading adj list...')
    adjlist = pd.read_csv(os.path.join(savedir, adjlist_file), index_col=False)

    
    print('Loading adm gdf...')
    adm_gdf = gpd.read_file(os.path.join(savedir, adm_file))

    print('Loading nodes gdf...')
    nodes_gdf =  gpd.read_file(os.path.join(loaddir, nodes_file))

    
    print('Loading graph...')
    graph = gt.load_graph(os.path.join(loaddir, graph_file))

    # convert graph to undirected, otherwise we'll have dead ends
    und_graph = gt.GraphView(graph, directed=False)

    # project to crs in metres
    print('Projecting adm gdf...')
    proj_adm = adm_gdf.to_crs(to_crs)

    print('Projecting nodes gdf...')
    proj_nodes = nodes_gdf.to_crs(to_crs)

    # represent area as point: centroid
    proj_adm['centroid'] = proj_adm.centroid

    # find nearest nodes to adm regions
    # 'distance' corresponds to the length of the straight-line between
    # the centroid of the adm area and its closest node on the road network graph
    print('Finding nearest nodes...')
    nearest = proj_adm[['centroid']].set_geometry('centroid').sjoin_nearest(
        proj_nodes[['geometry']], distance_col='distance')


    # identify the road nodes that are part of the adjacency list
    # i.e., for each (src, tgt) pair in the adj list, 
    # find the corresponding pair of nearest nodes in the road network, determined just before
    adjlist['src_vx'] = adjlist['focal'].map(lambda x: nearest.iloc[x]['index_right'])
    adjlist['tgt_vx'] = adjlist['neighbour'].map(lambda x: nearest.iloc[x]['index_right'])

    # form the pairs and remove double occurrences, 
    # it may save computation time in case they repeat
    pairs = adjlist.apply(lambda x: (x['src_vx'], x['tgt_vx']), axis=1)
    pairs = pairs.drop_duplicates()

    # find distance between pairs of nodes in the road network
    print('Finding shortest distance through road network...')
    tqdm.tqdm.pandas(desc='shorest_distance')
    distance = pairs.progress_apply(lambda x: graph_tool.topology.shortest_distance(und_graph, x[0], x[1], weights=und_graph.ep['length']))
    distance.index = pd.MultiIndex.from_arrays((adjlist['src_vx'], adjlist['tgt_vx']))

    
    # associate the distance through the road network to the original adj list

    # src_distance: distance from centroid of src adm unit to road network
    # tgt_distance: distance from centroid of tgt adm unit to road network
    adjlist['src_distance'] = adjlist['focal'].map(lambda x: nearest['distance'].iloc[x])
    adjlist['tgt_distance'] = adjlist['neighbour'].map(lambda x: nearest['distance'].iloc[x])

    # in_distance: distance, through the road nework, between the closest nodes in the road network
    adjlist['in_distance'] = adjlist.apply(lambda x: distance.loc[(x['src_vx'], x['tgt_vx'])], axis=1)

    # road_distance: sum of the distances above mentioned
    # correponds to the distance through the road network between (src, tgt) pairs of adm areas
    adjlist['road_distance'] = adjlist.apply(lambda x: x['src_distance'] + x['in_distance'] + x['tgt_distance'], axis=1)

    print('Saving to file...')
    adjlist.to_csv(os.path.join(savedir, neighbours_file), index=False)
    return



if __name__ == '__main__':    
    parser = argparser()
    args = parser.parse_args()
    main(args)
