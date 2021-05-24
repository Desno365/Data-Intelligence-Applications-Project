from unittest import TestCase
from ad import Ad
from bids_enum import BidsEnum
from slot import Slot
from utils import Utils
from vcg_auction import VCGAuction


class TestVCGAuction(TestCase):
    def test_perform_auction(self):
        ads = TestVCGAuction.get_example_ads_array()
        slots = TestVCGAuction.get_example_slots_array()

        Utils.print_array(ads)
        vcg_auction = VCGAuction(available_ads=ads, slate=slots)
        slots_assigned = vcg_auction.perform_auction()
        Utils.print_array(slots_assigned)

    def test_get_total_gain_of_best_allocation(self):
        slots = [
            Slot(slot_id=0, slot_prominence=0.80),
            Slot(slot_id=1, slot_prominence=0.80 * 0.80),
            Slot(slot_id=2, slot_prominence=0.80 * 0.80 * 0.80),
        ]
        ads = [
            Ad(ad_id=0, ad_quality=0.05, ad_value=BidsEnum.VERY_SMALL.value),
            Ad(ad_id=1, ad_quality=0.15, ad_value=BidsEnum.SMALL.value),
            Ad(ad_id=2, ad_quality=0.10, ad_value=BidsEnum.MEDIUM.value),
            Ad(ad_id=3, ad_quality=0.20, ad_value=BidsEnum.MAX.value),
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
        slots[0].update_assigned_ad(Ad(ad_id=9, ad_quality=0.50, ad_value=BidsEnum.MAX.value))
        slots[1].update_assigned_ad(Ad(ad_id=8, ad_quality=0.45, ad_value=BidsEnum.MEDIUM.value))
        slots[2].update_assigned_ad(Ad(ad_id=7, ad_quality=0.40, ad_value=BidsEnum.SMALL.value))

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
    def get_example_slots_array():
        slots = [
            Slot(slot_id=0, slot_prominence=0.80),
            Slot(slot_id=1, slot_prominence=0.80 * 0.80),
            Slot(slot_id=2, slot_prominence=0.80 * 0.80 * 0.80),
            Slot(slot_id=3, slot_prominence=0.80 * 0.80 * 0.80 * 0.80),
            Slot(slot_id=4, slot_prominence=0.80 * 0.80 * 0.80 * 0.80 * 0.80),
            Slot(slot_id=5, slot_prominence=0.80 * 0.80 * 0.80 * 0.80 * 0.80 * 0.80),
        ]
        assert len(slots) == 6  # Specified in the project requirements that there are 6 slots
        return slots

    @staticmethod
    def get_example_ads_array():
        #random_bid = random.choice(list(BidsEnum)).value
        ads = [
            Ad(ad_id=0, ad_quality=0.05, ad_value=BidsEnum.OFF.value),
            Ad(ad_id=1, ad_quality=0.10, ad_value=BidsEnum.VERY_SMALL.value),
            Ad(ad_id=2, ad_quality=0.15, ad_value=BidsEnum.SMALL.value),
            Ad(ad_id=3, ad_quality=0.20, ad_value=BidsEnum.MEDIUM.value),
            Ad(ad_id=4, ad_quality=0.25, ad_value=BidsEnum.MAX.value),
            Ad(ad_id=5, ad_quality=0.30, ad_value=BidsEnum.OFF.value),
            Ad(ad_id=6, ad_quality=0.35, ad_value=BidsEnum.VERY_SMALL.value),
            Ad(ad_id=7, ad_quality=0.40, ad_value=BidsEnum.SMALL.value),
            Ad(ad_id=8, ad_quality=0.45, ad_value=BidsEnum.MEDIUM.value),
            Ad(ad_id=9, ad_quality=0.50, ad_value=BidsEnum.MAX.value),
        ]
        return ads
