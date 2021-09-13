class AuctionAd:
    # ad_id = identifier for the ad.
    # estimated_quality = estimated probability given the ad that the user clicks it.
    # real_quality = real probability given the ad that the user clicks it.
    # bid = bid for the ad.
    def __init__(self, ad_id: int, estimated_quality: float, real_quality: float, bid: float, category: int):
        self.ad_id = ad_id
        self.estimated_quality = estimated_quality
        self.real_quality = real_quality
        self.bid = bid
        self.bid_per_quality = estimated_quality * bid
        self.category = category

    def __str__(self) -> str:
        return 'AuctionAdInput{ad_id=' + str(self.ad_id)\
               + ';estimated_quality=' + str(self.estimated_quality) \
               + ';real_quality=' + str(self.real_quality) \
               + ';bid=' + str(self.bid) \
               + ';bid_per_quality=' + str(self.bid_per_quality) + ';}'
