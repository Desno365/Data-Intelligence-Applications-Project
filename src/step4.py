# bandit learner for click probabilities in publisher (ad.ad_quality * slot.slot_prominence)
# arm = [click probability for ad in ads]
# len(ads) = len(advertisers)
# len(qualities) = len(ads) * constants.CATEGORIES
# does the publisher know the slot prominence values and ad placements so that we estimate only qualities?
# ad quality is constant, but slot prominence depends on ad placement and advertiser bids so it could in the worst case
# be different every time
# one bandit with many arms
# one bandit with arm = [[quality for _ in range(constants.CATEGORIES)] for _ in range(len(ads)]
# or
# many bandits with fewer arms (one bandit for every ad)
# len(ads) = len(bandits) with arm = [quality for _ in range(constants.CATEGORIES)]
# individual click probability values are i in range(0, 1.1, 0.1), 11 values total
# number of arms is 11**len(ads)
# pass click probability to advertiser
# advertiser passes click probability to monte carlo
# if click probability = None then
# MC would use activation_probability = current_ad.ad_quality * position.slot_prominence
# otherwise use activation_probability = click probability input argument
