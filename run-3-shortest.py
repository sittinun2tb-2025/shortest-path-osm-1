#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import params
import osmnx as ox
from shapely import Point, LineString
import pandas as pd
import geopandas as gpd

dir_output_gpkg = os.path.join(params.dir_app, 'osm_output_shortest.gpkg')

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


# Create Route shortest path GeoDataFrame
route = ox.shortest_path(graph, params.osmid_u, params.osmid_end, weight='length')
obj_route_geom = LineString([ ds for ds in [Point(graph.nodes[i]['x'], graph.nodes[i]['y']) for i in route] ])
gdf_route = gpd.GeoDataFrame(geometry=[obj_route_geom], crs="EPSG:4326")
#print (gdf_route)

# Combine all segments into a Output.gpkg
gdf_route.set_crs(epsg=4326, inplace=True)
gdf_route.to_file(dir_output_gpkg, layer='osm_shortest', driver='GPKG')
