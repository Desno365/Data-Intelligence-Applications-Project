class AuctionAd:
    # ad_id = identifier for the ad.
    # ad_quality = probability given the ad that the user clicks it.
    # ad_bid = bid for the ad.
    def __init__(self, ad_id: int, ad_quality: float, ad_bid: float):
        self.ad_id = ad_id
        self.ad_quality = ad_quality
        self.ad_bid = ad_bid
        self.ad_bid_per_quality = ad_quality * ad_bid

    def __str__(self) -> str:
        return 'AuctionAdInput{id=' + str(self.ad_id) + ';q=' + str(self.ad_quality) + ';b=' + str(self.ad_bid) + ';b_per_q=' + str(self.ad_bid_per_quality) + ';}'
