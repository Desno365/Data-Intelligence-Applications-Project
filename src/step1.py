import random
from typing import List

import numpy as np
from matplotlib import pyplot as plt

from src import ad, slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.bids_enum import BidsEnum
from src.utils import Utils


def get_random_bids() -> List[BidsEnum]:
    return [random.choice(list(BidsEnum)) for _ in range(5)]


# ################ Prepare experiment. ################ #

network_instance = network.Network(100, False)

print("Ads:")
advertisements = [ad.Ad(0, [0.5, 0.1, 0.1, 0.1, 0.1], 1, get_random_bids()),
                  ad.Ad(1, [0.1, 0.5, 0.1, 0.1, 0.1], 1, get_random_bids()),
                  ad.Ad(2, [0.1, 0.1, 0.5, 0.1, 0.1], 1, get_random_bids())]
Utils.print_array(advertisements)

print("Slates:")
slates = []
for current_category in range(constants.CATEGORIES):
    slate = [slot.Slot(0, 0.80),
             slot.Slot(1, 0.80 * 0.80)]
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
    print("Running with iterations " + str(iterations))
    list_iterations.append(iterations)
    r = AdPlacementSimulator.simulate_ad_placement(network=network_instance, ads=advertisements, slates=slates, iterations=iterations)
    number_of_activated_nodes_per_experiment.append(r[0]['activatedNodes'])
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

