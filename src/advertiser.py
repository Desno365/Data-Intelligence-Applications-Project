## Abstract advertiser class

# BIDS CAN TAKE ONE OF 5 VALUES, INCLUDING 0
from bids_enum import BidsEnum


class Advertiser():
    """Bids are instances of BidsEnum, not values. It's easier this way to compare bid values without comparing
    floats """

    def __init__(self, quality, value):
        self.adquality = quality
        self.advalue = value
        self.bids = [BidsEnum.OFF for _ in range(5)]

    def participate_auction(self, category):
        return self.adquality, self.advalue, self.bids

    def notify_results(self, category):
        # The advertiser won an auction in this category with this bid.
        print("thank you")
