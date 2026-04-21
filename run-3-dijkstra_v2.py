#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import pandas as pd
import geopandas as gpd
import heapq

import params

sys.stdout.reconfigure(encoding='utf-8')


dir_edges_pkl = os.path.join(params.dir_app, 'osm_edges.pkl')
dir_nodes_pkl = os.path.join(params.dir_app, 'osm_nodes.pkl')

# Create output file
dir_output_gpkg = os.path.join(params.dir_app, 'osm_output.gpkg')

obj_edges = pd.read_pickle(dir_edges_pkl) #read the pickle file
obj_nodes = pd.read_pickle(dir_nodes_pkl) #read the pickle file
#print (obj_nodes)

def Find_NodeID_Connect(edges, node_id):
    """ ผลลัพธ์ อาจไม่มี osmid ที่ไม่สามารถเดินทางไปยังจุดหมายได้ 
        เช่น osmid ที่เป็น dead end หรือ มีทางเดียว one way
    """
    # Find the node_id in the 'u' and 'v' columns of the edges dataframe
    #connected_edges = edges[(edges['u'] == node_id) | (edges['v'] == node_id)]
    conn_edges = edges[(edges['u'] == node_id)]
    # select the edge with the minimum length
    #conn_edges = conn_edges[ conn_edges['length'] == conn_edges['length'].min() ]
    return conn_edges


# osmid start
osmid_u = params.osmid_u
osmid_v = 0
# osmid end
osmid_end = params.osmid_end

# Begin distances with infinity
list_nodes = obj_nodes['osmid'].tolist() # List of node IDs

#ds_connected = Find_NodeID_Connect(obj_edges, osmid_u)
#print (ds_connected) # u to many v

list_nodes_conn = Find_NodeID_Connect(obj_edges, osmid_u)[['v', 'length']].values.tolist() # List of node IDs that are connected to osmid_u
list_nodes_conn = [(int(v), float('{:.2f}'.format(length))) for v, length in list_nodes_conn]
#print ("Node-ID %s connect to %s" % (osmid_u, list_nodes_conn))

# DEFUALT VALUE
# 1) list node v (vertex) all network
# 2) add column status=False (defualt)
# 3) add column distance="inf" (defualt)
# 4) add column count=-1 (defualt)

df_nodes = pd.DataFrame({
    'v': list_nodes, 
    'status': False,
    'distance': float('inf'),
    'count': -1
    })

dist_m = 0.0
num_path = 1

# ── Dijkstra ─────────────────────────────────────────────────────────────────
priority_queue = [(0.0, osmid_u)]          # (cumulative_cost, node)
visited       = set()
dist_map      = {int(n): float('inf') for n in list_nodes}
dist_map[osmid_u] = 0.0
prev_map      = {}                         # predecessor ของแต่ละ node
result_rows   = []
step          = 0

while priority_queue:
    curr_cost, curr_node = heapq.heappop(priority_queue)

    if curr_node in visited:
        continue

    visited.add(curr_node)
    step += 1

    conn = Find_NodeID_Connect(obj_edges, curr_node)[['u', 'v', 'length']].values.tolist()

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
                prev_map[v] = u            # บันทึก predecessor เมื่อพบเส้นทางสั้นกว่า
                heapq.heappush(priority_queue, (new_cost, v))
            result_rows.append({'u': u, 'v': v, 'distance': length,
                                 'status': 'T', 'count_section': step})

    if curr_node == osmid_end:
        break

df_result = pd.DataFrame(result_rows, columns=['u', 'v', 'distance', 'status', 'count_section'])

# ── Print table ───────────────────────────────────────────────────────────────
print(df_result.to_string(index=False))

# ── Path reconstruction จาก prev_map ─────────────────────────────────────────
path = []
node = osmid_end
while node in prev_map:
    path.append(node)
    node = prev_map[node]
path.append(osmid_u)
path.reverse()

# ดึง distance ของแต่ละ edge บนเส้นทางจาก df_result
path_rows = []
for i in range(len(path) - 1):
    u_node = path[i]
    v_node = path[i + 1]
    edge = df_result[(df_result['u'] == u_node) & (df_result['v'] == v_node)]
    dist_edge = edge['distance'].values[0] if len(edge) > 0 else float('nan')
    path_rows.append({'order': i + 1, 'vertex': u_node, 'next_vertex': v_node, 'edge_distance': dist_edge})

path_rows.append({'order': len(path), 'vertex': path[-1], 'next_vertex': '-', 'edge_distance': 0.0})
df_path = pd.DataFrame(path_rows)

total_dist = round(dist_map.get(osmid_end, float('nan')), 2)

# ── Print path ────────────────────────────────────────────────────────────────
print("\n" + "="*60)
print(f"เส้นทางสั้นที่สุด: {osmid_u} -> {osmid_end}")
print(f"จำนวน vertex ที่ผ่าน: {len(path)} จุด (รวมต้นทางและปลายทาง)")
print(f"ระยะทางรวม: {total_dist} เมตร")
print("="*60)
print(df_path.to_string(index=False))
print("="*60)

















