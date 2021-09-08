import random
from typing import List

from matplotlib import pyplot as plt

from src import ad, slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.bids_enum import BidsEnum
from src.utils import Utils


def get_random_bids() -> List[BidsEnum]:
    return [random.choice(list(BidsEnum)) for _ in range(5)]


BEST_PERFORMANCE = 10.0  # TODO calculate
print('ok')
network_instance = network.Network(50, False)

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

number_of_activated_nodes_per_experiment = []
list_iterations = []
for i in range(1, 100, 1):
    iterations = i
    list_iterations.append(iterations)
    r = AdPlacementSimulator.simulate_ad_placement(network=network_instance, ads=advertisements, slates=slates, iterations=iterations)
    number_of_activated_nodes_per_experiment.append(r[0]['activatedNodes'])

plt.figure(0)
plt.xlabel("Iterations")
plt.ylabel("Activated nodes")
plt.plot(number_of_activated_nodes_per_experiment, 'r')
#plt.ylim(ymin=0)
plt.show()

plt.plot(list_iterations, number_of_activated_nodes_per_experiment)
plt.show()



