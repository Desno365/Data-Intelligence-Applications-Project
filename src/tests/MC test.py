from src import bids_enum, slot, network
from src.auction import auction_ad
from src.auction.vcg_auction import VCGAuction

network_instance = network.Network(50, False)

social_influence = network_instance.estimateSocialInfluence(slates=[slate, slate, slate, slate, slate], iterations=50, use_estimated_qualities=False, use_estimated_activation_probabilities=False)
print(social_influence)
