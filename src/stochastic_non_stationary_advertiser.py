import random

from src.advertiser import Advertiser
from src.bids_enum import BidsEnum

"""
An advertiser that every n auctions changes its bids.
"""


class StochasticNonStationaryAdvertiser(Advertiser):

    def __init__(self, quality=None, value=0.5, n=15):
        super().__init__(quality, value)
        self.change_bids()
        self.n = n
        self.k = 0

    def participate_auction(self):
        if self.k == self.n:
            self.change_bids()
            self.k = 0

        self.k += 1
        return super().participate_auction()

    def change_bids(self):
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
        self.ad.setbids(self.bids)
