class Slot:
    # slot_id = identifier for the slot.
    # slot_prominence = probability that the user observes the slot.
    # price_per_click = price that advertiser must pay of ads gets clicked.
    def __init__(self, slot_id, slot_prominence, price_per_click):
        self.slot_id = slot_id
        self.slot_prominence = slot_prominence
        self.assigned_ad = None
        self.price_per_click = price_per_click

    def update_assigned_ad(self, assigned_ad):
        self.assigned_ad = assigned_ad
        self.price_per_click = 0.0

    def update_price_per_click(self, price_per_click):
        self.price_per_click = price_per_click

    def __str__(self):
        return 'Slot{id=' + str(self.slot_id) + ';prominence=' + str(self.slot_prominence) + ';ad=' + str(self.assigned_ad) + ';price=' + str(self.price_per_click) + ';}'
