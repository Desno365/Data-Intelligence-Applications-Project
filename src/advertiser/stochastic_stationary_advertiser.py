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

    def __init__(self, quality: List[float] = None, value: float = 0.5):
        super().__init__(quality=quality, value=value)
        self.change_bids()

    def participate_auction(self) -> Ad:
        return super().participate_auction()

    def change_bids(self) -> None:
        self.bids = [random.choice(list(BidsEnum)) for _ in range(constants.CATEGORIES)]
        self.ad.set_bids(self.bids)
