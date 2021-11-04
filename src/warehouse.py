"""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
This file contains the implementation of a warehouse for picking.
Once defined the warehouse characteristics, the graph of possible paths (i.e., G) is instantiated
and the matrix of minimum distances (i.e., distance_matrix) is calculated using Floyd-Warshall
algorithm.

Author: Mattia Neroni, Ph.D., Eng. (May 2021).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""
import networkx as nx
import networkx.algorithms.shortest_paths.dense as nxalg
import matplotlib.pyplot as plt

# Warehouse characteristics
LOCATION_X = 2
LOCATION_Y = 2
AISLES = 10
CROSS_AISLES = 1
AISLE_SIZE = 4
CROSS_AISLE_SIZE = 8
LOCATIONS = 8

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
pos = dict()
current_pos = [0, 0]
for x in range(AISLES):
    current_pos[1] = 0
    for y in range(locations_per_longaisle):
        G.add_node(node_id)
        if y > 0:
            weight = LOCATION_Y/2 + CROSS_AISLE_SIZE/2 if y in cross_points[1:-1] or (y - 1) in cross_points[1:-1] else LOCATION_Y
            current_pos[1] += weight
            G.add_edge(node_id, node_id - 1, weight=weight)
        if x > 0 and y in cross_points:
            G.add_edge(node_id, node_id - locations_per_longaisle, weight=LOCATION_X*2 + AISLE_SIZE)

        pos[node_id] = tuple(current_pos)
        node_id += 1
    current_pos[0] += LOCATION_X*2 + AISLE_SIZE

# Set the distance matrix
distance_matrix = nxalg.floyd_warshall_numpy(G)
#print(distance_matrix)


if __name__ == "__main__":
    # Plot the graph
    nx.draw(G, pos=pos, with_labels=True, font_size=8, font_weight="bold")
    plt.show()
