import numpy as np
from matplotlib import pyplot as plt

from src import slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.utils import Utils

# ################ Prepare experiment. ################ #

NUMBER_OF_ADVERTISERS = constants.SLATE_DIMENSION + 1

network_instance = network.Network(40, False)

print("Ads:")
advertisers = [StochasticStationaryAdvertiser(quality=None) for _ in range(NUMBER_OF_ADVERTISERS)]
advertisements = [adv.participate_auction() for adv in advertisers]
Utils.print_array(advertisements)

print("Slates:")
slates = []
for current_category in range(constants.CATEGORIES):
    slate = [slot.Slot(slot_id, 0.80 ** (slot_id + 1)) for slot_id in range(constants.SLATE_DIMENSION)]
    slates.append(slate)
Utils.print_array(slates)


# ################ Run experiment. ################ #

number_of_activated_nodes_per_experiment = []
list_iterations = []
log_range = np.logspace(0, 4, num=100, dtype='int')  # Starting from 10^0 to 10^4.
log_range = list(dict.fromkeys(log_range))
print("Using these values as possible iterations:")
print(log_range)

for iterations in log_range:
    print("#################### Running with iterations " + str(iterations))
    list_iterations.append(iterations)
    social_influence = AdPlacementSimulator.simulate_ad_placement(network=network_instance, ads=advertisements, slates=slates, iterations=iterations)
    number_of_activated_nodes_per_experiment.append(social_influence[advertisers[0].id]['activatedNodes'])
best_perfomance = number_of_activated_nodes_per_experiment[-1]


# ################ Plot result. ################ #

plt.figure(0)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
plt.plot([best_perfomance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
plt.ylim(ymin=0)
plt.show()

plt.figure(1)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(log_range, number_of_activated_nodes_per_experiment, 'r')
plt.plot([best_perfomance for i in range(len(number_of_activated_nodes_per_experiment))], 'b--')
plt.show()

