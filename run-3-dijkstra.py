#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import pickle
import pandas as pd
import geopandas as gpd

import params


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
# osmid end
osmid_end = params.osmid_end


node_order = [osmid_u]
osmid_v = 0

dict_finding_path = {
    'origin': None,
    'destinate': [None],
    'count_path': 0,
    'sum_length': 0.0
}

list_finding_path = []  


while 1:
    # Check if the destination node is end point
    if osmid_u == osmid_end:
        break

    # Find connected edges from the current node
    ds_edges = Find_NodeID_Connect(obj_edges, osmid_u)
    
    # origin node
    dict_finding_path['origin'] = osmid_u

    if ds_edges.empty:
        break
    
    # find node is connected to destination node
    for idx, row in ds_edges.iterrows():
        # Check node v is already in list
        if row['v'] in node_order:
            continue
        # Next node
        osmid_v = row['v']
        print ("Test: %s -> %s, Length: %s" % (osmid_u, osmid_v, row['length']))

    # switch node
    osmid_u = osmid_v

    # update path information
    dict_finding_path['destinate'] = osmid_v
    dict_finding_path['sum_length'] += row['length']
    dict_finding_path['count_path'] += 1
    list_finding_path.append(dict_finding_path.copy())

    # Check if the node is already in list
    if osmid_u not in node_order:
        node_order.append(osmid_u)
    else:
        break

#print ("Node order: %s" % node_order)

df = pd.DataFrame(list_finding_path)
print(df)




# Check if the destination node is End Point
if osmid_u != osmid_end:
    print ("No path found from %s to %s" % (osmid_u, osmid_end))

# Calculate path by osmid
s_u = 0
s_v = 0
list_segment = []

for i in node_order:
    if s_u == 0:
        s_u = i
        continue
    s_v = i
    #print ("Path: %s -> %s" % (s_u, s_v))
    segment = obj_edges[(obj_edges['u'] == s_u) & (obj_edges['v'] == s_v)]
    #print (segment[['osmid', 'u', 'v', 'length', 'oneway', 'geometry']])
    list_segment.append(segment)
    s_u = s_v   

# Combine all segments into a Output.gpkg
df_segment = pd.concat(list_segment, ignore_index=True)
gdf_segment = gpd.GeoDataFrame(df_segment, geometry='geometry')
gdf_segment.set_crs(epsg=4326, inplace=True)
gdf_segment.to_file(dir_output_gpkg, layer='segments', driver='GPKG')














# while num < count:  
#     edges_to_node = Find_NodeID_Connect(obj_edges, osmid_start) 
#     print (edges_to_node[['u', 'v', 'length', 'oneway']]) 
    
#     for index, row in edges_to_node.iterrows():
#         if osmid_end == row['v']:
#             osmid = osmid_end
#             break
        
#         osm_next = row['v']
#         print ("START: %s -> NEXT: %s" % (osmid_start, osm_next))

#     osmid_start = osm_next
#     num += 1    


# edges_to_node['v'].values[0]


#while True:
#    edges_to_node = Find_NodeID_Connect(obj_edges, osmid_start) 
#    print (edges_to_node[['u', 'v', 'length', 'oneway']]) 



#edges_to_node = Find_NodeID_Connect(obj_edges, osmid_start) 
#print (edges_to_node[['u', 'v', 'length', 'oneway']]) 

#edges_to_start = edges_to_node[edges_to_node['u'] == osmid_start] # Find edges where 'u' is the node_id
#print (edges_to_start[['u', 'v', 'length', 'oneway']]) 

#osmid_start = edges_to_start['v'].values[0] # Get the 'v' value from the first row of edges_to_start
#print (osmid_start)

#edges_to_node = Find_NodeID_Connect(obj_edges, osmid_start) 
#print (edges_to_node[['u', 'v', 'length', 'oneway']])


#if __name__ == "__main__":
#    pass
