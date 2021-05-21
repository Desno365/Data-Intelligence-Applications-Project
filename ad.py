class Ad:
    # ad_id = identifier for the ad.
    # ad_quality = probability given the ad that the user clicks it.
    # ad_value = bid for the ad.
    def __init__(self, ad_id, ad_quality, ad_value):
        self.ad_id = ad_id
        self.ad_quality = ad_quality
        self.ad_value = ad_value
        self.ad_value_per_quality = ad_quality * ad_value

    def __str__(self):
        return 'Ad{id=' + str(self.ad_id) + ';q=' + str(self.ad_quality) + ';v=' + str(self.ad_value) + ';v_per_q=' + str(self.ad_value_per_quality) + ';}'
