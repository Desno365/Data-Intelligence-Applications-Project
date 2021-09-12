import random
from typing import List
from unittest import TestCase

from src import constants
from src.auction.auction_ad import AuctionAd
from src.auction.vcg_auction import VCGAuction
from src.bids_enum import BidsEnum
from src.slot import Slot
from src.utils import Utils


class TestVCGAuction(TestCase):
    def test_perform_auction(self):
        ads = TestVCGAuction.get_example_ads_array()
        slots = constants.get_slates()[0]

        Utils.print_array(ads)
        slots_assigned = VCGAuction.perform_auction(available_ads=ads, slate=slots)
        Utils.print_array(slots_assigned)

    def test_perform_auction_with_random_input(self):
        number_of_auctions_to_try = 1000
        number_of_advertisers = 8
        for _ in range(number_of_auctions_to_try):
            ads = TestVCGAuction.get_random_ads_array(number_of_advertisers)
            slots = constants.get_slates()[0]

            Utils.print_array(ads)
            slots_assigned = VCGAuction.perform_auction(available_ads=ads, slate=slots)
            Utils.print_array(slots_assigned)

    def test_get_total_gain_of_best_allocation(self):
        slots = [
            Slot(slot_id=0, slot_prominence=0.80),
            Slot(slot_id=1, slot_prominence=0.80 * 0.80),
            Slot(slot_id=2, slot_prominence=0.80 * 0.80 * 0.80),
        ]
        ads = [
            AuctionAd(ad_id=0, estimated_quality=0.05, bid=BidsEnum.VERY_SMALL.value),
            AuctionAd(ad_id=1, estimated_quality=0.15, bid=BidsEnum.SMALL.value),
            AuctionAd(ad_id=2, estimated_quality=0.10, bid=BidsEnum.MEDIUM.value),
            AuctionAd(ad_id=3, estimated_quality=0.20, bid=BidsEnum.MAX.value),
        ]
        gain = VCGAuction.get_total_gain_of_best_allocation(ads=ads, slate=slots)
        expected_gain = (0.80 * 0.20 * BidsEnum.MAX.value) + (0.80 * 0.80 * 0.10 * BidsEnum.MEDIUM.value) + (0.80 * 0.80 * 0.80 * 0.15 * BidsEnum.SMALL.value)
        self.assertAlmostEqual(gain, expected_gain, delta=0.0001)

    def test_get_best_ads(self):
        ads = TestVCGAuction.get_example_ads_array()
        sorted_ads = VCGAuction.get_best_ads(ads)
        self.assertEqual(len(sorted_ads), 10)
        self.assertEqual(sorted_ads[0].ad_id, 9)
        self.assertEqual(sorted_ads[1].ad_id, 8)
        self.assertEqual(sorted_ads[2].ad_id, 4)
        self.assertEqual(sorted_ads[3].ad_id, 7)
        self.assertEqual(sorted_ads[4].ad_id, 3)
        self.assertEqual(sorted_ads[5].ad_id, 6)
        self.assertEqual(sorted_ads[6].ad_id, 2)
        self.assertEqual(sorted_ads[7].ad_id, 1)

    def test_get_total_gain_of_allocation(self):
        slots = [
            Slot(slot_id=0, slot_prominence=0.80),
            Slot(slot_id=1, slot_prominence=0.80 * 0.80),
            Slot(slot_id=2, slot_prominence=0.80 * 0.80 * 0.80),
        ]
        slots[0].update_assigned_ad(AuctionAd(ad_id=9, estimated_quality=0.50, bid=BidsEnum.MAX.value))
        slots[1].update_assigned_ad(AuctionAd(ad_id=8, estimated_quality=0.45, bid=BidsEnum.MEDIUM.value))
        slots[2].update_assigned_ad(AuctionAd(ad_id=7, estimated_quality=0.40, bid=BidsEnum.SMALL.value))

        # Test gain of whole slate.
        gain = VCGAuction.get_total_gain_of_allocation(allocated_slate=slots, except_ad_id=None)
        expected_gain = (0.80 * 0.50 * BidsEnum.MAX.value) + (0.80 * 0.80 * 0.45 * BidsEnum.MEDIUM.value) + (0.80 * 0.80 * 0.80 * 0.40 * BidsEnum.SMALL.value)
        self.assertAlmostEqual(gain, expected_gain, delta=0.0001)

        # Test gain of slate while ignoring ad with id 9.
        gain = VCGAuction.get_total_gain_of_allocation(allocated_slate=slots, except_ad_id=9)
        expected_gain = (0.80 * 0.80 * 0.45 * BidsEnum.MEDIUM.value) + (0.80 * 0.80 * 0.80 * 0.40 * BidsEnum.SMALL.value)
        self.assertAlmostEqual(gain, expected_gain, delta=0.0001)

        # Test gain of slate while ignoring ad with id 8.
        gain = VCGAuction.get_total_gain_of_allocation(allocated_slate=slots, except_ad_id=8)
        expected_gain = (0.80 * 0.50 * BidsEnum.MAX.value) + (0.80 * 0.80 * 0.80 * 0.40 * BidsEnum.SMALL.value)
        self.assertAlmostEqual(gain, expected_gain, delta=0.0001)

        # Test gain of slate while ignoring ad with id 7.
        gain = VCGAuction.get_total_gain_of_allocation(allocated_slate=slots, except_ad_id=7)
        expected_gain = (0.80 * 0.50 * BidsEnum.MAX.value) + (0.80 * 0.80 * 0.45 * BidsEnum.MEDIUM.value)
        self.assertAlmostEqual(gain, expected_gain, delta=0.0001)

    @staticmethod
    def get_example_ads_array() -> List[AuctionAd]:
        # random_bid = random.choice(list(BidsEnum)).value
        ads = [
            AuctionAd(ad_id=0, estimated_quality=0.05, bid=BidsEnum.OFF.value),
            AuctionAd(ad_id=1, estimated_quality=0.10, bid=BidsEnum.VERY_SMALL.value),
            AuctionAd(ad_id=2, estimated_quality=0.15, bid=BidsEnum.SMALL.value),
            AuctionAd(ad_id=3, estimated_quality=0.20, bid=BidsEnum.MEDIUM.value),
            AuctionAd(ad_id=4, estimated_quality=0.25, bid=BidsEnum.MAX.value),
            AuctionAd(ad_id=5, estimated_quality=0.30, bid=BidsEnum.OFF.value),
            AuctionAd(ad_id=6, estimated_quality=0.35, bid=BidsEnum.VERY_SMALL.value),
            AuctionAd(ad_id=7, estimated_quality=0.40, bid=BidsEnum.SMALL.value),
            AuctionAd(ad_id=8, estimated_quality=0.45, bid=BidsEnum.MEDIUM.value),
            AuctionAd(ad_id=9, estimated_quality=0.50, bid=BidsEnum.MAX.value),
        ]
        return ads

    @staticmethod
    def run_random_auction() -> None:
        ads = TestVCGAuction.get_example_ads_array()
        slots = constants.get_slates()[0]

        Utils.print_array(ads)
        slots_assigned = VCGAuction.perform_auction(available_ads=ads, slate=slots)
        Utils.print_array(slots_assigned)

    @staticmethod
    def get_random_ads_array(number_of_advertisers: int) -> List[AuctionAd]:
        ads = []
        for i in range(number_of_advertisers):
            ads.append(AuctionAd(ad_id=i, estimated_quality=random.uniform(0.05, 1), bid=random.choice(list(BidsEnum)).value),)
        ads.append(AuctionAd(ad_id=number_of_advertisers, estimated_quality=1, bid=random.choice(list(BidsEnum)).value))
        return ads
