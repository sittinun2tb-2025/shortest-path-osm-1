#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Generate images for README: workflow diagram and route map."""

import os
import sys
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import geopandas as gpd
import pandas as pd
import numpy as np

import params

out_dir = os.path.dirname(sys.argv[0]) or '.'
os.makedirs(os.path.join(out_dir, 'docs'), exist_ok=True)

# ── 1. Workflow Diagram ───────────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=(12, 4.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.5)
ax.axis('off')
fig.patch.set_facecolor('#F8F9FA')

STAGES = [
    ('Stage 1', 'rum-1-graph.py', 'Download\nOSM Road Network', '#2196F3', '#BBDEFB'),
    ('Stage 2', 'run-2-pkl.py',   'Convert GeoPackage\nto Pickle',       '#4CAF50', '#C8E6C9'),
    ('Stage 3', 'run-3-dijkstra.py', 'Dijkstra\nShortest Path',          '#FF9800', '#FFE0B2'),
    ('Stage 4', 'run-4-flood-detour.py', 'Flood Detour\nDijkstra',       '#F44336', '#FFCDD2'),
]

OUTPUTS = [
    'osm_graph.gpkg',
    'osm_edges.pkl\nosm_nodes.pkl',
    'osm_output.gpkg',
    'osm_flood_detour.gpkg',
]

BOX_W, BOX_H = 2.0, 1.4
Y_BOX   = 2.6
Y_OUT   = 0.7
X_START = 0.8
X_GAP   = 2.8

for i, ((stage, script, desc, color, light), output) in enumerate(zip(STAGES, OUTPUTS)):
    x = X_START + i * X_GAP

    # Stage box
    box = FancyBboxPatch((x, Y_BOX), BOX_W, BOX_H,
                         boxstyle='round,pad=0.08', linewidth=1.5,
                         edgecolor=color, facecolor=light)
    ax.add_patch(box)
    ax.text(x + BOX_W/2, Y_BOX + BOX_H - 0.22, stage,
            ha='center', va='top', fontsize=8.5, fontweight='bold', color=color)
    ax.text(x + BOX_W/2, Y_BOX + BOX_H/2 - 0.05, desc,
            ha='center', va='center', fontsize=8, color='#333333')
    ax.text(x + BOX_W/2, Y_BOX + 0.13, script,
            ha='center', va='bottom', fontsize=6.5, color='#666666',
            style='italic')

    # Output box
    out_box = FancyBboxPatch((x, Y_OUT), BOX_W, 0.85,
                              boxstyle='round,pad=0.06', linewidth=1,
                              edgecolor='#90A4AE', facecolor='#ECEFF1')
    ax.add_patch(out_box)
    ax.text(x + BOX_W/2, Y_OUT + 0.425, output,
            ha='center', va='center', fontsize=6.8, color='#37474F')

    # Arrow stage → output
    ax.annotate('', xy=(x + BOX_W/2, Y_OUT + 0.85),
                xytext=(x + BOX_W/2, Y_BOX),
                arrowprops=dict(arrowstyle='->', color='#546E7A', lw=1.5))

    # Arrow between stages
    if i < len(STAGES) - 1:
        ax.annotate('', xy=(x + BOX_W + 0.72, Y_BOX + BOX_H/2),
                    xytext=(x + BOX_W + 0.08, Y_BOX + BOX_H/2),
                    arrowprops=dict(arrowstyle='->', color='#546E7A', lw=1.8))

ax.text(6, 4.3, 'Workflow Pipeline: Shortest Path OSM',
        ha='center', va='top', fontsize=13, fontweight='bold', color='#263238')

plt.tight_layout(pad=0.3)
out_wf = os.path.join(out_dir, 'docs', 'workflow.png')
plt.savefig(out_wf, dpi=150, bbox_inches='tight', facecolor='#F8F9FA')
plt.close()
print(f'Saved: {out_wf}')

# ── 2. Route Map ──────────────────────────────────────────────────────────────

edges = pd.read_pickle(os.path.join(out_dir, 'osm_edges.pkl'))
nodes = pd.read_pickle(os.path.join(out_dir, 'osm_nodes.pkl'))

gdf_edges    = gpd.GeoDataFrame(edges, geometry='geometry', crs='EPSG:4326')
gdf_path     = gpd.read_file(os.path.join(out_dir, 'osm_output.gpkg'),       layer='dijkstra_v3')
gdf_detour   = gpd.read_file(os.path.join(out_dir, 'osm_flood_detour.gpkg'), layer='flood_detour')
gdf_flood    = gpd.read_file(os.path.join(out_dir, 'flood-1.gpkg'))

# Focus bbox on the paths + small padding
all_bounds = np.array([
    gdf_path.total_bounds,
    gdf_detour.total_bounds,
    gdf_flood.total_bounds,
])
minx = all_bounds[:, 0].min() - 0.004
miny = all_bounds[:, 1].min() - 0.003
maxx = all_bounds[:, 2].max() + 0.004
maxy = all_bounds[:, 3].max() + 0.003

fig, ax = plt.subplots(figsize=(11, 8))
fig.patch.set_facecolor('#E8EAF6')
ax.set_facecolor('#E3F2FD')

# Road network (clip to view)
gdf_edges_clip = gdf_edges.cx[minx:maxx, miny:maxy]
gdf_edges_clip.plot(ax=ax, color='#B0BEC5', linewidth=0.6, alpha=0.7, zorder=1)

# Flood zone
gdf_flood.plot(ax=ax, color='#EF5350', alpha=0.35, zorder=2, label='พื้นที่น้ำท่วม')
gdf_flood.boundary.plot(ax=ax, color='#B71C1C', linewidth=1.5, zorder=3)

# Shortest path
gdf_path.plot(ax=ax, color='#1565C0', linewidth=3.5, zorder=4,
              label=f'เส้นทางสั้นที่สุด (Dijkstra)')

# Flood detour
gdf_detour.plot(ax=ax, color='#2E7D32', linewidth=3.5, linestyle='--', zorder=5,
                label='เส้นทางเลี่ยงน้ำท่วม')

# Start / End markers
start_node = nodes[nodes['osmid'] == params.osmid_u]
end_node   = nodes[nodes['osmid'] == params.osmid_end]

for row, marker, color, label, offset in [
    (start_node, 'o', '#1B5E20', 'Start',  (-0.0012, 0.0006)),
    (end_node,   's', '#B71C1C', 'End',    ( 0.0008, 0.0006)),
]:
    if len(row):
        x0, y0 = float(row['x'].values[0]), float(row['y'].values[0])
        ax.plot(x0, y0, marker=marker, markersize=12, color=color,
                zorder=7, markeredgecolor='white', markeredgewidth=1.5)
        ax.text(x0 + offset[0], y0 + offset[1], label,
                fontsize=9, fontweight='bold', color=color, zorder=8,
                bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1.5))

ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_xlabel('Longitude', fontsize=9, color='#455A64')
ax.set_ylabel('Latitude',  fontsize=9, color='#455A64')
ax.set_title(f'Shortest Path & Flood Detour — Bangkok\n'
             f'(OSM Node: {params.osmid_u} → {params.osmid_end}  |  Buffer: {params.buffer_distance:,} m)',
             fontsize=11, fontweight='bold', color='#1A237E', pad=10)

# Grid
ax.grid(True, linestyle='--', linewidth=0.4, alpha=0.5, color='#78909C')
ax.tick_params(labelsize=8, colors='#455A64')
for spine in ax.spines.values():
    spine.set_edgecolor('#90A4AE')

# Legend
handles = [
    mpatches.Patch(facecolor='#B0BEC5', label='OSM Road Network'),
    mpatches.Patch(facecolor='#EF5350', alpha=0.5, edgecolor='#B71C1C', label='Flood Zone'),
    plt.Line2D([0], [0], color='#1565C0', linewidth=3, label='Shortest Path (Dijkstra)'),
    plt.Line2D([0], [0], color='#2E7D32', linewidth=3, linestyle='--', label='Flood Detour'),
    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#1B5E20',
               markersize=10, markeredgecolor='white', label='Start Node'),
    plt.Line2D([0], [0], marker='s', color='w', markerfacecolor='#B71C1C',
               markersize=10, markeredgecolor='white', label='End Node'),
]
ax.legend(handles=handles, loc='lower left', fontsize=8.5, framealpha=0.9,
          edgecolor='#90A4AE', facecolor='white')

# Scale note
ax.text(maxx - 0.0005, miny + 0.0004,
        '© OpenStreetMap contributors',
        ha='right', va='bottom', fontsize=7, color='#78909C', style='italic')

plt.tight_layout(pad=0.5)
out_map = os.path.join(out_dir, 'docs', 'route_map.png')
plt.savefig(out_map, dpi=150, bbox_inches='tight', facecolor='#E8EAF6')
plt.close()
print(f'Saved: {out_map}')
