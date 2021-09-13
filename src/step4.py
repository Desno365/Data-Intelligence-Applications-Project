# bandit learner for click probabilities in publisher (ad.ad_quality * slot.slot_prominence)
# len(ads) = len(advertisers)
# len(qualities) = len(ads) * constants.CATEGORIES

# does the publisher know the slot prominence values and ad placements so that we estimate only qualities?
# ad quality is constant
# slot prominence depends on ad placement and advertiser bids so it could in the worst case be different every time
# "Adopt a classical bandit algorithm in which one can learn the click probability (quality) of an ad"
# we have two scenarios: get feedback only when the ad is in the first slot
# get feedback every time the ad is clicked even if not in the first slot

# one bandit with many arms
# one bandit with arm = [[quality for _ in range(constants.CATEGORIES)] for _ in range(len(ads)]
# number of arms is number of discrete values**(len(ads)*constants.CATEGORIES)
# or
# many bandits with fewer arms (one bandit for every ad)
# len(ads) = len(bandits) with arm = [quality for _ in range(constants.CATEGORIES)]
# number of arms is number of discrete values**(constants.CATEGORIES)

# individual click probability values are i in range(0, 1.1, 0.1), 11 values total (could be too many)
# or i in range(0, 1.1, 0.25), only 5 values

# pass click probability to advertiser
# advertiser passes click probability to monte carlo
# if click probability = None then
# MC would use activation_probability = current_ad.ad_quality * position.slot_prominence
# otherwise use activation_probability = click probability input argument
# seeds_per_ad_is = network.calculateSeeds(slates, qualities)
# quality = qualities[ad_id][category]
import random
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher

# create context
network_instance = network.Network(1000, False)
nodes_per_category = network_instance.network_report()

stochastic_advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(constants.SLATE_DIMENSION)]
greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(constants.CATEGORIES)], ad_value=1, network=network_instance)
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
advertisers.append(greedy_learner)

publisher = Publisher(network=network_instance, advertisers=advertisers, bandit_type_qualities=BanditTypeEnum.THOMPSON_SAMPLING,
                      bandit_type_activations=BanditTypeEnum.THOMPSON_SAMPLING, window_size=None)

learn_from_first_slot_only = True

print('true quality values:')
for advertiser in advertisers:
    print(advertiser.id, advertiser.ad.real_qualities)

# Variables for plot
plot_rewards_bandit = {}
plot_regret_bandit = {}
plot_rewards_random = {}
plot_regret_random = {}
for advertiser in advertisers:
    ad_id = advertiser.id
    plot_rewards_bandit[ad_id] = {}
    plot_regret_bandit[ad_id] = {}
    plot_rewards_random[ad_id] = {}
    plot_regret_random[ad_id] = {}
    for category in range(constants.CATEGORIES):
        plot_rewards_bandit[ad_id][category] = np.array([])
        plot_regret_bandit[ad_id][category] = np.array([])
        plot_rewards_random[ad_id][category] = np.array([])
        plot_regret_random[ad_id][category] = np.array([])


for day in range(100):
    print('qualities at day', day)
    # get current quality estimates
    bandit_estimated_qualities = publisher.get_bandit_qualities()
    for ad_id in bandit_estimated_qualities.keys():
        print('ad_id: ', ad_id, 'bandit estimated qualities: ', bandit_estimated_qualities[ad_id])
    # pass quality estimates to ads
    for advertiser in advertisers:
        ad = advertiser.ad
        estimated_q = bandit_estimated_qualities[ad.ad_id]
        ad.set_estimated_qualities(estimated_q)
    # set context for simulation for calculating best bids
    slates = constants.get_slates()
    greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in stochastic_advertisers])
    greedy_learner.set_slates(slates=slates)
    # calculate bids by simulation
    print('calculating bids ...')
    greedy_simulation_start = datetime.now()
    greedy_ad = greedy_learner.participate_auction()
    print(f'calculated bids in {datetime.now() - greedy_simulation_start}')
    # do environment sample

    ads = []
    for advertiser in advertisers:
        ads.append(advertiser.ad)
    time = datetime.now()
    social_influence = AdPlacementSimulator.simulate_ad_placement(
        network=network_instance,
        ads=ads,
        slates=slates,
        iterations=1,  # iterations = 1 means network sample
        use_estimated_qualities=False,  # use_estimated_qualities=False means true qualities from real network
        estimated_activations=None   # use_estimated_activations=False means true activations from real network
    )
    elapsed_time = datetime.now() - time
    print(f'environment sample time {elapsed_time}')
    # do rewards and bandit update
    rewards = {}
    for advertiser in advertisers:
        ad_id = advertiser.id
        rewards[ad_id] = {}
        for category in range(constants.CATEGORIES):
            rewards[ad_id][category] = -1
    # calculate rewards
    for category in range(constants.CATEGORIES):
        slate = slates[category]
        susceptible_nodes = nodes_per_category[category]
        for slot in slate:
            ad = slot.assigned_ad
            number_of_seeds = social_influence[ad.ad_id][category]['seeds']
            measured_quality = (number_of_seeds / susceptible_nodes) / constants.SLOT_VISIBILITY
            # measured_quality = (number_of_seeds / nodes_per_category[category]) / slot.slot_prominence
            susceptible_nodes -= number_of_seeds
            if susceptible_nodes <= constants.number_of_bandit_arms:
                print("Not enough samples.")
                break
            error = abs(measured_quality - bandit_estimated_qualities[ad.ad_id][category])
            if error <= 1 / constants.number_of_bandit_arms:
                rewards[ad.ad_id][category] = 1
            else:
                rewards[ad.ad_id][category] = 0
            real_error = abs(slot.assigned_ad.real_quality - bandit_estimated_qualities[ad.ad_id][category])
            plot_regret_bandit[ad.ad_id][category] = np.append(plot_regret_bandit[ad.ad_id][category], real_error)
            plot_rewards_bandit[ad.ad_id][category] = np.append(plot_rewards_bandit[ad.ad_id][category], 1 - real_error)
            random_estimated_quality = random.choice(constants.bandit_quality_values)
            random_regret = abs(slot.assigned_ad.real_quality - random_estimated_quality)
            plot_regret_random[ad.ad_id][category] = np.append(plot_regret_random[ad.ad_id][category], random_regret)
            plot_rewards_random[ad.ad_id][category] = np.append(plot_rewards_random[ad.ad_id][category], 1 - random_regret)

            if learn_from_first_slot_only:
                break
    # update bandits with rewards
    publisher.update_bandits_quality(rewards=rewards)

# Create plot.
# Note: one experiment = one bandit (one bandit for each category and for each advertiser)
for advertiser in advertisers:
    ad_id = advertiser.id
    for category in range(constants.CATEGORIES):
        plt.figure(0)
        plt.xlabel("t")
        plt.ylabel(f"Reward ad {ad_id}, cat {category}")
        plt.plot(np.cumsum(plot_rewards_bandit[ad_id][category]), 'r')
        plt.plot(np.cumsum(plot_rewards_random[ad_id][category]), 'g')
        plt.legend(["Bandit", "Random"])
        plt.show()

        plt.figure(0)
        plt.xlabel("t")
        plt.ylabel(f"Regret ad {ad_id}, cat {category}")
        plt.plot(np.cumsum(plot_regret_bandit[ad_id][category]), 'r')
        plt.plot(np.cumsum(plot_regret_random[ad_id][category]), 'g')
        plt.legend(["Bandit", "Random"])
        plt.show()

print('true quality values:')
for advertiser in advertisers:
    print(advertiser.id, advertiser.ad.real_qualities)

