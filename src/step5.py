from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher
from random import random

# create context
network_instance = network.Network(1000, False)
stochastic_advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(constants.SLATE_DIMENSION + 1)]
# TODO greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(constants.CATEGORIES)], ad_value=1, network=network_instance)
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
# TODO advertisers.append(greedy_learner)
publisher = Publisher(network=network_instance, advertisers=advertisers, bandit_type_qualities=BanditTypeEnum.THOMPSON_SAMPLING,
                      bandit_type_activations=BanditTypeEnum.THOMPSON_SAMPLING, window_size=None)

nodes_per_category = network_instance.network_report()

sample_estimated_qualities = {}
for advertiser in advertisers:
    ad_id = advertiser.id
    sample_estimated_qualities[ad_id] = {}
    for category in range(constants.CATEGORIES):
        sample_estimated_qualities[ad_id][category] = {}
        sample_estimated_qualities[ad_id][category]['estimate'] = 0
        sample_estimated_qualities[ad_id][category]['number_of_samples'] = 0

bandit_estimated_activations = {}
for from_category in range(constants.CATEGORIES):
    bandit_estimated_activations[from_category] = {}
    for to_category in range(constants.CATEGORIES):
        bandit_estimated_activations[from_category][to_category] = {}
        bandit_estimated_activations[from_category][to_category] = random()

for day in range(10):
    # get current quality estimates
    bandit_estimated_qualities = publisher.get_bandit_qualities()
    bandit_estimated_activations = publisher.get_bandit_activations()
    # pass estimates
    for advertiser in advertisers:
        # pass quality estimates to ads
        ad = advertiser.ad
        estimated_q = bandit_estimated_qualities[ad.ad_id]
        ad.set_estimated_qualities(estimated_q)
        # pass activation estimates to the advertisers
        advertiser.estimated_activations = bandit_estimated_activations
    # set context for simulation for calculating best bids
    # TODO greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in stochastic_advertisers])
    slates = constants.get_slates()
    # TODO greedy_learner.set_slates(slates=slates)
    # calculate bids by simulation
    # print('calculating bids ...')
    # TODO greedy_ad = greedy_learner.participate_auction()
    # print('finish calculating bids')
    # do environment sample
    ads = []
    for advertiser in advertisers:
        ads.append(advertiser.ad)
    social_influence = AdPlacementSimulator.simulate_ad_placement(
        network=network_instance,
        ads=ads,
        slates=slates,
        iterations=1,  # iterations = 1 means network sample
        use_estimated_qualities=False,  # use_estimated_qualities=False means true qualities from real network
        estimated_activations=None   # use_estimated_activations=None means true activations from real network
    )

    # do rewards and bandit update
    rewards = {}

    for ad_id in social_influence.keys():
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
            # print(f"current sample estimate:{sample_estimated_qualities[ad.ad_id][category]['estimate']}   "
            #       f"number of samples:{sample_estimated_qualities[ad.ad_id][category]['number_of_samples']}   "
            #       f"new sample: {(number_of_seeds / susceptible_nodes)}   "
            #       f"number of seeds: {number_of_seeds}   susceptible nodes: {susceptible_nodes}   "
            #       f"slot prominence: {slot.slot_prominence}   "
            #       f"ad id: {ad.ad_id}")
            old_estimate = sample_estimated_qualities[ad.ad_id][category]['estimate']
            number_of_samples = sample_estimated_qualities[ad.ad_id][category]['number_of_samples']
            new_sample = (number_of_seeds / susceptible_nodes) / constants.SLOT_VISIBILITY
            # new_sample = (number_of_seeds / nodes_per_category[category]) / slot.slot_prominence
            estimated_quality = (old_estimate * number_of_samples + new_sample) / (number_of_samples + 1)

            sample_estimated_qualities[ad.ad_id][category]['number_of_samples'] += 1
            sample_estimated_qualities[ad.ad_id][category]['estimate'] = estimated_quality
            susceptible_nodes -= number_of_seeds
            if susceptible_nodes <= 0:
                break
            error = abs(new_sample - bandit_estimated_qualities[ad.ad_id][category])

            if error <= 1 / constants.number_of_bandit_arms:
                rewards[ad.ad_id][category] = 1
            else:
                rewards[ad.ad_id][category] = 0

            real_error = abs(slot.assigned_ad.real_quality - bandit_estimated_qualities[ad.ad_id][category])
            plot_regret_bandit[ad.ad_id][category] = real_error
            plot_rewards_bandit[ad.ad_id][category] = 1 - real_error
            random_regret = random.uniform(0, 1)
            plot_regret_random[ad.ad_id][category] = random_regret
            plot_rewards_random[ad.ad_id][category] = 1 - random_regret

            if learn_from_first_slot_only:
                break

    # update bandits with rewards
    publisher.update_bandits_quality(rewards=rewards)



