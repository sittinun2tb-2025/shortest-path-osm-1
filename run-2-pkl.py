#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import geopandas as gpd

dir_app = os.path.dirname(os.path.abspath(__file__))


dir_graph = os.path.join(dir_app, 'osm_graph.gpkg')
dir_edges_pkl = os.path.join(dir_app, 'osm_edges.pkl')
dir_nodes_pkl = os.path.join(dir_app, 'osm_nodes.pkl')

dir_flood     = os.path.join(dir_app, 'flood-1.gpkg')
dir_flood_pkl = os.path.join(dir_app, 'flood-1.pkl')

if not os.path.exists(dir_graph):
    print ("Graph File does not exist")
    sys.exit(1)

if not os.path.exists(dir_flood):
    print ("Flood File does not exist")
    sys.exit(1)

gdf_edges = gpd.read_file(dir_graph, layer='edges') #read the graph file
gdf_edges.to_crs(epsg=4326, inplace=True) #set the coordinate reference system
with open(dir_edges_pkl, 'wb') as f:
    pickle.dump(gdf_edges, f)

gdf_nodes = gpd.read_file(dir_graph, layer='nodes')
gdf_nodes.to_crs(epsg=4326, inplace=True)
with open(dir_nodes_pkl, 'wb') as f:
    pickle.dump(gdf_nodes, f)

gdf_flood = gpd.read_file(dir_flood, layer='flood1') # flood1 is the layer name in the gpkg file
gdf_flood.to_crs(epsg=4326, inplace=True)
with open(dir_flood_pkl, 'wb') as f:
    pickle.dump(gdf_flood, f)

print ("Pickle file created successfully")