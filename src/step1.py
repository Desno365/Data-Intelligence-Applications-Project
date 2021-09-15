import random

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt

from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser


# ################ Constants. ################ #
NUMBER_OF_STOCHASTIC_ADVERTISERS = constants.SLATE_DIMENSION + 1
MAX_NUMBER_OF_ITERATIONS_EXPONENT = 3
BASELINE_NUMBER_OF_ITERATIONS = 10000
NUMBER_OF_EXPERIMENTS = 10000


# ################ Prepare context: Network. ################ #
network_instance = network.Network(constants.number_of_nodes, False)
_ = network_instance.generate_live_edge_graph()
network_instance.depth_first_search([random.randint(0, constants.number_of_nodes-1) for i in range(3)])

# ################ Prepare context: Network. ################ #
advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
advertisements = [adv.participate_auction() for adv in advertisers]

# ################ Prepare variables for the experiment. ################ #
number_of_activated_nodes_per_experiment = []
log_range = np.logspace(0, MAX_NUMBER_OF_ITERATIONS_EXPONENT, num=NUMBER_OF_EXPERIMENTS, dtype='int')  # Starting from 10^0 to 10^4.
log_range = list(dict.fromkeys(log_range))
log_range.append(BASELINE_NUMBER_OF_ITERATIONS)  # Baseline (interpreted as the run with the highest number of iterations)
print("Using these values as possible iterations:")
print(log_range)


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
for iterations in log_range:
    print(f"#################### Running with {str(iterations)} iterations")
    social_influence = AdPlacementSimulator.simulate_ad_placement(
        network=network_instance,
        ads=advertisements,
        slates=constants.slates,
        use_estimated_qualities=False,
        use_estimated_activations=False,
        iterations=iterations
    )
    total_activated_nodes = 0
    for category in constants.categories:
        total_activated_nodes += social_influence[advertisers[0].id][category]['activatedNodes']
    number_of_activated_nodes_per_experiment.append(total_activated_nodes)


# ################ Prepare result. ################ #
best_performance = number_of_activated_nodes_per_experiment.pop()  # Baseline
log_range.pop()  # Baseline
absolute_performance_gap = [abs(best_performance - activated_nodes) for activated_nodes in number_of_activated_nodes_per_experiment]


# ################ Plot result. ################ #
plt.rcParams["figure.figsize"] = (8, 6)

plt.figure(0)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
plt.plot(log_range, [best_performance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
plt.legend(["Activated nodes per experiment", f"Baseline ({BASELINE_NUMBER_OF_ITERATIONS} iterations)"])
plt.show()

plt.figure(1)
plt.xlabel("Iterations")
plt.ylabel("Performance gap of activated nodes")
plt.plot(log_range, absolute_performance_gap, 'r')
plt.legend([" |baseline - experiment_value| "])
plt.axis([0, None, 0, None])  # plt.axis([xmin, xmax, ymin, ymax])
plt.show()
