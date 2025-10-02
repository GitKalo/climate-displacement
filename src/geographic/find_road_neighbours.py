import geopandas as gpd
import libpysal as lp
import pandas as pd
import numpy as np

import tqdm
import os



def borders(geom1, geom2):
    return geom1.intersection(geom2)



def main():
    to_crs = 'epsg:20539'
    loaddir = '/data/big/fmalveiro/complexity72/'
    savedir = './data/'

    adm_level = 2
    adm_loadpath = os.path.join(savedir, f"gadm41_SOM_{adm_level}.json.zip")
    edges_loadpath = os.path.join(loaddir, 'road_network_elements.zip!somalia-250905-edges.geojson')

    print('Loading adm gdf...')
    adm_gdf = gpd.read_file(adm_loadpath)

    print('Loading edges gdf...')
    edges_gdf = gpd.read_file(edges_loadpath)

    print('Projecting adm gdf...')
    proj_adm = adm_gdf.to_crs(to_crs)

    print('Projecting edges gdf...')
    proj_edges = edges_gdf.to_crs(to_crs)

    print('Finding Queen weights...')
    queen = lp.weights.Queen.from_dataframe(proj_adm, use_index=False)

    # because there were too many mistakes with the spelling...
    adjlist = queen.to_adjlist(drop_islands=False).rename({'neighbor': 'neighbour'}, axis=1)
    for column in ('focal', 'neighbour'):
        adjlist[column] = adjlist[column].astype(int)

    print('Finding border geometries...')
    tqdm.tqdm.pandas(desc='borders')
    intersections = adjlist.progress_apply(lambda x: 
        borders(
            proj_adm.iloc[int(x['focal'])]['geometry'], 
            proj_adm.iloc[int(x['neighbour'])]['geometry']
        ), axis=1)
    
    intersections = gpd.GeoSeries(intersections, crs=to_crs)
    intersections.index = pd.MultiIndex.from_arrays((adjlist['focal'], adjlist['neighbour']))


    print('Finding road intersections...')
    # here we refine the list of neighbours
    # from geographical neighbours to 'road network' neighbours
    road_intersects = {key: proj_edges['geometry'].intersects(border).any() 
                       for key, border in tqdm.tqdm(intersections.items(), total=len(intersections))
                      }
    road_intersects = pd.Series(road_intersects)

    print('Refining neighbours list...')
    # we only want to keep those through which a road goes through
    # so we drop those for which it does not happen
    filtered_idxs = np.concatenate(np.argwhere(~road_intersects))
    road_adjlist = adjlist.drop(filtered_idxs, axis=0).reset_index(drop=True)

    road_adjlist = road_adjlist.rename({'weight': 'road_connected'}, axis=1)

    print('Saving to file...')
    road_adjlist.to_csv(os.path.join(savedir, 'geographical_neighbours.csv'), index=False)
    return



if __name__ == '__main__':
    main()
