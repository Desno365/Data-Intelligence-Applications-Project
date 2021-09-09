import copy
from typing import List

from src import constants
from src.ad import Ad
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum
from src.slot import Slot
from matplotlib import pyplot as plt


class GreedyLearningAdvertiser(Advertiser):

    def __init__(self, quality=None, value=0.5, network=None):
        super().__init__(quality, value)
        self.stop_improving = False
        self.already_increased = [False for _ in range(5)]  # This list will keep track of which bid has already been
        # increased
        self.to_increment = 0  # This will keep track of the category bid that the learner should try to
        # increase.
        self.category_gain = [0 for _ in
                              range(5)]  # The marginal gain after having increased that category bid
        self.previous_gain = 0
        self.network = network
        self.rival_ads = None
        self.slates = None
        self.gain_history = []

    def participate_auction(self) -> Ad:
        # Reset learner
        self.stop_improving = False
        self.category_gain = [0 for _ in range(5)]
        self.previous_gain = 0
        self.bids = [BidsEnum.OFF for _ in range(5)]  # Reset the bids to zero

        self.find_optimal_bids()
        self.ad.set_bids(self.bids)

        return self.ad

    def set_rival_ads(self, rival_ads: List[Ad]) -> None:
        self.rival_ads = rival_ads

    def set_slates(self, slates: List[List[Slot]]) -> None:
        self.slates = slates

    def find_optimal_bids(self) -> None:
        self.improved_bids = self.bids.copy()

        while not self.stop_improving:

            for i in range(len(self.bids)):
                if not self.already_increased[i] and not self.bids[i].value == BidsEnum.MAX.value:
                    # Found the first non increased element
                    # print(f"Chosen category {self.to_increment} with the vector being {self.already_increased}")
                    self.improved_bids = self.bids.copy()
                    self.improved_bids[i].next_elem()

                    # Take a copy of the rival ads, append a copy of its ad with improved bids.
                    ads = self.rival_ads.copy()
                    copy_ad = copy.deepcopy(self.ad)
                    copy_ad.set_bids(self.improved_bids)
                    ads.append(copy_ad)

                    social_influence = AdPlacementSimulator.simulate_ad_placement(network=self.network, ads=ads, slates=self.slates, iterations=60)
                    activated_nodes = 0
                    seeds = {}
                    prices = {}

                    if self.id in social_influence.keys():
                        for category in social_influence[self.id].keys():
                            activated_nodes += social_influence[self.id][category]['activatedNodes']
                            seeds[category] = social_influence[self.id][category]["seeds"]
                            prices[category] = social_influence[self.id][category]["price"]

                    print(f"Simulated the network. Nodes activated: {activated_nodes}. Seeds: {seeds}")

                    self.category_gain[i] = activated_nodes * self.advalue
                    print(f"Gain from activated nodes: {self.category_gain[i]}")

                    # The price the advertiser must pay. Seeds are returned in a dictionary indexed by category.
                    # To calculate the payment, for each category take its price per click and multiply it by the number
                    # of seeds in that category.
                    for category in seeds.keys():
                        self.category_gain[i] -= (prices[category] * seeds[category])
                    self.already_increased[i] = True
                    print(f"Gain after payment: {self.category_gain[i]}")

            # Here all the bids have been improved one time and the gain is noted.

            if not self.already_increased.count(True) == 5:
                raise ValueError(f"Control should not go here.")

            self.improve()

    def improve(self) -> None:
        # TODO: Here I update each marginal gain with current gain - previous gain. Current gain depends on category,
        # but previous gain is the maximum gain of the preceding step. This often results in marginal gains being all
        # negative and the improvement stops after one step. Consider reworking this.
        # BUT my gain is the total gain computed on all categories. If the marginal gain is negative then I have
        # no incentive to take my most recent tentative.
        marginal_gains = [elem - self.previous_gain for elem in self.category_gain]

        if all(marg < 0 for marg in marginal_gains):
            print("\n")
            print(f"ALL MARGINAL GAINS ARE NEGATIVE. Marginal gains: {marginal_gains}")
            print(f"Previous gain is {self.previous_gain}")
            print(f"Bids are {self.bids}")
            # print(f"Continuing anyway...")
            print("\n")
            self.stop_improving = True

        else:
            # Improve, since there is at least one positive marginal gain.
            best_arm = marginal_gains.index(max(marginal_gains))
            self.gain_history.append(max(self.category_gain))

            self.bids[best_arm] = self.bids[best_arm].next_elem()
            self.previous_gain = self.category_gain[best_arm]

            print(
                f"Improvement: marginal gains are {marginal_gains}, the best is {best_arm} with gain {self.previous_gain}.")
            print(f"Now bids are: {self.bids}")

        self.category_gain = [0 for _ in range(5)]
        self.already_increased = [False for _ in range(5)]

    def plot_history(self) -> None:
        # TODO: UNTESTED I don't know if it works.
        plt.figure(0)
        plt.xlabel("Day")
        plt.ylabel("Gain")
        plt.plot(self.gain_history, range(1, self.gain_history), 'r')
        #plt.ylim(ymin=0)
        plt.show()
