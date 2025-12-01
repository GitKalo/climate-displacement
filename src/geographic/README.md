Descritpion and running order follows. It is assumed that administrative level 2 units are used.


`download_osm_data.py`: downloads OSM data from [`GeoFabrik`](https://download.geofabrik.de/). Creates zip file `osm_data.zip`, where OSM data will be stored. Creates file `somalia-{date}.osm.pbf` within the said zip file, where `date` is a string 'YYMMDD'. File (_i.e._, date) should be available to download on GeoFabrik website.


`filter_osm_data.py`: generates a `osm.pbf` file with data relative to the road network, out of the file containing all OSM data. Creates file `somalia-{date}-highways.osm.pbf`, saved within `osm_data.zip`.


`extract_road_network_elements.py`: extracts the elements of the road network out of the `somalia-{date}-highways.osm.pbf`. Creates zip file `DEFAULT-road_network_elements.zip`. Within it, it stores `somalia-{date}-{element}.geojson`, where `element \in {nodes, edges}`.


`extract_buildings.py`: extracts buildings from OSM data contained in `somalia-{date}.osm.pbf`. Saves data in `somalia-{date}-buildings.osm.pbf`, within `osm_data.zip`.


`simplify_road_network.py`: uses `neatnet` to simplify the road network. Creates `f"somalia-{date}-{element}_simplified.geojson"`, for `element` in `(nodes, edges)`. Files are saved within `road_network_elements.zip`.


`construct_road_network_graph.py`: constructs the graph of the road network using the extracted elements in `DEFAULT-road_network_elements.zip` -- edges correspond to road segments; nodes  link road segments. As it is set, it only keeps the Largest Connected Component (LCC) of the road network graph. Creates file `somalia-road_network_graph.gt.gz` and `road_network_elements.zip`.


`find_road_neighbours.py`: given a geodataframe with administrative units (downloaded from [`gadm`](https://gadm.org/download_country.html)), finds the pairs of administrative units for which there can be a path through the (undirected) road network between them. Uses the road network represented by `somalia-road_network_graph.gt.gz` and the road network nodes stored in `road_network_elements.zip!nodes.geojson`. Creates file `geographical_neighbours.csv`.


`get_geographical_weights.py`: finds the cost (distance) of the shortest path through the road network between the centroids of every two administrative units that are adjacent (through the road network). Updates `geographical_neighbours.csv`. For each pair of neighbouring administrative units, information relative to their distance to and through the road network is saved. Namely, given a pair `(src, tgt)`, representing the fact that `src` is adjacent to `tgt` through the road network, the following information is saved:


- `road_connected`: indicator that `src` and `tgt` are adjacent.
- `src_vx`: index of the road network node which is the closest to the centroid of `src`. The node is indexed in `road_network_elements.zip!nodes.geojson`.
- `tgt_vx`: index of the road network node which is the closest to the centroid of `tgt`. The node is indexed in `road_network_elements.zip!nodes.geojson`.
- `src_distance`: distance, in metres, from `src` to its closest node of the road network. Distance is computed as the length of the straight line linking the centroid of `src` to its closest node on the road network.
- `tgt_distance`: distance, in metres, from `tgt` to its closest node of the road network. Distance is computed as the length of the straight line linking the centroid of `tgt` to its closest node on the road network.
- `in_distance`: distance, in metres, between the two aforementioned nodes of the road network. Distance is obtained from computing the shortest path in the road network between them.
- `road_distance`: distance, in metres, from the centroid of `src` to the centroid of `tgt`. Corresponds to `src_distance + in_distance + tgt_distance`.


In `geographical_neighbours.csv`, `focal` and `neighbour` correspond to `src` and `tgt`, respectively. Administrative units are numbered with the index in which they appear on the file obtained from `gadm`.