import network
from src.advertiser import advertiser

isFullyConnected = False
numberOfNodes = 100
network = network.Network(numberOfNodes, isFullyConnected)

advertisers = [advertiser.Advertiser() for _ in range(2)]
for advertiser in advertisers:
    advertiser.set_random_bids()
    print('bids: ', advertiser.ad.bids)

result = network.estimateSocialInfluence(advertisers[0].ad_real_qualities, 10)
print('average activated nodes, seeds: ', result, ' / ', numberOfNodes)
