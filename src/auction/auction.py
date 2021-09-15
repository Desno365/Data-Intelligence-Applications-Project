import abc
from typing import List

from src.auction.auction_ad import AuctionAd
from src.type_definitions import SlateType


# This is an abstract class that specifies how a concrete implementation of an auction should behave.
class Auction(metaclass=abc.ABCMeta):

    @staticmethod
    @abc.abstractmethod
    # Must return the slate given in input but with an assigned_ad and a price_per_click for every slot.
    def perform_auction(available_ads: List[AuctionAd], slate: SlateType) -> SlateType:
        pass
