class VCGAuction:
    # available_ads = array of Ad objects containing the available ads.
    # slate = array of Slot objects containing the available slots. The array must be ordered by slot_prominence.
    def __init__(self, available_ads, slate):
        self.available_ads = available_ads
        self.slate = slate
        self.num_of_slots = len(slate)

        print(f'Received ads with length {len(available_ads)}, slate with length {len(slate)}')

        # Check that we have the minimum number of available ads to cover the slate.
        assert len(available_ads) > self.num_of_slots

        # Check that the slots array has its items sorted by prominence.
        assert all(slate[i].slot_prominence >= slate[i + 1].slot_prominence for i in range(len(slate) - 1))

    # Returns the slate with the assigned ads and the prices (if clicked).
    def perform_auction(self):
        x_a = []
        for ad1 in self.available_ads:
            # x_a = using the best assignment without ad a: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
            # Basically x_a is the total gain that other ads produce to the publisher if ad a does not exist.
            available_ads_without_ad1 = [a for a in self.available_ads if a.ad_id != ad1.ad_id]
            x_a.append(VCGAuction.get_total_gain_of_best_allocation(ads=available_ads_without_ad1, slate=self.slate))

        best_ads = VCGAuction.get_best_ads(self.available_ads)
        for i in range(self.num_of_slots):
            self.slate[i].update_assigned_ad(best_ads[i])

        y_a = []
        for i in range(len(self.available_ads)):
            # y_a = using the best assignment with all ads: sum on every ad a' different than a: slot_prominence of ad a' in assignment * quality of ad a' * value of ad a'
            # Basically y_a is the total gain that other ads produce to the publisher if ad a exists.
            y_a.append(VCGAuction.get_total_gain_of_allocation(self.slate, self.available_ads[i].ad_id))

        #prices = []
        #for i in range(len(self.available_ads)):
        #    value = (1 / (1 * self.available_ads[i].ad_quality)) * (x_a[i] - y_a[i])
        #    prices.append(value)
        return self.slate, x_a, y_a

    @staticmethod
    def get_total_gain_of_best_allocation(ads, slate):
        num_of_slots = len(slate)
        best_ads = VCGAuction.get_best_ads(ads)
        for i in range(num_of_slots):
            slate[i].update_assigned_ad(best_ads[i])
        return VCGAuction.get_total_gain_of_allocation(slate, None)

    @staticmethod
    def get_best_ads(ads):
        available_ads_sorted = sorted(ads, key=lambda x: x.ad_value_per_quality, reverse=True)
        return available_ads_sorted

    @staticmethod
    def get_total_gain_of_allocation(allocated_slots, except_ad_id):
        gain = 0.0
        for slot in allocated_slots:
            if slot.assigned_ad.ad_id != except_ad_id:
                gain += (slot.slot_prominence * slot.assigned_ad.ad_value_per_quality)
        return gain
