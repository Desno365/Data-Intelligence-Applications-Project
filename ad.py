class Ad:
    # ad_identifier = identifier for the ad.
    # ad_quality = probability given the ad that the user clicks it.
    # ad_value = bid for the ad.
    def __init__(self, ad_identifier, ad_quality, ad_value):
        self.ad_identifier = ad_identifier
        self.ad_quality = ad_quality
        self.ad_value = ad_value
        self.ad_value_per_quality = ad_quality * ad_value

    def __str__(self):
        return 'Ad{id=' + str(self.ad_identifier) + ';q=' + str(self.ad_quality) + ';v=' + str(self.ad_value) + ';v_per_q=' + str(self.ad_value_per_quality) + ';}'

    @staticmethod
    def print_ads_array(ads_array):
        print_string = '[ '
        for ad in ads_array:
            print_string += ad.__str__()
            print_string += ', '
        print_string += ' ]'
        print(print_string)