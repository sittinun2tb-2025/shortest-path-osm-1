# run-1-graph.py

import os
import osmnx as ox
import params

# Create output file
graph_file = os.path.join(params.dir_app, 'osm_graph.gpkg')

graph = ox.graph_from_point( 
    (params.centroid[1], params.centroid[0]), # lat, lon 
    dist=params.buffer_distance,  #units of meters
    network_type='drive',
    simplify=False
) 

# Simplify the graph
graph = ox.simplify_graph(graph, edge_attrs_differ=["osmid"])

# Convert graph to GeoDataFrame
gdf_nodes, gdf_edges = ox.graph_to_gdfs(graph)

gdf_nodes.to_file(graph_file, layer='nodes', driver='GPKG')
gdf_edges.to_file(graph_file, layer='edges', driver='GPKG')

print ("Graph saved to: %s -: %s" % (graph_file, os.path.exists(graph_file)))
