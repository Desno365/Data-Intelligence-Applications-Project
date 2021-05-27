import Network
import Auction
import Advertiser
import constants as const


class Slate:

    def __init__(self, dimension=const.SLATE_DIMENSION):
        self.dimension = dimension
        self.slots = []


class Publisher:

    def __init__(self, network: Network, monitored_advertiser: Advertiser ):
        self.network = network
        self.monitored_advertiser = monitored_advertiser
        self.auction = None
        self.slate = None

    def subscribe_advertiser(self, advertiser : Advertiser):
        self.monitored_advertiser = advertiser

    def subscribe_auction(self, auction : Auction):
        self.slate = auction.perform_auction()

    def play_round(self):
        monitored_slot = None
        for slot in self.slate.slots:
            if slot.assigned_ad.advertiser == self.monitored_advertiser:
                monitored_slot = slot

        seeds = []
        for node in self.network.nodes:
            if node.category == self.auction.category:
                clicked_slot = node.show_ad(self.slate)
                if monitored_slot is not None and 0 <= clicked_slot == monitored_slot:
                    seeds.append(node)

        activated_nodes = self.network.calculate_activated_nodes(seeds=seeds)

        return seeds, activated_nodes

    def round_cost(self, seeds):
        cost = 0
        for slot in self.slate.slots:
            if slot.assigned_ad.advertiser == self.monitored_advertiser:
                cost = len(seeds) * slot.price_per_click
        return cost

    def round_value(self, activated_nodes):
        value = 0
        for slot in self.slate.slots:
            if slot.assigned_ad.advertiser == self.monitored_advertiser:
                value = len(activated_nodes) * slot.assigned_ad.ad_value
        return value





