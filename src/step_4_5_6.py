import random
from datetime import datetime

import numpy as np
from matplotlib import pyplot as plt

from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_non_stationary_advertiser import StochasticNonStationaryAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher


# ################ Constants. ################ #
NUMBER_OF_DAYS = 100  # Days for the run.
NUMBER_OF_STOCHASTIC_ADVERTISERS = constants.SLATE_DIMENSION + 1
LEARN_QUALITIES = True  # True to learn qualities, False to use real qualities.
LEARN_ACTIVATIONS = False  # True to learn activation probabilities, False to use real activation probabilities.
USE_GREEDY_ADVERTISER = True  # True to enable the Greedy Advertiser, False to only use Stochastic Advertisers.
LEARN_FROM_FIRST_SLOT_ONLY = True  # True to learn only from first slot of slate, False to learn from all slots.
BANDIT_TYPE_FOR_QUALITIES = BanditTypeEnum.UCB1  # Bandit to be used for qualities.
BANDIT_TYPE_FOR_ACTIVATIONS = BanditTypeEnum.UCB1  # Bandit to be used for activations.
USE_NON_STATIONARY_ADVERTISERS = False  # True to use Non-Stationary Stochastic Advertisers, False to use Stationary Stochastic Advertisers.
SLIDING_WINDOW_SIZE = 100  # The size of the sliding window for bandit algorithms that have this parameter.
ABRUPT_CHANGE_INTERVAL = 100  # Abrupt change interval for Non-Stationary Stochastic Advertisers.


# ################ Prepare context: Network. ################ #
network_instance = network.Network(constants.number_of_nodes, False)
nodes_per_category = network_instance.network_report()


# ################ Prepare context: Advertisers. ################ #
if USE_NON_STATIONARY_ADVERTISERS:
    stochastic_advertisers = [StochasticNonStationaryAdvertiser(n=ABRUPT_CHANGE_INTERVAL) for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
else:
    stochastic_advertisers = [StochasticStationaryAdvertiser() for _ in range(NUMBER_OF_STOCHASTIC_ADVERTISERS)]
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
if USE_GREEDY_ADVERTISER:
    greedy_learner = GreedyLearningAdvertiser(network=network_instance, use_estimated_activations=LEARN_ACTIVATIONS,
                                              ad_real_qualities=[random.random() for _ in range(constants.CATEGORIES)],
                                              ad_value=1)
    advertisers.append(greedy_learner)


# ################ Prepare context: Publisher. ################ #
publisher = Publisher(
    network=network_instance,
    advertisers=advertisers,
    bandit_type_qualities=BANDIT_TYPE_FOR_QUALITIES,
    bandit_type_activations=BANDIT_TYPE_FOR_ACTIVATIONS,
    window_size=SLIDING_WINDOW_SIZE
)

# ################ Prepare variables for plotting. ################ #
if LEARN_ACTIVATIONS:
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
if LEARN_QUALITIES:
    plot_rewards_bandit_quality = {}
    plot_regret_bandit_quality = {}
    plot_rewards_random_quality = {}
    plot_regret_random_quality = {}
    for advertiser in advertisers:
        ad_id = advertiser.id
        plot_rewards_bandit_quality[ad_id] = {}
        plot_regret_bandit_quality[ad_id] = {}
        plot_rewards_random_quality[ad_id] = {}
        plot_regret_random_quality[ad_id] = {}
        for category in range(constants.CATEGORIES):
            plot_rewards_bandit_quality[ad_id][category] = np.array([])
            plot_regret_bandit_quality[ad_id][category] = np.array([])
            plot_rewards_random_quality[ad_id][category] = np.array([])
            plot_regret_random_quality[ad_id][category] = np.array([])
if USE_GREEDY_ADVERTISER:
    gain_history_greedy = []
    gain_history_stochastics = {}
    for advertiser in advertisers:
        gain_history_stochastics[advertiser.id] = []

for day in range(NUMBER_OF_DAYS):
    print('Running day', day)
    # get current quality estimates
    bandit_estimated_qualities = publisher.get_bandit_qualities()
    bandit_estimated_activations = publisher.get_bandit_activations()
    for from_category in range(len(bandit_estimated_activations)):
        print('from cat: ', from_category, 'bandit estimated activations: ', bandit_estimated_activations[from_category])

    # pass quality estimations to ads
    for advertiser in advertisers:
        ad = advertiser.ad
        estimated_qualities_dict = bandit_estimated_qualities[ad.ad_id]
        estimated_qualities_list = [estimated_qualities_dict[x] for x in estimated_qualities_dict]
        ad.set_estimated_qualities(estimated_qualities_list)
    # pass activations estimations to greedy advertiser
    if USE_GREEDY_ADVERTISER:
        greedy_learner.set_estimated_activations(bandit_estimated_activations)
    # set context for simulation for calculating best bids
    slates = constants.slates
    if USE_GREEDY_ADVERTISER:
        greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in stochastic_advertisers])
        greedy_learner.set_slates(slates=slates)
    # do environment sample
    ads = []
    greedy_simulation_start = datetime.now()
    for advertiser in advertisers:
        ads.append(advertiser.participate_real_auction())  # Here the greedy learner will compute its best bids.
    print(f'calculated bids in {datetime.now() - greedy_simulation_start}')
    time = datetime.now()
    social_influence = AdPlacementSimulator.simulate_ad_placement(
        network=network_instance,
        ads=ads,
        slates=slates,
        iterations=1,  # iterations = 1 means network sample
        use_estimated_qualities=False,
        use_estimated_activations=False,
        estimated_activations=None,
    )

    if USE_GREEDY_ADVERTISER:
        for advertiser in advertisers:
            ad_id = advertiser.id
            gain = 0
            if ad_id in social_influence.keys():
                for category in range(constants.CATEGORIES):
                    ad_category_info = social_influence[ad_id][category].copy()
                    gain += advertiser.ad_value * ad_category_info["activatedNodes"] - ad_category_info["price"] * ad_category_info["seeds"]
                    if ad_id == greedy_learner.id:
                        print(f'\t Seeds: {ad_category_info["seeds"]} - Activations: {ad_category_info["activatedNodes"]} - PPC: {ad_category_info["price"]}')
            if ad_id == greedy_learner.id:
                gain_history_greedy.append(gain)
            else:
                gain_history_stochastics[ad_id].append(gain)

    elapsed_time = datetime.now() - time
    print(f'environment sample time {elapsed_time}')

    # Report results to advertisers
    for advertiser in advertisers:
        advertiser.report_daily_results(social_influence=social_influence)

    if LEARN_QUALITIES:
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
                if susceptible_nodes <= constants.number_of_bandit_arms_qualities:
                    print("Not enough samples.")
                    break
                error = abs(measured_quality - bandit_estimated_qualities[ad.ad_id][category])
                if error <= 1 / constants.number_of_bandit_arms_qualities:
                    rewards_qualities[ad.ad_id][category] = 1
                else:
                    rewards_qualities[ad.ad_id][category] = 0
                real_error = abs(slot.assigned_ad.real_quality - bandit_estimated_qualities[ad.ad_id][category])
                plot_regret_bandit_quality[ad.ad_id][category] = np.append(plot_regret_bandit_quality[ad.ad_id][category], real_error)
                plot_rewards_bandit_quality[ad.ad_id][category] = np.append(plot_rewards_bandit_quality[ad.ad_id][category], 1 - real_error)
                random_estimated_quality = random.choice(constants.bandit_quality_values)
                random_regret = abs(slot.assigned_ad.real_quality - random_estimated_quality)
                plot_regret_random_quality[ad.ad_id][category] = np.append(plot_regret_random_quality[ad.ad_id][category], random_regret)
                plot_rewards_random_quality[ad.ad_id][category] = np.append(plot_rewards_random_quality[ad.ad_id][category], 1 - random_regret)
                if LEARN_FROM_FIRST_SLOT_ONLY:
                    break

        # update bandits with rewards
        publisher.update_bandits_quality(rewards=rewards_qualities)
    if LEARN_ACTIVATIONS:
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

                if error_activation <= constants.bandit_activation_values[0]:  # Range of activations is NOT [0, 1]!
                    rewards_activations[from_category][to_category] = 1
                else:
                    rewards_activations[from_category][to_category] = 0

                real_error_activation = abs(network_instance.weight_matrix[from_category][to_category] - bandit_estimated_activations[from_category][to_category])
                plot_regret_bandit_activation[from_category][to_category] = np.append(plot_regret_bandit_activation[from_category][to_category], real_error_activation)
                plot_rewards_bandit_activation[from_category][to_category] = np.append(plot_rewards_bandit_activation[from_category][to_category], 1 - (real_error_activation / constants.bandit_activation_values[-1]))

                random_estimated_activation = random.choice(constants.bandit_activation_values)
                random_regret_activation = abs(network_instance.weight_matrix[from_category][to_category] - random_estimated_activation)

                plot_regret_random_activation[from_category][to_category] = np.append(plot_regret_random_activation[from_category][to_category], random_regret_activation)
                plot_rewards_random_activation[from_category][to_category] = np.append(plot_rewards_random_activation[from_category][to_category], 1 - (random_regret_activation / constants.bandit_activation_values[-1]))
        # update bandits with rewards
        publisher.update_bandits_activations(rewards=rewards_activations)


fig = 0
'''
if LEARN_ACTIVATIONS:
    # # Create plot for activations
    # # Note: one experiment = one bandit (one bandit for each category and for each advertiser)
    for from_category in range(constants.CATEGORIES):
        for to_category in range(constants.CATEGORIES):
            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Activation Reward from category {from_category}, to cat {to_category}")
            plt.plot(np.cumsum(plot_rewards_bandit_activation[from_category][to_category]), 'r')
            plt.plot(np.cumsum(plot_rewards_random_activation[from_category][to_category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Activation Regret from category {from_category}, to cat {to_category}")
            plt.plot(np.cumsum(plot_regret_bandit_activation[from_category][to_category]), 'r')
            plt.plot(np.cumsum(plot_regret_random_activation[from_category][to_category]), 'g')
            plt.legend(["Bandit", "Random"])
            plt.show()

    print('true activation values:')
    for from_category in range(constants.CATEGORIES):
        print(network_instance.weight_matrix[from_category][:])
'''

if LEARN_QUALITIES:
    # Create plot for qualities
    # Note: one experiment = one bandit (one bandit for each category and for each advertiser)
    for advertiser in advertisers:
        ad_id = advertiser.id
        for category in range(constants.CATEGORIES):
            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Cumulative Quality Reward ad {ad_id}, cat {category}")
            plt.plot(np.cumsum(plot_rewards_bandit_quality[ad_id][category]), 'g')
            plt.plot(np.cumsum(plot_rewards_random_quality[ad_id][category]), 'r')
            plt.legend(["Bandit", "Random"])
            plt.show()

            plt.figure(fig)
            fig += 1
            plt.xlabel("t")
            plt.ylabel(f"Cumulative Quality Regret ad {ad_id}, cat {category}")
            plt.plot(np.cumsum(plot_regret_bandit_quality[ad_id][category]), 'g')
            plt.plot(np.cumsum(plot_regret_random_quality[ad_id][category]), 'r')
            #if USE_NON_STATIONARY_ADVERTISERS:
            #    for i in range(NUMBER_OF_DAYS):
            #        i = i + 1
            #        if i % ABRUPT_CHANGE_INTERVAL == 0:
            #            plt.axvline(x=i)
            plt.legend(["Bandit", "Random"])
            plt.show()

    print('true quality values:')
    for advertiser in advertisers:
        print(advertiser.id, advertiser.ad.real_qualities)

# Print gain of advertisers.
if USE_GREEDY_ADVERTISER:
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

    plt.figure(fig)
    fig += 1
    plt.title('Gain History')
    plt.xlabel("Day")
    plt.ylabel("Gain history")
    plt.plot(gain_history_greedy, 'g')
    for advertiser in advertisers:
        rgb = (random.random(), random.random(), random.random())
        if advertiser.id != greedy_learner.id:
            plt.plot(gain_history_stochastics[advertiser.id], color=rgb)
    plt.plot(gain_history_greedy, 'g')
    plt.legend(["Greedy"])
    plt.show()
