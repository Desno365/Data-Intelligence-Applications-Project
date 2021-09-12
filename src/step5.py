from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher
from random import random

network_instance = network.Network(50, False)
stochastic_advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(7)]
greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(5)], ad_value=1, network=network_instance)
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
advertisers.append(greedy_learner)
publisher = Publisher(network=network, advertisers=advertisers, bandit_type_qualities=BanditTypeEnum.UCB1,
                      bandit_type_activations=BanditTypeEnum.UCB1, window_size=None)

bandit_estimated_activations = {}
for from_category in range(constants.CATEGORIES):
    bandit_estimated_activations[from_category] = {}
    for to_category in range(constants.CATEGORIES):
        bandit_estimated_activations[from_category][to_category] = {}
        bandit_estimated_activations[from_category][to_category] = random()

for day in range(30):



