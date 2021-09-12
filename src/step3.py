import numpy as np
from matplotlib import pyplot as plt

from src import slot, constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.utils import Utils

NUMBER_OF_STOCHASTIC_ADVERTISERS = constants.SLATE_DIMENSION + 10

network_instance = network.Network(50, False)

print("Slates:")
slates = constants.get_slates()
Utils.print_array(slates)

print("Ads:")
advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
for advertiser in advertisers:
    print('ad id', advertiser.id, 'bids', advertiser.ad.bids)
greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(5)], ad_value=1, network=network_instance)
greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in advertisers])
greedy_learner.set_slates(slates=slates)
advertisers.append(greedy_learner)
greedy_ad = greedy_learner.participate_auction()

greedy_learner.plot_history()


