#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import heapq
import pandas as pd
import geopandas as gpd

import params

sys.stdout.reconfigure(encoding='utf-8')

# ── โหลดข้อมูล ────────────────────────────────────────────────────────────────
dir_edges_pkl = os.path.join(params.dir_app, 'osm_edges.pkl')
dir_nodes_pkl = os.path.join(params.dir_app, 'osm_nodes.pkl')
dir_flood     = os.path.join(params.dir_app, 'flood-1.gpkg')

obj_edges = pd.read_pickle(dir_edges_pkl)
obj_nodes = pd.read_pickle(dir_nodes_pkl)
flood_gdf = gpd.read_file(dir_flood)

# ── หา edges ที่ถูกน้ำท่วมปิดกั้น ────────────────────────────────────────────
edges_gdf     = gpd.GeoDataFrame(obj_edges, geometry='geometry', crs='EPSG:4326')
flooded_edges = gpd.sjoin(edges_gdf, flood_gdf[['geometry']], how='inner', predicate='intersects')
blocked_pairs = set(zip(flooded_edges['u'].astype(int), flooded_edges['v'].astype(int)))

print("=" * 60)
print("Edges ที่ถูกน้ำท่วมปิดกั้น:")
print(flooded_edges[['u', 'v', 'length']].to_string(index=False))
print("=" * 60)

# ── ฟังก์ชันหา edges ที่เชื่อมต่อ (ยกเว้น blocked) ───────────────────────────
def Find_NodeID_Connect(edges, node_id, blocked=set()):
    conn = edges[edges['u'] == node_id]
    conn = conn[~conn.apply(lambda r: (int(r['u']), int(r['v'])) in blocked, axis=1)]
    return conn

# ── ค่าเริ่มต้น ───────────────────────────────────────────────────────────────
osmid_u   = params.osmid_u
osmid_end = params.osmid_end
list_nodes = obj_nodes['osmid'].tolist()

# ── Dijkstra (หลีกเลี่ยง flooded edges) ──────────────────────────────────────
priority_queue = [(0.0, osmid_u)]
visited        = set()
dist_map       = {int(n): float('inf') for n in list_nodes}
dist_map[osmid_u] = 0.0
prev_map       = {}
result_rows    = []
step           = 0

while priority_queue:
    curr_cost, curr_node = heapq.heappop(priority_queue)

    if curr_node in visited:
        continue

    visited.add(curr_node)
    step += 1

    conn = Find_NodeID_Connect(obj_edges, curr_node, blocked_pairs)[['u', 'v', 'length']].values.tolist()

    for u, v, length in conn:
        u      = int(u)
        v      = int(v)
        length = round(float(length), 2)

        if v in visited:
            result_rows.append({'u': u, 'v': v, 'distance': length,
                                 'status': 'F', 'count_section': 0})
        else:
            new_cost = curr_cost + length
            if new_cost < dist_map.get(v, float('inf')):
                dist_map[v] = new_cost
                prev_map[v] = u
                heapq.heappush(priority_queue, (new_cost, v))
            result_rows.append({'u': u, 'v': v, 'distance': length,
                                 'status': 'T', 'count_section': step})

    if curr_node == osmid_end:
        break

df_result = pd.DataFrame(result_rows, columns=['u', 'v', 'distance', 'status', 'count_section'])

# ── Print ตาราง Dijkstra ──────────────────────────────────────────────────────
print("\nตาราง Dijkstra (flood detour):")
print(df_result.to_string(index=False))

# ── Path reconstruction ───────────────────────────────────────────────────────
path = []
node = osmid_end
while node in prev_map:
    path.append(node)
    node = prev_map[node]
path.append(osmid_u)
path.reverse()

path_rows = []
for i in range(len(path) - 1):
    u_node = path[i]
    v_node = path[i + 1]
    edge      = df_result[(df_result['u'] == u_node) & (df_result['v'] == v_node)]
    dist_edge = edge['distance'].values[0] if len(edge) > 0 else float('nan')

    # ดึง geometry LINESTRING จาก osm_edges
    geom_row  = obj_edges[(obj_edges['u'] == u_node) & (obj_edges['v'] == v_node)]
    geometry  = geom_row['geometry'].values[0] if len(geom_row) > 0 else None

    path_rows.append({'order': i + 1, 'vertex': u_node,
                      'next_vertex': v_node, 'edge_distance': dist_edge,
                      'geometry': geometry})

df_path = gpd.GeoDataFrame(path_rows, geometry='geometry', crs='EPSG:4326')

total_dist = round(dist_map.get(osmid_end, float('nan')), 2)

# ── Print เส้นทาง ─────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print(f"เส้นทางเลี่ยงน้ำท่วม: {osmid_u} -> {osmid_end}")
print(f"จำนวน vertex ที่ผ่าน: {len(path)} จุด (รวมต้นทางและปลายทาง)")
print(f"ระยะทางรวม: {total_dist} เมตร")
print("=" * 60)
print(df_path[['order', 'vertex', 'next_vertex', 'edge_distance', 'geometry']].to_string(index=False))
print("=" * 60)

# ── บันทึก GeoPackage ─────────────────────────────────────────────────────────
dir_output = os.path.join(params.dir_app, 'osm_flood_detour.gpkg')
df_path.to_file(dir_output, layer='flood_detour', driver='GPKG')
print(f"\nบันทึกไฟล์: {dir_output}")
