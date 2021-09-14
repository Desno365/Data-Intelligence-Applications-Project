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
learn_qualities = True
learn_activations = False
use_greedy_advertiser = True
learn_from_first_slot_only = False
bandit_type_qualities = BanditTypeEnum.THOMPSON_SAMPLING
bandit_type_activations = BanditTypeEnum.THOMPSON_SAMPLING
window_size = 50
number_of_days = 50

network_instance = network.Network(constants.number_of_nodes, False)
nodes_per_category = network_instance.network_report()

stochastic_advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(constants.SLATE_DIMENSION + 1)]
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
if use_greedy_advertiser:
    greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(constants.CATEGORIES)], ad_value=1,
                                              network=network_instance, )
    advertisers.append(greedy_learner)

publisher = Publisher(network=network_instance, advertisers=advertisers, bandit_type_qualities=bandit_type_qualities,
                      bandit_type_activations=bandit_type_activations, window_size=window_size)

# Variables for plot
if learn_activations:
    plot_rewards_bandit_activation = {}
    plot_regret_bandit_activation = {}
    plot_rewards_random_activation = {}
    plot_regret_random_activation = {}
    for from_category in range(constants.CATEGORIES):
        plot_rewards_bandit_activation[from_category] = {}
        plot_regret_bandit_activation[from_category] = {}
        plot_rewards_random_activation[from_category] = {}
        plot_regret_random_activation[from_category] = {}
        for to_category in range(constants.CATEGORIES):
            plot_rewards_bandit_activation[from_category][to_category] = np.array([])
            plot_regret_bandit_activation[from_category][to_category] = np.array([])
            plot_rewards_random_activation[from_category][to_category] = np.array([])
            plot_regret_random_activation[from_category][to_category] = np.array([])
if learn_qualities:
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

for day in range(number_of_days):
    print('activations at day', day)
    # get current quality estimates
    bandit_estimated_qualities = publisher.get_bandit_qualities()
    bandit_estimated_activations = publisher.get_bandit_activations()
    for from_category in bandit_estimated_activations.keys():
        print('from cat: ', from_category, 'bandit estimated activations: ', bandit_estimated_activations[from_category])

    # pass estimations to advertisers and ads
    for advertiser in advertisers:
        ad = advertiser.ad
        estimated_q = bandit_estimated_qualities[ad.ad_id]
        ad.set_estimated_qualities(estimated_q)
        advertiser.estimated_activations = bandit_estimated_activations
    # set context for simulation for calculating best bids
    slates = constants.get_slates()
    greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in stochastic_advertisers])
    greedy_learner.set_slates(slates=slates)
    # calculate bids by simulation
    print('calculating bids ...')
    greedy_simulation_start = datetime.now()
    # todo greedy_ad = greedy_learner.participate_auction()
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

    if learn_qualities:
        rewards_qualities = {}
        for advertiser in advertisers:
            ad_id = advertiser.id
            rewards_qualities[ad_id] = {}
            for category in range(constants.CATEGORIES):
                rewards_qualities[ad_id][category] = -1
        # calculate rewards for quality estimates
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
                    rewards_qualities[ad.ad_id][category] = 1
                else:
                    rewards_qualities[ad.ad_id][category] = 0
                real_error = abs(slot.assigned_ad.real_quality - bandit_estimated_qualities[ad.ad_id][category])
                plot_regret_bandit[ad.ad_id][category] = np.append(plot_regret_bandit[ad.ad_id][category], real_error)
                plot_rewards_bandit[ad.ad_id][category] = np.append(plot_rewards_bandit[ad.ad_id][category], 1 - real_error)
                random_estimated_quality = random.choice(constants.bandit_quality_values)
                random_regret = abs(slot.assigned_ad.real_quality - random_estimated_quality)
                plot_regret_random[ad.ad_id][category] = np.append(plot_regret_random[ad.ad_id][category], random_regret)
                plot_rewards_random[ad.ad_id][category] = np.append(plot_rewards_random[ad.ad_id][category],
                                                                    1 - random_regret)
                if learn_from_first_slot_only:
                    break
        # update bandits with rewards
        publisher.update_bandits_quality(rewards=rewards_qualities)
    if learn_activations:
        # do rewards and bandit update for activation estimate
        rewards_activations = {}
        for from_category in constants.categories:
            rewards_activations[from_category] = {}
            for to_category in range(constants.CATEGORIES):
                rewards_activations[from_category][to_category] = -1
        # calculate rewards
        for from_category in constants.categories:
            for to_category in constants.categories:

                if network_instance.cross_category_edges[from_category][to_category] != 0:
                    measured_activation = network_instance.activation_realization[from_category][to_category] / \
                                          network_instance.cross_category_edges[from_category][to_category]
                else:
                    measured_activation = 0
                # print(
                #     f'n{network_instance.activation_realization[from_category][to_category]}, '
                #     f'tot{network_instance.cross_category_edges[from_category][to_category]}, '
                #     f'act{measured_activation}')
                error_activation = abs(measured_activation - bandit_estimated_activations[from_category][to_category])

                if error_activation <= 1 / constants.number_of_bandit_arms:
                    rewards_activations[from_category][to_category] = 1
                else:
                    rewards_activations[from_category][to_category] = 0

                real_error_activation = abs(network_instance.weight_matrix[from_category][to_category] - bandit_estimated_activations[from_category][to_category])
                plot_regret_bandit_activation[from_category][to_category] = np.append(plot_regret_bandit_activation[from_category][to_category], real_error_activation)
                plot_rewards_bandit_activation[from_category][to_category] = np.append(plot_rewards_bandit_activation[from_category][to_category], 1 - real_error_activation)

                random_estimated_activation = random.choice(constants.bandit_activation_values)
                random_regret_activation = abs(network_instance.weight_matrix[from_category][to_category] - random_estimated_activation)

                plot_regret_random_activation[from_category][to_category] = np.append(plot_regret_random_activation[from_category][to_category], random_regret_activation)
                plot_rewards_random_activation[from_category][to_category] = np.append(plot_rewards_random_activation[from_category][to_category], 1 - random_regret_activation)
        # update bandits with rewards
        publisher.update_bandits_activations(rewards=rewards_activations)

if learn_activations:
    # # Create plot for activations
    # # Note: one experiment = one bandit (one bandit for each category and for each advertiser)
    for from_category in range(constants.CATEGORIES):
        for to_category in range(constants.CATEGORIES):
            plt.figure(0)
            plt.xlabel("t")
            plt.ylabel(f"Reward from category {from_category}, to cat {to_category}")
            plt.plot(np.cumsum(plot_rewards_bandit_activation[from_category][to_category]), 'r')
            plt.plot(np.cumsum(plot_rewards_random_activation[from_category][to_category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

            plt.figure(1)
            plt.xlabel("t")
            plt.ylabel(f"Regret ad {from_category}, cat {to_category}")
            plt.plot(np.cumsum(plot_regret_bandit_activation[from_category][to_category]), 'r')
            plt.plot(np.cumsum(plot_regret_random_activation[from_category][to_category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

    print('true activation values:')
    for from_category in range(constants.CATEGORIES):
        print(network_instance.weight_matrix[from_category][:])
fig = 0
if learn_qualities:
    # Create plot for qualities
    # Note: one experiment = one bandit (one bandit for each category and for each advertiser)
    for advertiser in advertisers:
        ad_id = advertiser.id
        for category in range(constants.CATEGORIES):
            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Cumulative Reward ad {ad_id}, cat {category}")
            plt.plot(np.cumsum(plot_rewards_bandit[ad_id][category]), 'r')
            plt.plot(np.cumsum(plot_rewards_random[ad_id][category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Cumulative Regret ad {ad_id}, cat {category}")
            plt.plot(np.cumsum(plot_regret_bandit[ad_id][category]), 'r')
            plt.plot(np.cumsum(plot_regret_random[ad_id][category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

    print('true quality values:')
    for advertiser in advertisers:
        print(advertiser.id, advertiser.ad.real_qualities)

# Print gain of advertisers.
gain_of_greedy = greedy_learner.daily_gain_history
gains_of_stochastic = []
for stochastic_advertiser in stochastic_advertisers:
    gains_of_stochastic.append(stochastic_advertiser.daily_gain_history)

mean_gain_of_stochastic = np.mean(gains_of_stochastic, axis=0)

plt.figure(fig)
fig += 1
plt.xlabel("t")
plt.ylabel("Cumulative Gain")
plt.plot(np.cumsum(gain_of_greedy), 'r')
plt.plot(np.cumsum(mean_gain_of_stochastic), 'g')
plt.legend(["Greedy", "Mean Gain of Stochastic advs"])
plt.show()
