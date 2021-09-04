import random

from src.ad import Ad
from src.bids_enum import BidsEnum


class Advertiser:
    """Bids are instances of BidsEnum, not values. It's easier this way to compare bid values without comparing
    floats """

    def __init__(self, network, quality=None, value=0.5):
        if quality is None:
            quality = [random.uniform(0, 1) for _ in range(5)]
        #print(f"quality: {quality}")
        self.adquality = quality
        self.id = random.randint(a=1, b=9999999999999)
        self.advalue = value
        self.bids = [BidsEnum.OFF for _ in range(5)]
        #print(f"creating ad with quality: {self.adquality}")
        self.ad = Ad(self.id, self.adquality, self.advalue, self.bids)
        self.network = network

    def participate_auction(self) -> "Ad":
        return self.ad

    def notify_results(self, category):
        # The advertiser won an auction in this category with this bid.
        print("thank you")

    def set_random_bids(self):
        self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
