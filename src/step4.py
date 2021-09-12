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
from datetime import datetime

from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher

# create context
network_instance = network.Network(100, False)
stochastic_advertisers = [StochasticStationaryAdvertiser(ad_real_qualities=None) for _ in range(constants.SLATE_DIMENSION)]
greedy_learner = GreedyLearningAdvertiser(ad_real_qualities=[1 for _ in range(5)], ad_value=1, network=network_instance)
advertisers = []
for stochastic_advertiser in stochastic_advertisers:
    advertisers.append(stochastic_advertiser)
advertisers.append(greedy_learner)
publisher = Publisher(network=network, advertisers=advertisers, bandit_type=BanditTypeEnum.UCB1, window_size=None)

nodes_per_category = network_instance.network_report()

sample_estimated_qualities = {}
for advertiser in advertisers:
    ad_id = advertiser.id
    sample_estimated_qualities[ad_id] = {}
    for category in range(constants.CATEGORIES):
        sample_estimated_qualities[ad_id][category] = {}
        sample_estimated_qualities[ad_id][category]['estimate'] = 0
        sample_estimated_qualities[ad_id][category]['number_of_samples'] = 0

time = datetime.now()
for day in range(200):
    print('#######################day', day)
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
    greedy_learner.qualities = bandit_estimated_qualities
    # set context for simulation for calculating best bids
    greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in stochastic_advertisers])
    slates = constants.get_slates()
    greedy_learner.set_slates(slates=slates)
    # calculate bids by simulation
    print('calculating bids ...')
    greedy_ad = greedy_learner.participate_auction()
    print('finish calculating bids')
    # do environment sample
    ads = []
    for advertiser in advertisers:
        ads.append(advertiser.ad)
    social_influence = AdPlacementSimulator.simulate_ad_placement(
        network=network_instance, ads=ads,
        slates=constants.get_slates(),
        iterations=1,  # iterations = 1 means network sample
        use_estimated_qualities=False,  # use_estimated_qualities=False means true qualities from real network
        use_estimated_activations=False)   # use_estimated_activations=False means true activations from real network

    # do rewards and bandit update
    rewards = {}
    for ad_id in social_influence.keys():
        rewards[ad_id] = {}
        for category in range(constants.CATEGORIES):
            rewards[ad_id][category] = 0
    # calculate rewards
    # print('bandit rewards for quality estimates')
    # for ad_id in social_influence.keys():
    #     rewards[ad_id] = {}
    #     for category in range(constants.CATEGORIES):
    #         # sliding window with length 1
    #         # estimated_quality = (social_influence[ad_id][category]['seeds'] / nodes_per_category[category])
    #         # moving average formula
    #         estimated_qualities[ad_id][category] = ((estimated_qualities[ad_id][category] * day) + (social_influence[ad_id][category]['seeds'] / nodes_per_category[category])) / (day + 1)
    #         print(f'ad_id {ad_id}, category : {category}, est_q {estimated_qualities[ad_id][category]}')
    #         estimate_error = abs(qualities[ad_id][category] - estimated_qualities[ad_id][category])
    #         # using true quality is cheating
    #         # true_quality = list(filter(lambda item: item.id == ad_id, advertisers))[0].adquality
    #         # estimate_error = (qualities[ad_id][category] - true_quality[category])**2
    #         # print(f'error: {estimate_error}')
    #         if estimate_error <= 0.0001:
    #             estimate_error = 0.0001
    #         rewards[ad_id][category] = 1 / estimate_error
    #     print('ad_id: ', ad_id, 'reward: ', rewards[ad_id])
    # calculate rewards but better
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
            new_sample = (number_of_seeds / susceptible_nodes) / slot.slot_prominence
            estimated_quality = (old_estimate * number_of_samples + new_sample) / (number_of_samples + 1)

            sample_estimated_qualities[ad.ad_id][category]['number_of_samples'] += 1
            sample_estimated_qualities[ad.ad_id][category]['estimate'] = estimated_quality
            susceptible_nodes -= number_of_seeds
            if susceptible_nodes <= 0:
                break
            error = (sample_estimated_qualities[ad.ad_id][category]['estimate'] - bandit_estimated_qualities[ad.ad_id][category]) ** 2
            if error <= 0.001:
                error = 0.001
            rewards[ad.ad_id][category] = 1 / error


    # update bandits with rewards
    publisher.update_bandits_quality(rewards=rewards)

print('true quality values:')
for advertiser in advertisers:
    print(advertiser.id, advertiser.ad.real_qualities)

elapsed_time = datetime.now() - time
for ad_id in sample_estimated_qualities.keys():
    print(f'ad_id: {ad_id}, bids: {list(filter(lambda item: item.id == ad_id, advertisers))[0].ad.bids}')
    for category in range(constants.CATEGORIES):
        print(f'category: {category}, estimated q: {sample_estimated_qualities[ad_id][category]}')

print(sample_estimated_qualities)
print(f'elapsed time: {elapsed_time}')
