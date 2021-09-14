import random

import numpy as np
from matplotlib import pyplot as plt, colors

from src import slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.utils import Utils
import networkx as nx

# ################ Prepare experiment. ################ #

NUMBER_OF_ADVERTISERS = constants.SLATE_DIMENSION + 1

network_instance = network.Network(500, False)
live_edges, _ = network_instance.generate_live_edge_graph()
network_instance.depth_first_search([random.randint(0, 499) for i in range(3)], live_edges)

slates = constants.slates
advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(NUMBER_OF_ADVERTISERS)]
advertisements = [adv.participate_auction() for adv in advertisers]

# ################ Draw the network ################ #
G = network_instance.drawing_network
labels = nx.get_node_attributes(G, 'category')

edge_colours = []
edge_width = []
for edge in G.edges:
    if G.edges[edge]["is_active"]:
        edge_colours.append('black')
        edge_width.append(0.5)
    else:
        edge_colours.append('pink')
        edge_width.append(0.1)

color_map = []
node_size = []
attributes = nx.get_node_attributes(G, 'category')
for node in G:
    if G.nodes[node]['is_seed']:
        color_map.append('magenta')
        node_size.append(50)
    elif G.nodes[node]['is_active']:
        color_map.append('black')
        node_size.append(30)
    elif attributes[node] == 0:
        color_map.append((0.8, 0.6, 1))
        node_size.append(10)
    elif attributes[node] == 1:
        color_map.append((0.4, 0.4, 1))
        node_size.append(10)
    elif attributes[node] == 2:
        color_map.append((0, 0, 1))
        node_size.append(10)
    elif attributes[node] == 3:
        color_map.append((0, 0.6, 0.2))
        node_size.append(10)
    elif attributes[node] == 4:
        color_map.append((0, 0.5, 0.6))
        node_size.append(10)

nx.draw_spring(G, with_labels=False, labels=labels, node_size=node_size, arrows=True, width=edge_width, node_color=color_map, edge_color=edge_colours)
plt.show()

# ################ Run experiment. ################ #
number_of_activated_nodes_per_experiment = []
list_iterations = []
log_range = np.logspace(0, 3, num=100, dtype='int')  # Starting from 10^0 to 10^4.
log_range = list(dict.fromkeys(log_range))
log_range = [1, 5, 10, 50]
print("Using these values as possible iterations:")
print(log_range)

for iterations in log_range:
    print(f"#################### Running with {str(iterations)} iterations")
    list_iterations.append(iterations)
    social_influence = AdPlacementSimulator.simulate_ad_placement(network=network_instance,
                                                                  ads=advertisements,
                                                                  slates=slates,
                                                                  use_estimated_qualities=False,
                                                                  use_estimated_activations=False,
                                                                  iterations=iterations)
    for category in constants.categories:
        n = social_influence[advertisers[0].id][category]['activatedNodes']
    number_of_activated_nodes_per_experiment.append(n)
    print(n)
best_performance = number_of_activated_nodes_per_experiment[-1]

# ################ Plot result. ################ #

plt.figure(0)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
plt.plot([best_performance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
plt.ylim(ymin=0)
plt.show()

plt.figure(1)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
plt.plot([best_perfomance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
plt.show()

