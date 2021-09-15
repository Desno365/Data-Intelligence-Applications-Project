from datetime import datetime
from typing import List, Dict

from src import constants
from src.ad import Ad
from src.auction.auction_ad import AuctionAd
from src.auction.vcg_auction import VCGAuction
from src.network import Network
from src.slot import Slot


class AdPlacementSimulator:

    @staticmethod
    def simulate_ad_placement(
            network: Network,  # the network of nodes.
            ads: List[Ad],  # the list of ads available, every ad comes from an advertiser.
            slates: List[List[Slot]],  # the list of slates, one slate per category (a slate is a list of slots).
            use_estimated_qualities: bool = False,  # true to use estimated qualities, false to use real qualities.
            use_estimated_activations: bool = False,  # true to use estimated activations, false to use real one
            estimated_activations: List[List[float]] = None,  # the estimated activation to use
            iterations: int = 100,  # number of iterations for the Monte Carlo simulation.
    ) -> Dict[int, Dict[int, Dict]]:
        assert len(slates) == constants.CATEGORIES
        assert iterations > 0

        # The auction must be simulated for each category.
        for current_category in range(constants.CATEGORIES):
            # For each category we need to perform an auction.
            # The auction needs the bid and quality of all the ads for that category.
            # The auction also need the slate of the category.
            # Note: the slot prominence is equal for all slate, the only thing changing is the slot object itself.
            # The auction then will return the slate itself but with an ad and price assigned to every slot.
            auction_ads_for_the_category = []
            for ad in ads:
                new_auction_ad = AuctionAd(
                    ad_id=ad.ad_id,
                    estimated_quality=ad.estimated_qualities[current_category],
                    real_quality=ad.real_qualities[current_category],
                    bid=ad.bids[current_category].value
                )
                auction_ads_for_the_category.append(new_auction_ad)
            slate_of_the_category = slates[current_category]
            slate_with_assigned_ads = VCGAuction.perform_auction(available_ads=auction_ads_for_the_category, slate=slate_of_the_category)
            # Utils.print_array(slate_with_assigned_ads)
            # Overwrite information of the slate with the new assigned slate.
            # Now we have ready the slate of the current category with all the information needed.
            slates[current_category] = slate_with_assigned_ads

        # Monte Carlo simulation:
        # Input: all the slates (one slate per category) with the assigned ads.
        # Output: dictionary with ad_id keys (uniquely identifies advertiser) specifying the average number of seeds
        # and activated nodes
        # Note: having the division by ad_id is equivalent as dividing by advertiser since every advertiser has one ad.
        if constants.settings['executionTimePrint']:
            time = datetime.now()
        if not use_estimated_activations:
            estimated_activations = None
        social_influence = network.estimateSocialInfluence(slates=slates,
                                                           iterations=iterations,
                                                           use_estimated_qualities=use_estimated_qualities,
                                                           estimated_activation_probabilities=estimated_activations)
        if constants.settings['executionTimePrint']:
            print('estimate social influence', datetime.now()-time)
        #network.prettyPrintSocialInfluence(social_influence)

        # Set price to zero for all:
        for ad_id in social_influence.keys():
            for current_category in social_influence[ad_id].keys():
                social_influence[ad_id][current_category]["price"] = 0.0

        # Add price information:
        for current_category in range(constants.CATEGORIES):
            slate_of_the_category = slates[current_category]
            for slot in slate_of_the_category:
                social_influence[slot.assigned_ad.ad_id][current_category]["price"] = slot.price_per_click

        return social_influence
        # Social influence:
        # {
        #   ad_id: {
        #       category_id: {
        #           price: float
        #           seeds: float,
        #           activatedNodes: float
        #       }
        #   }
        # }

