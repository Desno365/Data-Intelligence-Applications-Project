from typing import List

from src.slot import Slot

# Definition of the project constants

# set to true to enable debug printing
settings = {'auctionPrint': False,
            'adPrint': False,
            'advertiserPrint': False}
# the number of node categories in the network, each node is assigned a random category at creation
CATEGORIES = 5
categories = [0, 1, 2, 3, 4]
# the number of ad slots in a slate
SLATE_DIMENSION = 3
# this is never used, delete before delivery
click_propensities = [1, 1, 1, 1, 1]
# the probability that there is an edge between two nodes in the network
network_connectivity = 0.4
# margin for floating point value comparisons
floatingPointMargin = 0.001
# the number of bandit arms and their values
number_of_bandit_arms = 10
bandit_quality_values = []
for i in range(1, 11, 1):
    j = i/10
    bandit_quality_values.append(j)


def get_slates() -> List[List[Slot]]:
    slates = []
    for current_category in range(CATEGORIES):
        slate = [Slot(slot_id, 0.80 ** (slot_id + 1)) for slot_id in range(SLATE_DIMENSION)]
        slates.append(slate)
    return slates
