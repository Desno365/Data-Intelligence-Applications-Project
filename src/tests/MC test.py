from src import bids_enum, slot, network
from src.auction import auction_ad, vcg_auction

bid = bids_enum.BidsEnum.MAX.value
bid1 = bids_enum.BidsEnum.MEDIUM.value
bid2 = bids_enum.BidsEnum.OFF.value
# advertisements = [ad.Ad(0, [0.2,0.1,0.1,0.1,0.1], 1, [bid]),
#                   ad.Ad(1, [0.1,0.1,0.1,0.1,0.1], 1, [bid]),
#                   ad.Ad(2, [0.1,0.1,0.1,0.1,0.1], 1, [bid])]
auction_ads = [auction_ad.AuctionAd(0, 1, bid),
               auction_ad.AuctionAd(1, 0.1, bid),
               auction_ad.AuctionAd(2, 0.3, bid)]
slate = [slot.Slot(0, 0.5),
         slot.Slot(1, 0.3)]
slate1 = [slot.Slot(0, 0.6),
          slot.Slot(1, 0.5)]
a = vcg_auction.VCGAuction(auction_ads, slate)
slate = a.perform_auction()
# b = vcg_auction.VCGAuction(advertisements, slate1)
# slate1 = b.perform_auction()
# print('the slate', slate)
# print('the slots\n', slate[0], '\n', slate[1])
#
network_instance = network.Network(50, False)
# result = network_instance.MC_pseudoNodes_freshSeeds([1, 1, 1, 1, 1], slates=[slate, slate, slate1, slate, slate])
# print(result)

# result = network_instance.estimateSocialInfluence(iterations=50, slates=[slate, slate, slate, slate, slate])
# print(result)
social_influence = network_instance.estimateSocialInfluence(iterations=50, slates=[slate, slate, slate, slate, slate])
print(social_influence)
