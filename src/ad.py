from typing import List

from src import constants
from src.bids_enum import BidsEnum


class Ad:
    # ad_id = identifier for the ad.
    # ad_quality = probability given the ad that the user clicks it.
    # ad_value = bid for the ad.
    def __init__(self, ad_id: int, ad_quality: List[float], ad_value: float, bids: List[BidsEnum]):
        self.ad_id = ad_id
        self.ad_quality = ad_quality
        self.ad_value = ad_value
        self.bids = bids
        if constants.settings['adPrint']:
            print(f"Create Ad with id {self.ad_id}, quality {self.ad_quality}, value {self.ad_value}, bids {self.bids}")

    def set_bids(self, bids: List[BidsEnum]):
        self.bids = bids
        if constants.settings['adPrint']:
            print(f"New bids: {bids}")

    def __str__(self) -> str:
        return 'Ad{id=' + str(self.ad_id) + ';q=' + str(self.ad_quality) + ';v=' + str(self.ad_value) + ';}'
