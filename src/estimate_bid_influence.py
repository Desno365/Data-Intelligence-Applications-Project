import network
import advertiser
isFullyConnected = False
numberOfNodes = 100
adQuality = 0.1
network = network.Network(numberOfNodes, isFullyConnected)

advertisers = [advertiser.Advertiser() for _ in range(2)]
for advertiser in advertisers:
    advertiser.set_random_bids()
    print(advertiser.bids)

result = network.MC_pseudoNodes_freshSeeds(adQuality, 10)
print(result)
