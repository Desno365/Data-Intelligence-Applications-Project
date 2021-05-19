import numpy as np
import random
from ad import Ad
from bids_enum import BidsEnum


num_of_slots = 6  # Specified in the project requirements.
slot_prominence = [0.5, 0.45, 0.40, 0.35, 0.30, 0.25]  # This is the probability that the user observes the slot.
assert len(slot_prominence) == num_of_slots  # Check correctness of number of slots.
assert all(slot_prominence[i] >= slot_prominence[i+1] for i in range(len(slot_prominence)-1))  # Check that slot_prominence is a sorted array.


class VCGAuction():
    def __init__(self, available_ads):
        self.available_ads = available_ads

    def update_ads(self, available_ads):
        self.available_ads = available_ads

    # Returns the ads allocation and the prices.
    def perform_auction(self):
        available_ads_sorted = sorted(self.available_ads, key=lambda x: x.ad_value_per_quality, reverse=True)
        allocation = []
        for i in range(num_of_slots):
            allocation.append(available_ads_sorted[i])
        return allocation


ads = []
num_of_ads = 10
for i in range(num_of_ads):
    random_bid = random.choice(list(BidsEnum)).value
    ads.append(Ad(ad_identifier=i, ad_quality=i / num_of_ads, ad_value=random_bid))

Ad.print_ads_array(ads)
auction = VCGAuction(ads)
allocation_found = auction.perform_auction()
Ad.print_ads_array(allocation_found)

