from typing import List

from src import constants
from src.advertiser.advertiser import Advertiser
from src.bandit_algorithms.bandit_type_enum import BanditTypeEnum
from src.network import Network


class Publisher:

    def __init__(self, network: Network, advertisers: List[Advertiser], bandit_type_qualities: BanditTypeEnum,
                 bandit_type_activations: BanditTypeEnum, window_size: int or None):
        self.network = network
        self.advertisers = advertisers
        self.auctions = []
        self.slates = constants.slates

        self.bandits_quality = {}
        # bandits: {
        #   ad_id: {
        #       category: {
        #           'bandit': BanditLearner
        #           'last_arm_pulled': int
        #       }
        #   }
        # }
        for advertiser in self.advertisers:
            self.bandits_quality[advertiser.ad.ad_id] = {}
            for category in range(constants.CATEGORIES):
                if category not in self.bandits_quality[advertiser.ad.ad_id].keys():
                    self.bandits_quality[advertiser.ad.ad_id][category] = {}
                bandit_learner = bandit_type_qualities.instantiate_bandit(n_arms=constants.number_of_bandit_arms, window_size=window_size)
                self.bandits_quality[advertiser.ad.ad_id][category]['bandit'] = bandit_learner

        self.bandits_activation = {}
        # bandits_prominance: {
        #   from_category: {
        #       to_category: {
        #           'bandit': BanditLearner
        #           'last_arm_pulled': int
        # }}}
        for from_category in range(constants.CATEGORIES):
            self.bandits_activation[from_category] = {}
            for to_category in range(constants.CATEGORIES):
                self.bandits_activation[from_category][to_category] = {}
                bandit_learner = bandit_type_activations.instantiate_bandit(n_arms=constants.number_of_bandit_arms, window_size=window_size)
                self.bandits_activation[from_category][to_category]['bandit'] = bandit_learner

    # # Create an auction for each category and get the relative slate
    # def generate_auctions(self, available_ads: List[Ad]):
    #     for i in range(const.CATEGORIES):
    #         # todo: dove vengono differenziate le diverse auctions?
    #         self.auctions.append(VCGAuction(available_ads, self.slates[i]))
    #         self.slates[i] = self.auctions[i].perform_auction()
    #
    # # Play a round for a given category, return the number of seeds and the number of activated nodes
    # # The activated nodes is the average number of activated nodes given the seeds, as computed in influenceEstimation
    # # todo : need to be fixed to perform an actual auction if needed
    # def play_round(self, category, advertiser, iteration_for_average=30):
    #     # [[]] -> [advertiser (with respect to slot position), seeds/activated_nodes]
    #     seeds = [[] for _ in range(const.SLATE_DIMENSION)]
    #     activated_nodes = [[] for _ in range(const.SLATE_DIMENSION)]
    #     for node in self.network.nodes:
    #         if node.category == category:
    #             clicked_slot = node.show_ad(self.slates[category])
    #             if clicked_slot >= 0:
    #                 seeds[clicked_slot].append(node)
    #
    #     for ad in range(const.SLATE_DIMENSION):
    #         activated_nodes[ad] = self.network.monteCarloEstimation(seeds=seeds[ad], iterations=30)
    #
    #     return len(seeds), activated_nodes
    #
    # # Get the expected number of seeds and activated nodes for an auction
    # # The function refer to the auctions currently saved in the publisher, with function generate_auctions
    # # Input: category (the auction to check), advertiser (the advertiser to monitor), iterations (number of iterations
    # # for the average)
    # # Output: average number of seeds , average number of activated nodes
    # def estimate_auction_effect(self, category: int, advertiser, iterations=15):
    #     avg_seeds = 0
    #     avg_activated_nodes = 0
    #     for _ in range(iterations):
    #         seeds = []
    #         for node in self.network.nodes:
    #             if node.category == category:
    #                 clicked_slot = node.show_ad(self.slates[category])
    #                 if clicked_slot >= 0 and self.slates[category][clicked_slot].assinged_ad == advertiser:
    #                     seeds.append(node)
    #         activated_nodes, node_activation_probabilities = influence_estimation.monteCarloEstimation(
    #             seeds=seeds, iterations=iterations)
    #
    #         avg_seeds += len(seeds)
    #         avg_activated_nodes += activated_nodes
    #
    #     return avg_seeds/iterations, avg_activated_nodes/iterations
    #
    # # Given an advertiser, a category and the number of seeds, return the cost of the auction
    # def get_cost(self, advertiser, category: int, number_of_seeds):
    #     for slot in self.slates[category]:
    #         if slot.assigned_ad == advertiser:
    #             return slot.price_per_click * number_of_seeds

    def get_bandit_qualities(self):
        qualities = {}
        # qualities: {
        #   ad_id: {
        #       category: pulled_quality_value
        #   }
        # }
        # do bandit round
        for advertiser in self.advertisers:
            ad_id = advertiser.ad.ad_id
            qualities[advertiser.id] = {}
            for category in range(constants.CATEGORIES):
                # do bandit for single ad
                pulled_arm = self.bandits_quality[ad_id][category]['bandit'].pull_arm()
                self.bandits_quality[ad_id][category]['last_pulled_arm'] = pulled_arm
                qualities[ad_id][category] = constants.bandit_quality_values[pulled_arm]
        return qualities

    def get_bandit_activations(self):
        activations = {}
        # activations: {
        #   from_category: {
        #       to_category: pulled_activation_value
        # }}
        # do bandit round
        for from_category in range(constants.CATEGORIES):
            activations[from_category] = {}
            for to_category in range(constants.CATEGORIES):
                # do bandit for single ad
                pulled_arm = self.bandits_activation[from_category][to_category]['bandit'].pull_arm()
                self.bandits_activation[from_category][to_category]['last_pulled_arm'] = pulled_arm
                activations[from_category][to_category] = constants.bandit_activation_values[pulled_arm]
        return activations

    # rewards = measured click probabilities for each category and for each ad.
    def update_bandits_quality(self, rewards):
        # rewards:
        # {
        #   ad_id:
        #   {
        #       category:
        #       {
        #           value: number of seeds / number of nodes
        #       }
        #   }
        # }
        for advertiser in self.advertisers:
            for category in range(constants.CATEGORIES):
                if rewards[advertiser.id][category] != -1:
                    bandit = self.bandits_quality[advertiser.id][category]['bandit']
                    last_pulled_arm = self.bandits_quality[advertiser.id][category]['last_pulled_arm']
                    bandit.update(last_pulled_arm, rewards[advertiser.id][category])

    # rewards = measured click probabilities for each category and for each ad.
    def update_bandits_activations(self, rewards):
        # activations:{
        #   from_category:{
        #       to_category:{
        #           value:
        # }}}
        for from_category in range(constants.CATEGORIES):
            for to_category in range(constants.CATEGORIES):
                bandit = self.bandits_activation[from_category][to_category]['bandit']
                last_pulled_arm = self.bandits_activation[from_category][to_category]['last_pulled_arm']
                bandit.update(last_pulled_arm, rewards[from_category][to_category])


    # do real network sample
    # input slates
    # output rewards for updating bandits
    # find better method name
    def real_network_sample(self, slates):
        # seeds:
        # {ad_id:
        #   {category:
        #       {list of node_ids}
        #   }
        # }
        seeds = self.network.calculateSeeds(slates)

        # rewards:
        # {
        #   ad_id:
        #   {
        #       category:
        #       {
        #           value: number of seeds / number of nodes
        #       }
        #   }
        # }
        rewards = {}
        # nodes_per_category:
        # {
        #   category:
        #       {number}
        # }
        nodes_per_category = self.network.network_report()
        for advertiser in self.advertisers:
            rewards[advertiser] = {}
            for category in range(constants.categories):
                rewards[advertiser][category] = seeds[advertiser.id][category] / nodes_per_category[category]
        return rewards
