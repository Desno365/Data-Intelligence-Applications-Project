import copy
from typing import List

from src import constants
from src.auction.auction import Auction
from src.auction.auction_ad import AuctionAd
from src.slot import Slot


class VCGAuction(Auction):
    # available_ads = the available ads.
    # slate = the available slots. The array must be ordered by slot_prominence.
    # For the algorithms implemented here see https://i.imgur.com/6z0SSwj.jpg and https://i.imgur.com/0kWZa7E.jpg
    def __init__(self, available_ads: List[AuctionAd], slate: List[Slot]):
        super().__init__(available_ads=available_ads, slate=slate)

    # Returns the slate given in input but with an assigned_ad and a price_per_click for every slot.
    def perform_auction(self) -> List[Slot]:
        if(constants.settings['auctionPrint']):
            print(f'Running auction')

        # Compute best assignment. This basically implements what is written here https://i.imgur.com/6z0SSwj.jpg
        best_ads = VCGAuction.get_best_ads(ads=self.available_ads)
        for i in range(self.num_of_slots):
            self.slate[i].update_assigned_ad(assigned_ad=best_ads[i])

        # Compute the price for every ad assigned to a slot. This basically implements what is written here https://i.imgur.com/0kWZa7E.jpg
        slate_deep_copy = copy.deepcopy(self.slate)  # "compute_x_a" will modify the assignments of the slate. So to avoid modifying the original slate we make a deep copy.
        for slot in self.slate:
            ad_id = slot.assigned_ad.ad_id
            slot_prominence_a = slot.slot_prominence
            quality_a = slot.assigned_ad.ad_quality
            x_a = VCGAuction.compute_x_a(ads=self.available_ads, slate=slate_deep_copy, a_id=ad_id)
            y_a = VCGAuction.compute_y_a(allocated_slate=self.slate, a_id=ad_id)

            p_a = (1 / (slot_prominence_a * quality_a)) * (x_a - y_a)
            slot.update_price_per_click(price_per_click=p_a)
            if (constants.settings['auctionPrint']):
                print(f'x: {x_a}, y: {y_a}, p: {p_a}, prominence: {slot_prominence_a}, '
                      f'quality: {quality_a}, bid: {slot.assigned_ad.ad_bid}')
            #print(f'Computed price for ad with id {ad_id}. slot_prominence_a={slot_prominence_a}, quality_a={quality_a}, x_a={x_a}, y_a={y_a}, p_a={p_a}.')
            if not p_a <= slot.assigned_ad.ad_bid + constants.floatingPointMargin:
                print('price and bid', p_a, slot.assigned_ad.ad_bid)
            assert p_a <= slot.assigned_ad.ad_bid + constants.floatingPointMargin # Price must be lower or equal than the bid.

        return self.slate

    @staticmethod
    # allocated_slate = the already allocated slate, allocated with the best assignment.
    # a_id = id of the ad "a" that we want to use to compute y_a.
    # Returns y_a is the total gain that other ads (different than "a") produce to the publisher if ad "a" exists.
    # Formally y_a is: using the best assignment with all ads: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
    def compute_y_a(allocated_slate: List[Slot], a_id: int) -> float:
        assert VCGAuction.is_slate_allocated(allocated_slate)
        return VCGAuction.get_total_gain_of_allocation(allocated_slate=allocated_slate, except_ad_id=a_id)

    @staticmethod
    # ads = all the ads available, including ad "a".
    # slate = all the slots available.
    # a_id = id of the ad "a" that we want to use to compute x_a.
    # Returns x_a that is basically the total gain that other ads produce to the publisher if ad "a" does not exist.
    # Formally x_a is: using the best assignment without ad a: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
    # WARNING: this method modifies the slate by assigning the best ads. If this is not wanted make a deep copy of the slate!
    def compute_x_a(ads: List[AuctionAd], slate: List[Slot], a_id: int) -> float:
        available_ads_without_a = [ad1 for ad1 in ads if ad1.ad_id != a_id]
        return VCGAuction.get_total_gain_of_best_allocation(ads=available_ads_without_a, slate=slate)

    @staticmethod
    # WARNING: this method modifies the slate by assigning the best ads. If this is not wanted make a deep copy of the slate!
    def get_total_gain_of_best_allocation(ads: List[AuctionAd], slate: List[Slot]) -> float:
        num_of_slots = len(slate)
        best_ads = VCGAuction.get_best_ads(ads=ads)
        for i in range(num_of_slots):
            slate[i].update_assigned_ad(assigned_ad=best_ads[i])
        return VCGAuction.get_total_gain_of_allocation(allocated_slate=slate, except_ad_id=None)

    @staticmethod
    def get_best_ads(ads: List[AuctionAd]) -> List[AuctionAd]:
        available_ads_sorted = sorted(ads, key=lambda x: x.ad_bid_per_quality, reverse=True)
        return available_ads_sorted

    @staticmethod
    def get_total_gain_of_allocation(allocated_slate: List[Slot], except_ad_id: int or None) -> float:
        assert VCGAuction.is_slate_allocated(allocated_slate)
        gain = 0.0
        for slot in allocated_slate:
            if slot.assigned_ad.ad_id != except_ad_id:
                gain += (slot.slot_prominence * slot.assigned_ad.ad_bid_per_quality)
        return gain

    @staticmethod
    def is_slate_allocated(slate: List[Slot]) -> bool:
        return all(slot.assigned_ad is not None for slot in slate)
