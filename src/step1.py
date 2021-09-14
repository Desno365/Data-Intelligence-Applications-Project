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
G = network_instance.drawing_network
subax1 = plt.subplot(121)
labels = nx.get_node_attributes(G, 'category')
color_map = []
attributes = nx.get_node_attributes(G, 'category')
for node in G:
    if attributes[node] == 0:
        color_map.append('red')
    elif attributes[node] == 1:
        color_map.append('green')
    elif attributes[node] == 2:
        color_map.append('blue')
    elif attributes[node] == 3:
        color_map.append('yellow')
    elif attributes[node] == 4:
        color_map.append('purple')
nx.draw_spring(G, with_labels=False, labels=labels, node_size=10, arrows=True, width=0.05, node_color=color_map)
# subax2 = plt.subplot(122)
# nx.draw_shell(G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
plt.show()
# slates = constants.slates
# advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(NUMBER_OF_ADVERTISERS)]
# advertisements = [adv.participate_auction() for adv in advertisers]
#
# # ################ Run experiment. ################ #
# number_of_activated_nodes_per_experiment = []
# list_iterations = []
# log_range = np.logspace(0, 3, num=100, dtype='int')  # Starting from 10^0 to 10^4.
# log_range = list(dict.fromkeys(log_range))
# # log_range = [1, 5, 10, 50, 100, 200, 500, 1000]
# print("Using these values as possible iterations:")
# print(log_range)
#
# for iterations in log_range:
#     print(f"#################### Running with {str(iterations)} iterations")
#     list_iterations.append(iterations)
#     social_influence = AdPlacementSimulator.simulate_ad_placement(network=network_instance,
#                                                                   ads=advertisements,
#                                                                   slates=slates,
#                                                                   use_estimated_qualities=False,
#                                                                   use_estimated_activations=False,
#                                                                   iterations=iterations)
#     for category in constants.categories:
#         n = social_influence[advertisers[0].id][category]['activatedNodes']
#     number_of_activated_nodes_per_experiment.append(n)
#     print(n)
# best_performance = number_of_activated_nodes_per_experiment[-1]
#
# # ################ Plot result. ################ #
#
# plt.figure(0)
# plt.xlabel("Iterations")
# plt.ylabel("Activated nodes")
# plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
# plt.plot([best_performance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
# plt.ylim(ymin=0)
# plt.show()
#
# plt.figure(1)
# plt.xlabel("Iterations")
# plt.ylabel("Activated nodes")
# plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
# plt.plot([best_perfomance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
# plt.show()

