class AuctionAd:
    # ad_id = identifier for the ad.
    # quality = probability given the ad that the user clicks it.
    # bid = bid for the ad.
    def __init__(self, ad_id: int, quality: float, bid: float, category: int):
        self.ad_id = ad_id
        self.quality = quality
        self.bid = bid
        self.bid_per_quality = quality * bid
        self.category = category

    def __str__(self) -> str:
        return 'AuctionAdInput{id=' + str(self.ad_id) + ';q=' + str(self.quality) + ';b=' + str(self.bid) + ';b_per_q=' + str(self.bid_per_quality) + ';}'
