#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import pandas as pd
import geopandas as gpd

dir_app = os.path.dirname(sys.argv[0])

dir_graph = os.path.join(dir_app, 'osm_graph.gpkg')
dir_edges_pkl = os.path.join(dir_app, 'osm_edges.pkl')
dir_nodes_pkl = os.path.join(dir_app, 'osm_nodes.pkl')

if not os.path.exists(dir_graph):
    print ("Graph File does not exist")
    sys.exit(1)

#Create Pickle file
pickle_edges_file = open(dir_edges_pkl, 'wb') 
pickle_nodes_file = open(dir_nodes_pkl, 'wb')

gdf_edges = gpd.read_file(dir_graph, layer='edges') #read the graph file
gdf_edges.to_crs(epsg=4326, inplace=True) #set the coordinate reference system
gdf_nodes = gpd.read_file(dir_graph, layer='nodes') 
gdf_nodes.to_crs(epsg=4326, inplace=True) 

data = {
    "edges": gdf_edges,
    "nodes": gdf_nodes
}

# Important: Pickle the dataframes
pickle.dump(data['edges'], pickle_edges_file) #pickle the dataframe
pickle_edges_file.close() #close file
pickle.dump(data['nodes'], pickle_nodes_file) #pickle the dataframe
pickle_nodes_file.close() #close file

print ("Pickle file created successfully")








# Test Read Pickle file
#test_edges = pd.read_pickle(dir_edges_pkl) #read the pickle file
#test_nodes = pd.read_pickle(dir_nodes_pkl) #read the pickle file
#print (test_nodes)










