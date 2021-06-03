import abc
from typing import List

from ad import Ad
from slot import Slot


# This is an abstract class that specifies how a concrete implementation of an auction should behave.
class Auction(metaclass=abc.ABCMeta):

    # available_ads = the available ads.
    # slate = the available slots. The array must be ordered by slot_prominence.
    def __init__(self, available_ads: List[Ad], slate: List[Slot]):
        self.available_ads = available_ads
        self.slate = slate
        self.num_of_slots = len(slate)

        print(f'Initializing auction. Received ads with length {len(available_ads)}, slate with length {len(slate)}')

        # Check that we have the minimum number of available ads to cover the slate.
        # Note: uses "+ 1" because for calculating the price of an ad we need the existence of another ad that could substitute it.
        assert len(available_ads) >= self.num_of_slots + 1

        # Check that the slate array has its items sorted by prominence.
        assert all(slate[i].slot_prominence >= slate[i + 1].slot_prominence for i in range(len(slate) - 1))

    # Must return the slate given in input but with an assigned_ad and a price_per_click for every slot.
    @abc.abstractmethod
    def perform_auction(self) -> List[Slot]:
        pass
