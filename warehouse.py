"""


"""
import networkx as nx
import networkx.algorithms.shortest_paths.dense as nxalg
#import matplotlib.pyplot as plt

# Warehouse characteristics
LOCATION_X = 1
LOCATION_Y = 1
AISLES = 20
CROSS_AISLES = 1
AISLE_SIZE = 3
CROSS_AISLE_SIZE = 6
LOCATIONS = 10

# The graph instance
G = nx.Graph()

# Calculate cross points
cross_points = [0]
old = 0
for _ in range(CROSS_AISLES + 1):
    cross_points.append(old + LOCATIONS + 1)
    old += LOCATIONS + 1

# Calculate total nodes per side Y
locations_per_longaisle = LOCATIONS * (CROSS_AISLES + 1) + CROSS_AISLES + 2

# Populate the graph
node_id = 0
for x in range(AISLES):
    for y in range(locations_per_longaisle):
        G.add_node(node_id)
        if y > 0:
            weight = LOCATION_Y/2 + CROSS_AISLE_SIZE/2 if y in cross_points[1:-1] or (y - 1) in cross_points[1:-1] else LOCATION_Y
            G.add_edge(node_id, node_id - 1, weight=weight)
        if x > 0 and y in cross_points:
            G.add_edge(node_id, node_id - locations_per_longaisle, weight=LOCATION_X*2)
        node_id += 1

# Plot the graph
#nx.draw(G, with_labels=True, font_weight='bold')
#plt.show()

# Set the distance matrix
distance_matrix = nxalg.floyd_warshall_numpy(G)
