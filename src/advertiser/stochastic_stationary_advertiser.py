import random

from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum

"""
An advertiser that has its bids set randomly.
"""


class StochasticStationaryAdvertiser(Advertiser):

    def __init__(self, quality=None, value=0.5):
        super().__init__(quality=quality, value=value)
        self.change_bids()

    def participate_auction(self):
        return super().participate_auction()

    def change_bids(self):
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
        self.ad.setbids(self.bids)
