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
