import random

from Advertiser import Advertiser
from bids_enum import BidsEnum

"""
An advertiser that every n auctions changes its bids.
"""


class StochasticAdvertiser(Advertiser):

    def __init__(self, quality=0.5, value=0.5, n=15):
        super().__init__(quality, value)
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
        print(self.bids)
        self.n = n
        self.k = 0

    def participate_auction(self, category):
        if self.k == self.n:
            self.change_bids()
            self.k = 0

        self.k += 1
        return super().participate_auction()

    def change_bids(self):
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]


StochasticAdvertiser()
print(list(BidsEnum)[2])
print(BidsEnum.MEDIUM.next_elem().next_elem())
