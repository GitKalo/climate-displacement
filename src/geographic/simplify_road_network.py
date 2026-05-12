import geopandas as gpd
import neatnet
import momepy

import tempfile
import zipfile
import os


def fill_information(nodes_gdf, edges_gdf):
    """
    New edge segments do not contain crucial attributes, e.g., length
    New nodes have an artificial nodeID, not an osmid:
    - new nodes may have been created, which do not exist in OSM data
    """

    # edge length most likely will have to be updated with 
    # simplified['edges'].to_crs('epsg:20539')['geometry'].length

    # the new attribute 'mm_len' should correspond to the updated length

    # the new edge dataframe contains attributes 
    # 'node_start', 'node_end', 'mm_len',
    # which should serve the same purpose as 's', 't', 'length'
    # in the original edge dataframe
    # names of the new dataframe should be adapted so that
    # the graph can be successfully built afterwards
    input('break')
    return


def main():
    date = '251124'

    savedir = '/data/big/fmalveiro/complexity72/'

    osm_zip = 'osm_data.zip'
    elements_zip = 'road_network_elements.zip'

    buildings_file = f"somalia-{date}-buildings.osm.pbf"

    from_crs = 'epsg:4326'
    to_crs = 'epsg:20539'

    elements = ('nodes', 'edges')


    loadpath = f"{os.path.join(savedir, osm_zip)}!{buildings_file}"
    buildings_gdf = gpd.read_file(loadpath)

    element_gdfs = {}
    for element in elements:
        loadfile = f"somalia-{date}-{element}.geojson"
        loadpath = f"{os.path.join(savedir, elements_zip)}!{loadfile}"

        print(f"Loading {element}...")
        element_gdfs[element] = gpd.read_file(loadpath)
    
    
    proj_buildings = buildings_gdf.to_crs(to_crs)
    proj_elements = {key: value.to_crs(to_crs) for key, value in element_gdfs.items()}

    simplified_elems = {}
    
    print('Simplifying edges...')
    simplified_elems['edges'] = neatnet.neatify(proj_elements['edges'], exclusion_mask=proj_buildings.geometry)

    # process sometimes gets killed
    # let us see if freeing out no-longer-needed memory helps somehow
    del element_gdfs
    del proj_elements

    print('Obtaining a graph out of simplified edges...')
    graph = momepy.gdf_to_nx(simplified_elems['edges'], approach='primal')

    print('Getting nodes and edges out of the simplified graph...')
    final_nodes, final_edges, sw = momepy.nx_to_gdf(
        graph, points=True, lines=True, spatial_weights=True
    )
    
    print(graph)
    print(f"Shape of nodes and edges gdfs: {final_nodes.shape[0]}, {final_edges.shape[0]}")
    
    reproj_elems = {key: value.to_crs(from_crs) for key, value in zip(elements, (final_nodes, final_edges))}

    del graph
    
    del final_nodes
    del final_edges

    final_nodes, final_edges = fill_information(final_nodes, final_edges)

    with tempfile.TemporaryDirectory() as tmpdir:

        for key, value in reproj_elems.items():
            savefile = f"somalia-{date}-{key}_simplified.geojson"
            tmppath = os.path.join(tmpdir, savefile)

            print(f"Saving to tmpdir {tmpdir}...")
            value.to_file(tmppath)

            savepath = os.path.join(savedir, elements_zip)

            with zipfile.ZipFile(savepath, 'a') as zfile:
                print(f"Zipping simplified {key}...")
                zfile.write(tmppath, arcname=savefile)

    return



if __name__ == '__main__':
    main()
