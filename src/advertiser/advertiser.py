import random
from typing import List

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

    def participate_auction(self) -> Ad:
        return self.ad

    def change_bids(self) -> None:
        self.ad.set_bids([random.choice(list(BidsEnum)) for _ in range(5)])
