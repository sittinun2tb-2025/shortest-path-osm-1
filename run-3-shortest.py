#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import networkx as nx
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

import params

sys.stdout.reconfigure(encoding='utf-8')

dir_edges_pkl   = os.path.join(params.dir_app, 'osm_edges.pkl')
dir_nodes_pkl   = os.path.join(params.dir_app, 'osm_nodes.pkl')
dir_output_gpkg = os.path.join(params.dir_app, 'osm_output_shortest.gpkg')

obj_edges = pd.read_pickle(dir_edges_pkl)
obj_nodes = pd.read_pickle(dir_nodes_pkl)

# สร้าง directed graph จาก pkl
G = nx.DiGraph()
for _, row in obj_nodes.iterrows():
    G.add_node(int(row['osmid']), x=row['geometry'].x, y=row['geometry'].y)
for _, row in obj_edges.iterrows():
    G.add_edge(int(row['u']), int(row['v']), length=float(row['length']))

# หาเส้นทางสั้นที่สุด (Dijkstra)
route      = nx.shortest_path(G, params.osmid_u, params.osmid_end, weight='length')
total_dist = nx.shortest_path_length(G, params.osmid_u, params.osmid_end, weight='length')

# สร้าง geometry จาก node coordinates
coords     = [(G.nodes[n]['x'], G.nodes[n]['y']) for n in route]
route_geom = LineString(coords)

gdf_route = gpd.GeoDataFrame(
    [{'total_distance_m': round(total_dist, 2), 'num_nodes': len(route)}],
    geometry=[route_geom],
    crs='EPSG:4326'
)
gdf_route.to_file(dir_output_gpkg, layer='osm_shortest', driver='GPKG')

print(f"เส้นทางสั้นที่สุด: {params.osmid_u} -> {params.osmid_end}")
print(f"จำนวน node ที่ผ่าน: {len(route)} จุด")
print(f"ระยะทางรวม: {round(total_dist, 2)} เมตร")
print(f"บันทึกไฟล์: {dir_output_gpkg}")
