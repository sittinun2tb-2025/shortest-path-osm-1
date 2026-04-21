# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Stage 1 — download OSM road network (requires internet)
python rum-1-graph.py

# Stage 2 — convert GeoPackage to pickle (requires osm_graph.gpkg)
python run-2-pkl.py

# Stage 3 — Dijkstra shortest path
python run-3-dijkstra_v2.py

# Stage 4 — flood-aware detour
python run-4-flood-detour.py
```

All scripts must be run from the project root directory. `params.py` uses `os.path.dirname(sys.argv[0])` to resolve file paths, so working directory matters.

## Architecture

**Pipeline:** `rum-1-graph.py` → `run-2-pkl.py` → `run-3-dijkstra_v2.py` / `run-4-flood-detour.py`

**params.py** is the single config file. All scripts import it for `osmid_u`, `osmid_end`, `buffer_distance`, `centroid`, and `dir_app`.

**Data flow:**
- `rum-1-graph.py` downloads a drive network via `osmnx.graph_from_point()` centered on the midpoint of start/end, radius=500m, saves to `osm_graph.gpkg` (layers: `nodes`, `edges`)
- `run-2-pkl.py` reads `osm_graph.gpkg` and serializes both layers to pickle for fast loading in subsequent scripts
- Dijkstra scripts load `osm_edges.pkl` / `osm_nodes.pkl` and use `Find_NodeID_Connect(edges, node_id)` — a one-directional lookup (`u == node_id` only, respecting one-way streets)

**Dijkstra implementation (`run-3-dijkstra_v2.py`):**
- Uses `heapq` min-heap on `(cumulative_cost, node)`
- `prev_map[v] = u` is updated whenever a shorter path to `v` is found
- `step` counter (increments per finalized node) becomes `count_section` in the output table
- Output table columns: `u`, `v`, `distance` (edge length, not cumulative), `status` (`T`/`F`), `count_section`
- Status `F` with `count_section=0` means the neighbor was already finalized (back-edge)

**Flood detour (`run-4-flood-detour.py`):**
- Loads `flood-1.gpkg` (single MultiPolygon, EPSG:4326)
- Uses `gpd.sjoin(..., predicate='intersects')` to find blocked edge pairs
- `blocked_pairs` is a `set` of `(u, v)` tuples passed into `Find_NodeID_Connect` to filter edges before Dijkstra
- Output saved as `osm_flood_detour.gpkg` layer `flood_detour` — a GeoDataFrame with LINESTRING geometry per path segment, suitable for QGIS

**Key constraint:** `osm_graph.gpkg` (8.8 MB) is excluded from git (see `.gitignore`) and must be regenerated locally via `rum-1-graph.py`.
