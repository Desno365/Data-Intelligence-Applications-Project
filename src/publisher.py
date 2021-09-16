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
                bandit_learner = bandit_type_qualities.instantiate_bandit(n_arms=constants.number_of_bandit_arms_qualities, window_size=window_size)
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
                bandit_learner = bandit_type_activations.instantiate_bandit(n_arms=constants.number_of_bandit_arms_activations, window_size=window_size)
                self.bandits_activation[from_category][to_category]['bandit'] = bandit_learner

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
        activations = []
        # activations: [
        #   from_category: [
        #       to_category: pulled_activation_value
        #   ]
        # ]
        # do bandit round
        for from_category in range(constants.CATEGORIES):
            activations.append([])
            for to_category in range(constants.CATEGORIES):
                # do bandit for single ad
                pulled_arm = self.bandits_activation[from_category][to_category]['bandit'].pull_arm()
                self.bandits_activation[from_category][to_category]['last_pulled_arm'] = pulled_arm
                activations[from_category].append(constants.bandit_activation_values[pulled_arm])
            assert len(activations[from_category]) == constants.CATEGORIES
        assert len(activations) == constants.CATEGORIES
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
        seeds = self.network.calculate_seeds(slates)

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
