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
from src import constants, network
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.advertiser.stochastic_stationary_advertiser import StochasticStationaryAdvertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.publisher import Publisher

# create context
network_instance = network.Network(50, False)
advertisers = [StochasticStationaryAdvertiser(quality=None) for _ in range(7)]
greedy_learner = GreedyLearningAdvertiser(quality=[1 for _ in range(5)], value=1, network=network_instance)
advertisers.append(greedy_learner)
publisher = Publisher(network=network, advertisers=advertisers, bandit_type=BanditTypeEnum.UCB1, window_size=None)

# get current quality estimate
qualities = publisher.get_bandit_qualities()
for ad_id in qualities.keys():
    print('ad_id: ', ad_id, 'qualities: ', qualities[ad_id])

# pass qualities to advertiser
greedy_learner.qualities = qualities

# calculate bids by simulation
greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in advertisers])
slates = constants.get_slates()
greedy_learner.set_slates(slates=slates)
print('calculating bids ...')
print('first auction')
greedy_ad = greedy_learner.participate_auction()
print('second auction')
greedy_ad = greedy_learner.participate_auction()


# advertisers pass bids to publisher
# publisher makes real auctions to get real slates
# pensavo di fare separati questo punto e quello dopo
# ma in simulate ad placement viene già fatto tutto quindi uso quello
ads = []
for advertiser in advertisers:
    ads.append(advertiser.ad)
social_influence = AdPlacementSimulator.simulate_ad_placement(
    network=network_instance, ads=ads,
    slates=constants.get_slates(),
    iterations=1,  # iterations = 1 means network sample
    qualities=None)  # qualities=None means true qualities from real network

# get rewards from real environment using real slates
# rewards = publisher.real_network_sample(slates=slates)
# print(rewards)
nodes_per_category = network_instance.network_report()
rewards = {}
print('bandit rewards for quality estimates')
for ad_id in social_influence.keys():
    rewards[ad_id] = {}
    for category in range(constants.CATEGORIES):
        estimate_error = (qualities[ad_id][category] - (social_influence[ad_id][category]['seeds'] / nodes_per_category[category]))**2
        if estimate_error == 0:
            estimate_error = 0.0001
        rewards[ad_id][category] = 1 / estimate_error
    print('ad_id: ', ad_id, 'reward: ', rewards[ad_id])

# update bandits with rewards
publisher.update_bandits(rewards=rewards)

print('qualities after one step of improvement')
qualities = publisher.get_bandit_qualities()
for ad_id in qualities.keys():
    print('ad_id: ', ad_id, 'qualities: ', qualities[ad_id])

# for day in range(10):
#     print('#######################day', day)
#     greedy_learner.qualities = qualities
#     # # calculate bids by simulation
#     # greedy_learner.set_rival_ads(rival_ads=[advertiser.ad for advertiser in advertisers])
#     # slates = constants.get_slates()
#     # greedy_learner.set_slates(slates=slates)
#     print('calculating bids ...')
#     greedy_ad = greedy_learner.participate_auction()
#     # do environment sample
#     ads = []
#     for advertiser in advertisers:
#         ads.append(advertiser.ad)
#     social_influence = AdPlacementSimulator.simulate_ad_placement(
#         network=network_instance, ads=ads,
#         slates=constants.get_slates(),
#         iterations=1,  # iterations = 1 means network sample
#         qualities=None)  # qualities=None means true qualities from real network
#
#     # do rewards and bandit update
#     rewards = {}
#     print('bandit rewards for quality estimates')
#     for ad_id in social_influence.keys():
#         rewards[ad_id] = {}
#         for category in range(constants.CATEGORIES):
#             estimate_error = (qualities[ad_id][category] - (
#                         social_influence[ad_id][category]['seeds'] / nodes_per_category[category])) ** 2
#             if estimate_error == 0:
#                 estimate_error = 0.0001
#             rewards[ad_id][category] = 1 / estimate_error
#         print('ad_id: ', ad_id, 'reward: ', rewards[ad_id])
#
#     # update bandits with rewards
#     publisher.update_bandits(rewards=rewards)
#
#     print('qualities after one step of improvement')
#     qualities = publisher.get_bandit_qualities()
#     for ad_id in qualities.keys():
#         print('ad_id: ', ad_id, 'qualities: ', qualities[ad_id])
