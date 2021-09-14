import random
from typing import List

import numpy as np
from matplotlib import pyplot as plt

from src import constants
from src.ad import Ad
from src.bids_enum import BidsEnum


class Advertiser:

    def __init__(self, ad_real_qualities: List[float] = None, ad_value: float = 0.5):
        if ad_real_qualities is None:
            ad_real_qualities = [random.uniform(0.05, 1) for _ in range(constants.CATEGORIES)]
        self.ad_real_qualities = ad_real_qualities
        self.id = random.randint(a=1, b=9999)
        self.ad_value = ad_value
        self.ad = Ad(
            ad_id=self.id,
            estimated_qualities=self.ad_real_qualities,
            real_qualities=self.ad_real_qualities,
            value=self.ad_value,
            bids=[BidsEnum.OFF for _ in range(constants.CATEGORIES)]
        )
        self.estimated_activations = {}
        for from_category in range(constants.CATEGORIES):
            self.estimated_activations[from_category] = {}
            for to_category in range(constants.CATEGORIES):
                self.estimated_activations[from_category][to_category] = random.random()
        self.daily_gain_history = np.array([])

    def participate_auction(self) -> Ad:
        return self.ad

    def change_bids(self) -> None:
        self.ad.set_bids([random.choice(list(BidsEnum)) for _ in range(5)])

    def report_daily_results(self, social_influence):
        d_gain = self.compute_gain_from_social_influence(social_influence=social_influence)
        self.daily_gain_history = np.append(self.daily_gain_history, d_gain)

    def compute_gain_from_social_influence(self, social_influence) -> float:
        activated_nodes = 0
        seeds = {}
        prices = {}

        # Note for each category activated nodes, seeds and prices.
        if self.id in social_influence.keys():
            for category in social_influence[self.id].keys():
                activated_nodes += social_influence[self.id][category]['activatedNodes']
                seeds[category] = social_influence[self.id][category]["seeds"]
                prices[category] = social_influence[self.id][category]["price"]
        else:
            if constants.settings['advertiserPrint']:
                print('greedy advertiser ad is not in the slate')
                print(self.id, social_influence.keys())

        if constants.settings['advertiserPrint']:
            print(f"Simulated the network. Nodes activated: {activated_nodes}. Seeds: {seeds}")

        gain = activated_nodes * self.ad_value
        if constants.settings['advertiserPrint']:
            print(f"Gain from activated nodes: {gain}")

        # The price the advertiser must pay. Seeds are taken in a dictionary indexed by category.
        # To calculate the payment, for each category take its price per click and multiply it by the number
        # of seeds in that category.
        for category in seeds.keys():
            gain -= (prices[category] * seeds[category])
        if constants.settings['advertiserPrint']:
            print(f"Gain after payment: {gain}")
        return gain

