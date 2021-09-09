import random
from typing import List

from src.ad import Ad
from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum

"""
An advertiser that every n auctions changes its bids.
"""


class StochasticNonStationaryAdvertiser(Advertiser):

    def __init__(self, quality: List[float] = None, value: float = 0.5, n: int = 15):
        super().__init__(quality, value)
        self.change_bids()
        self.n = n
        self.k = 0

    def participate_auction(self) -> Ad:
        if self.k == self.n:
            self.change_bids()
            self.k = 0

        self.k += 1
        return super().participate_auction()

    def change_bids(self) -> None:
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
        self.ad.setbids(self.bids)
