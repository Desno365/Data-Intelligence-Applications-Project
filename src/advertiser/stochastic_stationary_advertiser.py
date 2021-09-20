import random
from typing import List

from src import constants
from src.ad import Ad
from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum

"""
An advertiser that has its bids set randomly.
"""


class StochasticStationaryAdvertiser(Advertiser):

    def __init__(self, ad_real_qualities: List[float] = None, value: float = 0.5):
        super().__init__(ad_real_qualities=ad_real_qualities, ad_value=value)
        self.ad.set_bids([random.choice(list(BidsEnum)) for _ in range(constants.CATEGORIES)])
        print(f'SELECTING BID: ad {self.id} bid {self.ad.bids}')

    def participate_real_auction(self) -> Ad:
        return super().participate_real_auction()
