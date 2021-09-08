from typing import List

from src.ad import Ad
from src.auction.auction_ad import AuctionAd
from src.auction.vcg_auction import VCGAuction
from src.constants import CATEGORIES
from src.slot import Slot
from src.utils import Utils


class AdPlacementSimulator:

    @staticmethod
    # ads = the list of ads available, every ad comes from an advertiser.
    # slates = the list of slates, one slate per category (a slate is a list of slots).
    # iterations = number of iterations for the Monte Carlo simulation
    def simulate_ad_placement(network: Network, ads: List[Ad], slates: List[List[Slot]], iterations: int):

        # The auction must be simulated for each category.
        for current_category in range(CATEGORIES):
            # For each category we need to perform an auction.
            # The auction needs the bid and quality of all the ads for that category.
            # The auction also need the slate of the category.
            # Note: the slot prominence is equal for all slate, the only thing changing is the slot object itself.
            # The auction then will return the slate itself but with an ad and price assigned to every slot.
            auction_ads_for_the_category = []
            for ad in ads:
                new_auction_ad = AuctionAd(ad_id=ad.ad_id, ad_quality=ad.ad_quality[current_category], ad_bid=ad.ad_value)
                auction_ads_for_the_category.append(new_auction_ad)

            slate_of_the_category = slates[current_category]
            vcg_auction = VCGAuction(available_ads=auction_ads_for_the_category, slate=slate_of_the_category)
            slate_with_assigned_ads = vcg_auction.perform_auction()
            Utils.print_array(slate_with_assigned_ads)

            # Overwrite information of the slate with the new assigned slate.
            # Now we have ready the slate of the current category with all the information needed.
            slates[current_category] = slate_with_assigned_ads

        # TODO: for monte carlo use the "slates" variable
        # Monte Carlo:
        # Input: lista di slate con pubblicità assegnate e prezzi.
        # Ouput: dictionary che per ogni ad_id (univoco per advertiser) specifica numero medio di seed e nodi attivati.
        # Nota quindi: dividere per ad_id è equivalente a dividere per advertiser.
        # return dictionary
        # Monte Carlo simulation:

        social_influence = network.estimateSocialInfluence(iterations=iterations, slates=slates)

        return social_influence
