from typing import List

from src import constants
from src.bids_enum import BidsEnum


class Ad:
    # ad_id = identifier for the ad.
    # estimated_qualities = estimated probability given the ad that the user clicks it. One probability per category.
    # real_qualities = real probability given the ad that the user clicks it. One probability per category.
    # value = value of the advertiser for the ad.
    # bids = bids for the ad, one bid per category.
    def __init__(self, ad_id: int, estimated_qualities: List[float], real_qualities: List[float], value: float, bids: List[BidsEnum]):
        assert len(estimated_qualities) == constants.CATEGORIES
        assert all(0.0 <= quality <= 1.0 for quality in estimated_qualities)
        assert len(real_qualities) == constants.CATEGORIES
        assert all(0.0 <= quality <= 1.0 for quality in real_qualities)
        assert len(bids) == constants.CATEGORIES

        self.ad_id = ad_id
        self.estimated_qualities = estimated_qualities
        self.real_qualities = real_qualities
        self.value = value
        self.bids = bids
        if constants.settings['adPrint']:
            print(f"Create Ad with id {self.ad_id}, estimated qualities {self.estimated_qualities}, real_qualities {self.real_qualities}, value {self.value}, bids {self.bids}")

    def set_bids(self, bids: List[BidsEnum]) -> None:
        assert len(bids) == constants.CATEGORIES
        self.bids = bids
        if constants.settings['adPrint']:
            print(f"New bids: {bids}")

    def set_estimated_qualities(self, estimated_qualities: List[float]) -> None:
        assert len(estimated_qualities) == constants.CATEGORIES
        assert all(0.0 <= quality <= 1.0 for quality in estimated_qualities)
        self.estimated_qualities = estimated_qualities
        if constants.settings['adPrint']:
            print(f"New estimated qualities: {estimated_qualities}")

    def __str__(self) -> str:
        return 'Ad{id=' + str(self.ad_id)\
               + ';estimated_qualities=' + str(self.estimated_qualities) \
               + ';real_qualities=' + str(self.real_qualities) \
               + ';value=' + str(self.value) + ';}'
