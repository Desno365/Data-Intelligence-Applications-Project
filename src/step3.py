import numpy as np
from matplotlib import pyplot as plt

from src import slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.utils import Utils

NUMBER_OF_STOCHASTIC_ADVERTISERS = constants.SLATE_DIMENSION

network_instance = network.Network(50, False)

print("Slates:")
slates = []
for current_category in range(constants.CATEGORIES):
    slate = [slot.Slot(slot_id, 0.80 ** (slot_id + 1)) for slot_id in range(constants.SLATE_DIMENSION)]
    slates.append(slate)
Utils.print_array(slates)

print("Ads:")
advertisers = [StochasticStationaryAdvertiser(quality=None) for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
greedy_learner = GreedyLearningAdvertiser(quality=None, value=0.5, network=network_instance)
greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in advertisers])
greedy_learner.set_slates(slates=slates)
advertisers.append(greedy_learner)
greedy_ad = greedy_learner.participate_auction()

# TODO: make graphs
