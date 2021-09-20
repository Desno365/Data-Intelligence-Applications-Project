import math
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

    def __init__(self, n: int, ad_real_qualities: List[float] = None, ad_value: float = 0.5):
        super().__init__(ad_real_qualities=ad_real_qualities, ad_value=ad_value)
        assert n > 0

        self.change_bids()
        self.n = n
        self.k = 0

    def participate_real_auction(self) -> Ad:
        self.k += 1
        if self.k >= self.n:
            print(f"Advertiser with id {self.id} is making an abrupt change.")
            self.change_qualities()
            self.change_bids()
            self.k = 0
        return super().participate_real_auction()

    def change_bids(self) -> None:
        self.ad.set_bids([random.choice(list(BidsEnum)) for _ in range(constants.CATEGORIES)])

    def change_qualities(self):
        ad_real_qualities = [random.uniform(0.05, 1) for _ in range(constants.CATEGORIES)]
        current_estimated_qualities = self.ad.estimated_qualities
        self.ad = Ad(
            ad_id=self.id,
            estimated_qualities=current_estimated_qualities,
            real_qualities=ad_real_qualities,
            value=self.ad_value,
            bids=[BidsEnum.OFF for _ in range(constants.CATEGORIES)]
        )
