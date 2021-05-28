import Network
from vcg_auction import VCGAuction


class Publisher:

    def __init__(self, network: Network):
        self.network = network
        self.auction = None
        self.slate = None

    def subscribe_auction(self, auction: VCGAuction):
        self.slate = auction.perform_auction()

    def play_round(self):
        seeds = [[] for i in range(len(self.slate))]
        activated_nodes = [[] for i in range(len(self.slate))]
        for node in self.network.nodes:
            if node.category == self.auction.category:
                clicked_slot = node.show_ad(self.slate)
                if 0 <= clicked_slot <= len(self.slate)-1:
                    seeds[clicked_slot].append(node)

        # todo fix the right method to get the activated nodes
        for ad in range(len(self.slate)):
            activated_nodes[ad] = self.network.calculate_activated_nodes(seeds=seeds[ad])

        return seeds, activated_nodes

    def round_cost(self, seeds, advertiser):
        cost = 0
        for slot in self.slate.slots:
            if slot.assigned_ad.advertiser == advertiser:
                cost = len(seeds) * slot.price_per_click
        return cost

    def round_value(self, activated_nodes, advertiser):
        value = 0
        for slot in self.slate.slots:
            if slot.assigned_ad.advertiser == advertiser:
                value = len(activated_nodes) * slot.assigned_ad.ad_value
        return value





