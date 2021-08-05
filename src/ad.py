from typing import List

from src.bids_enum import BidsEnum


class Ad:
    # ad_id = identifier for the ad.
    # ad_quality = probability given the ad that the user clicks it.
    # ad_value = bid for the ad.
    def __init__(self, ad_id: int, ad_quality: List[float], ad_value: float, bids: List[BidsEnum]):
        self.ad_id = ad_id
        self.ad_quality = ad_quality
        self.ad_value = ad_value
        self.ad_value_per_quality = [qual * ad_value for qual in ad_quality]
        self.bids = bids
        print(f"Create Ad with id {self.ad_id}, quality {self.ad_quality}, value {self.ad_value}, bids {self.bids}, value per quality {self.ad_value_per_quality}")

    def setbids(self, bids: List[BidsEnum]):
        self.bids = bids
        print(f"")


    def __str__(self) -> str:
        return 'Ad{id=' + str(self.ad_id) + ';q=' + str(self.ad_quality) + ';v=' + str(self.ad_value) + ';v_per_q=' + str(self.ad_value_per_quality) + ';}'