import Network
import influenceEstimation
import constants as const
from auction.vcg_auction import VCGAuction
from typing import List
from ad import Ad
from slot import Slot


class Publisher:

    def __init__(self, network: Network):
        self.network = network
        self.auctions = []
        self.slates = [[] for _ in range(const.CATEGORIES)]
        # todo set the id and the prominance
        for i in range(const.CATEGORIES):
            for id in range(const.SLATE_DIMENSION):
                self.slates[i].append(Slot(id, 0.5))

    # Create an auction for each category and get the relative slate
    def generate_auctions(self, available_ads: List[Ad]):
        for i in range(const.CATEGORIES):
            # todo: dove vengono differenziate le diverse auctions?
            self.auctions.append(VCGAuction(available_ads, self.slates[i]))
            self.slates[i] = self.auctions[i].perform_auction()

    # Play a round for a given category, return the number of seeds and the number of activated nodes
    # The activated nodes is the average number of activated nodes given the seeds, as computed in influenceEstimation
    # todo : how can we return the average of the seeds?
    # todo : is it possible to produce the average number of estimated nodes without a specific instantiation of seeds?
    def play_round(self, category):
        # [[]] -> [advertiser (with respect to slot position), seeds/activated_nodes]
        seeds = [[] for _ in range(const.SLATE_DIMENSION)]
        activated_nodes = [[] for _ in range(const.SLATE_DIMENSION)]
        for node in self.network.nodes:
            if node.category == category:
                clicked_slot = node.show_ad(self.slates[category])
                if clicked_slot >= 0:
                    seeds[clicked_slot].append(node)

        for ad in range(const.SLATE_DIMENSION):
            activated_nodes[ad] = influenceEstimation.calculateActivations(seeds=seeds[ad])

        return len(seeds), activated_nodes

    # Given an advertiser, a category and the number of seeds, return the cost of the auction
    def get_cost(self, advertiser, category, number_of_seeds):
        for slot in self.slates[category]:
            if slot.assigned_ad == advertiser:
                return slot.price_per_click * number_of_seeds







