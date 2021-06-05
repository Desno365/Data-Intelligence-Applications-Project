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
        # todo set the id and the prominence
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
    # todo : need to be fixed to perform an actual auction if needed
    def play_round(self, category, advertiser, iteration_for_average=30):
        # [[]] -> [advertiser (with respect to slot position), seeds/activated_nodes]
        seeds = [[] for _ in range(const.SLATE_DIMENSION)]
        activated_nodes = [[] for _ in range(const.SLATE_DIMENSION)]
        for node in self.network.nodes:
            if node.category == category:
                clicked_slot = node.show_ad(self.slates[category])
                if clicked_slot >= 0:
                    seeds[clicked_slot].append(node)

        for ad in range(const.SLATE_DIMENSION):
            activated_nodes[ad] = self.network.monteCarloEstimation(seeds=seeds[ad], iterations=30)

        return len(seeds), activated_nodes

    # Get the expected number of seeds and activated nodes for an auction
    # The function refer to the auctions currently saved in the publisher, with function generate_auctions
    # Input: category (the auction to check), advertiser (the advertiser to monitor), iterations (number of iterations
    # for the average)
    # Output: average number of seeds , average number of activated nodes
    def estimate_auction_effect(self, category: int, advertiser, iterations=15):
        avg_seeds = 0
        avg_activated_nodes = 0
        for _ in range(iterations):
            seeds = []
            for node in self.network.nodes:
                if node.category == category:
                    clicked_slot = node.show_ad(self.slates[category])
                    if clicked_slot >= 0 and self.slates[category][clicked_slot].assinged_ad == advertiser:
                        seeds.append(node)
            activated_nodes, node_activation_probabilities = influenceEstimation.monteCarloEstimation(
                seeds=seeds, iterations=iterations)

            avg_seeds += len(seeds)
            avg_activated_nodes += activated_nodes

        return avg_seeds/iterations, avg_activated_nodes/iterations

    # Given an advertiser, a category and the number of seeds, return the cost of the auction
    def get_cost(self, advertiser, category: int, number_of_seeds):
        for slot in self.slates[category]:
            if slot.assigned_ad == advertiser:
                return slot.price_per_click * number_of_seeds







