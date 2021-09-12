import random
from typing import List

from src import constants
from src.ad import Ad
from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum

"""
An advertiser that every n auctions changes its bids.
"""


class StochasticNonStationaryAdvertiser(Advertiser):

    def __init__(self, ad_real_qualities: List[float] = None, ad_value: float = 0.5, n: int = 15):
        super().__init__(ad_real_qualities=ad_real_qualities, ad_value=ad_value)
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
        self.ad.set_bids([random.choice(list(BidsEnum)) for _ in range(constants.CATEGORIES)])
