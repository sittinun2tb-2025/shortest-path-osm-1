# rum-1-graph.py

import os
import sys
import json
from datetime import datetime, timezone
import numpy as np
#print ("Numpy Version: %s" % np.__version__)
import scipy
#print ("Scipy Version: %s" % scipy.__version__)
import osmnx as ox
#print ("Osmnx Version: %s" % ox.__version__)
import matplotlib.pyplot as plt

import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString, Point
from shapely.ops import transform

import pyproj
geod = pyproj.Geod(ellps="WGS84")

import params


#centroid = LineString([params.start_p, params.end_p]).interpolate(0.5, normalized=True).coords[0]

# Create output file
graph_file = os.path.join(params.dir_app, 'osm_graph.gpkg')

graph = ox.graph_from_point( 
    (params.centroid[1], params.centroid[0]), # lat, lon 
    dist=params.buffer_distance,  #units of meters
    network_type='drive',
    simplify=False, 
    #retain_all=False, 
    #truncate_by_edge=False, 
    #clean_periphery=None, 
    #custom_filter=None
) 

# Simplify the graph
graph = ox.simplify_graph(graph, edge_attrs_differ=["osmid"])

# Convert graph to GeoDataFrame
gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)
#gdf_edges = ox.graph_to_gdfs(graph, nodes=False, edges=True, node_geometry=True)

gdf_nodes.set_crs(epsg=4326, inplace=True)
gdf_edges.set_crs(epsg=4326, inplace=True)

gdf_nodes.to_file(graph_file, layer='nodes', driver='GPKG')
gdf_edges.to_file(graph_file, layer='edges', driver='GPKG')

print ("Graph saved to: %s -: %s" % (graph_file, os.path.exists(graph_file)))
