import random
from typing import List

from src import constants
from src.ad import Ad
from src.bids_enum import BidsEnum


class Advertiser:
    """Bids are instances of BidsEnum, not values. It's easier this way to compare bid values without comparing
    floats """

    def __init__(self, quality: List[float] = None, value: float = 0.5):
        if quality is None:
            quality = [random.uniform(0.05, 1) for _ in range(constants.CATEGORIES)]
        self.adquality = quality
        self.id = random.randint(a=1, b=999999999999999)
        self.advalue = value
        self.bids = [BidsEnum.OFF for _ in range(constants.CATEGORIES)]
        #print(f"creating ad with quality: {self.adquality}")
        self.ad = Ad(ad_id=self.id, ad_quality=self.adquality, ad_value=self.advalue, bids=self.bids)

    def participate_auction(self) -> Ad:
        return self.ad

    def change_bids(self) -> None:
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
