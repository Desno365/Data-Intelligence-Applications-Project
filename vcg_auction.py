import numpy as np
import random
from ad import Ad
from bids_enum import BidsEnum
from slot import Slot
from utils import Utils


num_of_slots = 6  # Specified in the project requirements.
slots = [
    Slot(slot_id=0, slot_prominence=0.50, price_per_click=0.0),
    Slot(slot_id=1, slot_prominence=0.45, price_per_click=0.0),
    Slot(slot_id=2, slot_prominence=0.40, price_per_click=0.0),
    Slot(slot_id=3, slot_prominence=0.35, price_per_click=0.0),
    Slot(slot_id=4, slot_prominence=0.30, price_per_click=0.0),
    Slot(slot_id=5, slot_prominence=0.25, price_per_click=0.0),
]

# Check correctness of number of slots.
assert len(slots) == num_of_slots

# Check that the slots array has its items sorted by prominence.
assert all(slots[i].slot_prominence >= slots[i+1].slot_prominence for i in range(len(slots)-1))


class VCGAuction:
    def __init__(self, available_ads):
        assert len(available_ads) > num_of_slots
        self.available_ads = available_ads

    def update_ads(self, available_ads):
        assert len(available_ads) > num_of_slots
        self.available_ads = available_ads

    # Returns the slots with the ads allocated and the prices.
    def perform_auction(self):
        x_a = []
        for ad1 in self.available_ads:
            # x_a = using the best assignment without ad a: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
            # Basically x_a is the total gain that other ads produce to the publisher if ad a does not exist.
            available_ads_without_ad1 = [a for a in self.available_ads if a.ad_id != ad1.ad_id]
            x_a.append(VCGAuction.get_total_gain_of_best_allocation(available_ads_without_ad1))

        best_ads = VCGAuction.get_best_ads(self.available_ads)
        for i in range(num_of_slots):
            slots[i].update_assigned_ad(best_ads[i])

        y_a = []
        for i in range(len(self.available_ads)):
            # y_a = using the best assignment with all ads: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
            # Basically y_a is the total gain that other ads produce to the publisher if ad a exists.
            y_a.append(VCGAuction.get_total_gain_of_allocation(slots, self.available_ads[i].ad_id))

        #prices = []
        #for i in range(len(self.available_ads)):
        #    value = (1 / (1 * self.available_ads[i].ad_quality)) * (x_a[i] - y_a[i])
        #    prices.append(value)
        return slots, x_a, y_a

    @staticmethod
    def get_total_gain_of_best_allocation(ads):
        best_ads = VCGAuction.get_best_ads(ads)
        for i in range(num_of_slots):
            slots[i].update_assigned_ad(best_ads[i])
        return VCGAuction.get_total_gain_of_allocation(slots, None)

    @staticmethod
    def get_best_ads(available_ads):
        available_ads_sorted = sorted(available_ads, key=lambda x: x.ad_value_per_quality, reverse=True)
        allocation = []
        for i in range(num_of_slots):
            allocation.append(available_ads_sorted[i])
        return allocation

    @staticmethod
    def get_total_gain_of_allocation(allocated_slots, except_ad_id):
        assert len(allocated_slots) >= num_of_slots
        gain = 0.0
        for slot in allocated_slots:
            if slot.assigned_ad.ad_id != except_ad_id:
                gain += (slot.slot_prominence * slot.assigned_ad.ad_value_per_quality)
        return gain


ads = []
num_of_ads = 10
for i in range(num_of_ads):
    random_bid = random.choice(list(BidsEnum)).value
    ads.append(Ad(ad_id=i, ad_quality=i / num_of_ads, ad_value=random_bid))

Utils.print_array(ads)
vcg_auction = VCGAuction(ads)
slots_assigned, x_a, y_a = vcg_auction.perform_auction()
Utils.print_array(slots_assigned)
print('x_a: ', x_a)
print('y_a: ', y_a)

