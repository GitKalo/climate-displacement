"""
Construct the road network graph out of nodes and edges.
"""

import graph_tool.topology
import graph_tool as gt
import geopandas as gpd
import pandas as pd
import numpy as np
import shapely

import itertools
import tempfile
import zipfile

import tqdm
import os



def get_graph(nodes_gdf, edges_gdf, node_vars, edge_vars, graph_attrs=None):

    dtype_mapping = {
        'int64': 'int',
        'float64': 'float',
        'int32': 'int'
    }
    
    for columns, gdf in zip((node_vars, edge_vars), (nodes_gdf, edges_gdf)):
        assert all([column in gdf.columns for column in columns])

    nodes_gdf = nodes_gdf[node_vars]
    edges_gdf = edges_gdf[edge_vars]
        
    
    # pass from vertex ids to vertex index in dataframe: map ids to vertex index
    assert 'id' in nodes_gdf.columns
    assert nodes_gdf['id'].unique().size == nodes_gdf.shape[0]
    

    # only add nodes for which there are edges
    used_nodes = np.sort(np.union1d(edges_gdf['u'].to_numpy(), edges_gdf['v'].to_numpy()))

    print('Determining useful nodes...')

    nodes_gdf = nodes_gdf.drop(nodes_gdf[~nodes_gdf['id'].isin(used_nodes)].index).reset_index(drop=True)

    # vertex with id XXXXX is indexed at 0, with id YYYYY is indexed at 1 ...
    vertex_ids = pd.Series(np.arange(nodes_gdf.shape[0]), index=nodes_gdf['id'], name='index')
    vertex_map = vertex_ids.to_dict()


    print('Mapping columns...')
    for key, value in zip(('u', 'v'), ('s', 't')):
        edges_gdf[value] = edges_gdf[key].map(vertex_map)

    # since for this case we do not require a detailed analysis, 
    # we will be dropping edges for which nodes are unreferenced
    edges_gdf = edges_gdf.dropna().reset_index(drop=True)

    print(edges_gdf.head(2))

    
    
    edge_list = edges_gdf[['s', 't']].astype('int').to_records(index=False)


    graph = gt.Graph(directed=True)

    # add all nodes
    vertices = graph.add_vertex(n=nodes_gdf.shape[0])

    if 'node_index' in nodes_gdf.columns:
        nodes_gdf = nodes_gdf.drop('node_index', axis=1)

    print(nodes_gdf)
    
    nodes_gdf = nodes_gdf[node_vars].reset_index(names='node_index', drop=False)
    vprops = nodes_gdf.dtypes

    print(f"Adding node properties {vprops.keys().tolist()}...")
    for key, value in vprops.items():
        if key == 'geometry':
            continue
            
        graph.vertex_properties[key] = graph.new_vertex_property(dtype_mapping[value.name], vals=nodes_gdf[key].to_numpy())

    print('Adding edges...')
    graph.add_edge_list(edge_list.tolist(), hashed=False)

    eprops = edges_gdf.dtypes
    
    print(f"Adding edge properties {eprops.keys().tolist()}...")
    for key, value in eprops.items():
        if key in ('highway', 'geometry'):
            continue

        graph.edge_properties[key] = graph.new_edge_property(dtype_mapping[value.name], vals=edges_gdf[key].to_numpy())
    
    return graph, nodes_gdf, edges_gdf


def keep_lcc(graph, nodes_gdf, edges_gdf, node_vars, edge_vars):
    """

    """
    comps, hist = graph_tool.topology.label_components(graph, directed=False)
    lcc_idx = np.argmax(hist)

    components = pd.Series(comps)
    histogram = pd.Series(hist)
    print(histogram.sort_values(ascending=False))

    nodes_gdf['component'] = components

    # keep only nodes in the lcc
    nodes_gdf = nodes_gdf.drop(components[components != lcc_idx].index)

    
    node_ids = nodes_gdf['id']

    # drop edges that reference nodes outside of the lcc
    condition = ~(edges_gdf['u'].isin(node_ids) & edges_gdf['v'].isin(node_ids))

    edges_gdf = edges_gdf.drop(condition[condition].index)


    return get_graph(nodes_gdf, edges_gdf, node_vars, edge_vars)


def connect_components(graph, nodes_gdf, edges_gdf, node_vars, edge_vars, crs):
    """
    Connect every relevant component of the road network graph to the LCC.
    """
    comps, hist = graph_tool.topology.label_components(graph, directed=False)
    lcc_idx = np.argmax(hist)

    components = pd.Series(comps)
    histogram = pd.Series(hist)
    print(histogram.sort_values(ascending=False))


    nodes_gdf['component'] = components
    
    # drop components of size one
    one_sized = histogram[histogram == 1].index

    print('Dropping one-sized components...')
    nodes_gdf = nodes_gdf.drop(nodes_gdf[nodes_gdf['component'].isin(one_sized)].index, axis=0)

    
    lcc_nodes = nodes_gdf[nodes_gdf['component'] == lcc_idx]

    proj_lcc = lcc_nodes.to_crs(crs)

    fake_edge_pairs = []
    for key, group in tqdm.tqdm(nodes_gdf.groupby('component'), desc='component'):
        if key == lcc_idx:
            continue

        proj_component = group.to_crs(crs)

        closest_nodes = proj_component.sjoin_nearest(proj_lcc, how='left', distance_col='distance')
        closest_pair_idx = closest_nodes['distance'].idxmin()

        closest_pair = closest_nodes.loc[closest_pair_idx]

        fake_edge_pairs.append((closest_pair['node_index_left'], closest_pair['node_index_right'], closest_pair['distance']))
        fake_edge_pairs.append((closest_pair['node_index_right'], closest_pair['node_index_left'], closest_pair['distance']))


    print(len(fake_edge_pairs))
    fake_edges = pd.DataFrame.from_records(fake_edge_pairs, columns=['s', 't', 'length'])

    fake_edges['u'] = fake_edges['s'].map(lambda x: nodes_gdf.iloc[x]['id'])
    fake_edges['v'] = fake_edges['t'].map(lambda x: nodes_gdf.iloc[x]['id'])

    print(fake_edges.head(2))

    
    fake_edges['geometry'] = fake_edges.apply(
        lambda x: shapely.geometry.LineString(nodes_gdf.iloc[x['s']]['geometry'], nodes_gdf.iloc[x['t']]['geometry']), axis=1
    )

    print(fake_edges.head(2))
    
    print()
    print(edges_gdf.head(2))
    
    input('break')

    
    return


def save_graph(graph, savedir, savefile):

    os.makedirs(savedir, exist_ok=True)

    try:
        os.remove(os.path.join(savedir, savefile))

    except FileNotFoundError:
        pass

    
    return graph.save(os.path.join(savedir, savefile))



def main():
    date = '250905'

    savedir = '/data/big/fmalveiro/complexity72/'
    elements_zip = 'DEFAULT-road_network_elements.zip'

    crs = 'epsg:20539'
    tweak_graph = 'lcc'

    loadpath = os.path.join('/data/big/fmalveiro/complexity72', elements_zip)

    print('Loading nodes...')
    nodes_gdf = gpd.read_file(f"{loadpath}!somalia-{date}-nodes.geojson")

    print('Loading edges...')
    edges_gdf = gpd.read_file(f"{loadpath}!somalia-{date}-edges.geojson")

    print(f"There are {nodes_gdf.shape[0]} nodes and {edges_gdf.shape[0]} edges.")

    node_vars = nodes_gdf.columns
    edge_vars = ['u', 'v', 'length', 'highway', 'geometry']

    print('Getting the graph...')
    graph, nodes_gdf, edges_gdf = get_graph(nodes_gdf, edges_gdf, node_vars, edge_vars)
    
    print(f"Halfway through, there are {nodes_gdf.shape[0]} nodes and {edges_gdf.shape[0]} edges.")
    print(graph)


    if tweak_graph == 'lcc':
        print('Keeping only LCC...')
        graph, nodes_gdf, edges_gdf = keep_lcc(graph, nodes_gdf, edges_gdf, node_vars, edge_vars)
    elif tweak_graph == 'connect':
        print('Connecting disconnected components...')
        graph, nodes_gdf, edges_gdf = connect_components(graph, nodes_gdf, edges_gdf, node_vars, edge_vars, crs)
    elif tweak_graph is not None:
        raise ValueError(tweak_graph)

    
    print(f"Finally, there are {nodes_gdf.shape[0]} nodes and {edges_gdf.shape[0]} edges left.")

    print('Saving the graph...')
    save_graph(graph, savedir, 'somalia-road_network_graph.gt.gz')

    with tempfile.TemporaryDirectory() as tmpdir:
        for element, gdf in zip(('nodes', 'edges'), (nodes_gdf, edges_gdf)):
            gdf.to_file(os.path.join(tmpdir, f"somalia-{date}-{element}.geojson"))

        # zipfile does not overwrite, we must save again
        savepath = os.path.join(savedir, elements_zip.replace('DEFAULT-', ''))
        if os.path.exists(savepath):
            os.remove(savepath)
        
        with zipfile.ZipFile(savepath, 'w') as zfile:
            for element, gdf in zip(('nodes', 'edges'), (nodes_gdf, edges_gdf)):
                loadfile = f"somalia-{date}-{element}.geojson"
                loadpath = os.path.join(tmpdir, loadfile)

                print(f"Zipping {element}...")
                zfile.write(loadpath, arcname=loadfile)
    
    return



if __name__ == '__main__':
    main()
