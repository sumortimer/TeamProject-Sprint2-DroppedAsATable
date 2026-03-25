import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import random
import sqlite3
from scipy.spatial import cKDTree
import os

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

# 1. GET THE ROAD NETWORK
print("Downloading Exeter network...")
original_lat = 50.7184
original_lon = -3.5339

lat_shift = 1000 / 111111
lon_shift = 600 / (111111 * np.cos(np.radians(original_lat)))

new_lat = original_lat + lat_shift
new_lon = original_lon + lon_shift

G = ox.graph_from_point(
    (new_lat, new_lon),
    dist=1200,
    network_type='drive',
    simplify=True
)

print(f"Network: {len(G.nodes())} nodes, {len(G.edges())} edges")

# Get bounding box for queries
bbox = ox.utils_geo.bbox_from_point((new_lat, new_lon), dist=1300)
north, south, east, west = bbox

# 2. ADD ELEVATION DATA

# Realistic elevation simulation based on Exeter geography
for node_id in G.nodes():
    lon = G.nodes[node_id]['x']
    lat = G.nodes[node_id]['y']

    # Simple elevation model for Exeter
    # Lower near river Exe (approx -3.53), higher on surrounding hills
    river_lon = -3.53
    distance_from_river = abs(lon - river_lon) * 111000  # approximate meters
    elevation = 15 + (distance_from_river * 0.06)  # 15m base, +6m per 100m

    # Add some random variation
    elevation += random.uniform(-2, 2)
    G.nodes[node_id]['elevation'] = round(np.clip(elevation, 10, 85), 1)


# 3. ADD LIGHTING DATA (using correct OSMnx syntax)

nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)
center_lat = nodes_gdf['y'].mean()
center_lon = nodes_gdf['x'].mean()

# Calculate betweenness centrality for node importance
try:
    # Convert to undirected for centrality calculation
    G_undirected = G.to_undirected()
    betweenness = nx.betweenness_centrality(G_undirected, weight='length')
except:
    betweenness = {node: 0 for node in G.nodes()}

for node_id in G.nodes():
    # Get node degree (number of connections)
    degree = G.degree(node_id)

    # Distance to center
    lon = G.nodes[node_id]['x']
    lat = G.nodes[node_id]['y']
    distance_to_center = ((lon - center_lon)**2 + (lat - center_lat)**2)**0.5 * 111000

    # Lighting score: better in center, on high-degree nodes, and high betweenness
    centrality_score = max(0, 1 - (distance_to_center / 1200))
    degree_score = min(1, degree / 8)  # Cap at degree 8
    betweenness_score = min(1, betweenness.get(node_id, 0) * 10)

    lighting_score = 0.5 * centrality_score + 0.3 * degree_score + 0.1 * betweenness_score + 0.1 * random.random()
    G.nodes[node_id]['lighting'] = round(np.clip(lighting_score, 0, 1), 2)


# 4. ADD CRIME DATA

for node_id in G.nodes():
    G.nodes[node_id]['crime'] = round(np.clip(np.random.uniform(0, 1) - 0.15, 0, 1), 2)

# 5. ADD GREENERY DATA

# Simulate greenery based on distance from random park locations
nodes_gdf = ox.graph_to_gdfs(G, nodes=True, edges=False)
center_lat = nodes_gdf['y'].mean()
center_lon = nodes_gdf['x'].mean()

# Assume parks are on the outskirts
park_locations = [
    (center_lon + 0.008, center_lat + 0.005),
    (center_lon - 0.007, center_lat - 0.006),
    (center_lon + 0.003, center_lat - 0.008),
    (center_lon - 0.005, center_lat + 0.007)
]

for node_id in G.nodes():
    x, y = G.nodes[node_id]['x'], G.nodes[node_id]['y']
    min_dist = min([((x - px)**2 + (y - py)**2)**0.5 * 111000 for px, py in park_locations])
    greenery_score = max(0.1, 1 - (min_dist / 500))
    greenery_score += random.uniform(-0.05, 0.05)
    G.nodes[node_id]['greenery'] = round(np.clip(greenery_score, 0, 1), 2)

# 6. ADD GRADIENT (from elevation changes)

for node_id in G.nodes():
  G.nodes[node_id]['gradient'] = round(np.random.uniform(0, 0.15), 3)

# 7. BUILD FINAL DATASETS

# mapping from original IDs to sequential local IDs
original_to_local = {node_id: idx for idx, node_id in enumerate(G.nodes())}

# Build nodes dataset with all indicators
nodes_data = []
for node_id, attrs in G.nodes(data=True):
    local_id = original_to_local[node_id]

    nodes_data.append({
        'nodeID': local_id,
        'coordinatesX': round(attrs.get('x', 0), 6),
        'coordinatesY': round(attrs.get('y', 0), 6),
        'lighting': attrs.get('lighting', 0.5),
        'crime': attrs.get('crime', 0.5),
        'greenery': attrs.get('greenery', 0.5),
        'gradient': attrs.get('gradient', 0.5),
        'elevation': attrs.get('elevation', 0)
    })

# Build edges dataset with gradients
edges_data = []
edge_id = 0
processed_pairs = set()

for u, v, data in G.edges(data=True):
    pair = tuple(sorted([u, v]))
    if pair not in processed_pairs:
        processed_pairs.add(pair)
        length = data.get('length', 0)
        gradient = data.get('gradient', 0)

        edges_data.append({
            'edgeId': edge_id,
            'startNode': original_to_local[u],
            'endNode': original_to_local[v],
            'length': round(length, 2),
            'gradient': round(gradient, 4)
        })
        edge_id += 1

# Create DataFrames
nodes_df = pd.DataFrame(nodes_data)
edges_df = pd.DataFrame(edges_data)

# 8. SAVE TO DATABASE
db_file = "task6.db"
conn = sqlite3.connect(db_file)
nodes_df.to_sql('nodes', conn, if_exists='replace', index=False)
edges_df.to_sql('edges', conn, if_exists='replace', index=False)
conn.close()