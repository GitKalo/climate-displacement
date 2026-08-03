import csv
import geopandas as gpd

# Load GADM dataset
gdf_gadm = gpd.read_file('data/gadm41_SOM_2.json.zip')
gdf_gadm = gdf_gadm.to_crs('epsg:20539') # centroids are obtained with more accuracy using a projected CRS
gdf_gadm['centroid'] = gdf_gadm.centroid

f = csv.writer(open('data/geo_labels_gadm.csv', 'w'))
for idx, row in gdf_gadm.iterrows():
    f.writerow([idx, row['NAME_2']])