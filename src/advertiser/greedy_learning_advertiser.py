import copy
import random
from typing import List

from matplotlib import pyplot as plt

from src import constants
from src.ad import Ad
from src.ad_placement_simulator import AdPlacementSimulator
from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum
from src.network import Network
from src.slot import Slot


class GreedyLearningAdvertiser(Advertiser):

    def __init__(self, network: Network, use_estimated_activations: bool, ad_real_qualities: List[float] = None, ad_value: float = 0.5,):
        super().__init__(ad_real_qualities=ad_real_qualities, ad_value=ad_value)
        self.stop_improving = False
        self.already_increased = [False for _ in range(constants.CATEGORIES)]  # This list will keep track of which bid has already been increased
        self.to_increment = 0  # This will keep track of the category bid that the learner should try to increase.
        self.category_gain = [0.0 for _ in range(constants.CATEGORIES)]  # The marginal gain after having increased that category bid
        self.previous_gain = 0
        self.network = network
        self.rival_ads = None
        self.slates = None
        self.simulation_gain_history = []
        self.category_price = [0.0 for _ in range(constants.CATEGORIES)]
        self.simulation_price_history = []
        self.category_activated_nodes = [0 for _ in range(constants.CATEGORIES)]
        self.simulation_activated_nodes_history = []
        self.use_estimated_activations = use_estimated_activations

    def participate_auction(self) -> Ad:
        # Reset learner
        self.stop_improving = False
        self.simulation_gain_history = []
        self.simulation_price_history = []
        self.simulation_activated_nodes_history = []
        self.category_gain = [0 for _ in range(constants.CATEGORIES)]
        self.previous_gain = 0
        self.bids = [BidsEnum.OFF for _ in range(constants.CATEGORIES)]  # Reset the bids to zero
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
            if constants.settings['advertiserPrint']:
                print('debug already_increased before improvement', self.already_increased)
            for i in range(len(self.bids)):
                if not self.already_increased[i]:
                    if self.bids[i].value == BidsEnum.MAX.value:
                        # Bid is already maximum value. No gain is possible
                        self.already_increased[i] = True
                        self.category_gain[i] = 0
                        continue
                    # Found the first non increased element
                    # print(f"Chosen category {self.to_increment} with the vector being {self.already_increased}")
                    self.improved_bids = self.bids.copy()
                    if constants.settings['advertiserPrint']:
                        print('debug improved bids before improvement', self.improved_bids)
                    self.improved_bids[i] = self.improved_bids[i].next_elem()
                    if constants.settings['advertiserPrint']:
                        print('debug improved bids after improvement', self.improved_bids)

                    # Take a copy of the rival ads, append a copy of its ad with improved bids.
                    ads = self.rival_ads.copy()
                    copy_ad = copy.deepcopy(self.ad)
                    copy_ad.set_bids(self.improved_bids)
                    ads.append(copy_ad)

                    social_influence = AdPlacementSimulator.simulate_ad_placement(
                        network=self.network,
                        ads=ads,
                        slates=self.slates,
                        iterations=constants.greedy_simulation_iterations,
                        use_estimated_qualities=True,
                        use_estimated_activations=self.use_estimated_activations,
                        estimated_activations=self.estimated_activations
                    )
                    gain, total_value, total_price = self.compute_gain_from_social_influence(social_influence=social_influence)
                    self.category_gain[i] = gain
                    self.category_activated_nodes[i] = total_value
                    self.category_price[i] = total_price
                    self.already_increased[i] = True

            # Here all the bids have been improved one time and the gain is noted.

            if not self.already_increased.count(True) == constants.CATEGORIES:
                print('not enough true values', self.already_increased)
                raise ValueError(f"Control should not go here.")

            self.improve()

    def improve(self) -> None:
        # Here I update each marginal gain with current gain - previous gain. Current gain depends on category,
        # but previous gain is the maximum gain of the preceding step. This often results in marginal gains being all
        # negative and the improvement stops after one step. Consider reworking this.
        #
        # BUT my gain is the total gain computed on all categories. If the marginal gain is negative then I have
        # no incentive to take my most recent tentative.
        marginal_gains = [elem - self.previous_gain for elem in self.category_gain]

        if all(marg < 0 for marg in marginal_gains):
            print("\n")
            print(f"ALL MARGINAL GAINS ARE NEGATIVE. Marginal gains: {marginal_gains}")
            print(f"Previous gain is {self.previous_gain}")
            print(f"Bids are {self.bids}")
            print("\n")
            self.stop_improving = True

        else:
            # Improve, since there is at least one positive marginal gain.
            # (randomly choose an arm with the maximum value)
            indices = []
            max_value = max(marginal_gains)
            for i in range(len(marginal_gains)):
                if marginal_gains[i] == max_value:
                    indices.append(i)
            best_arm = random.choice(indices)
            self.simulation_gain_history.append(self.category_gain[best_arm])
            self.simulation_activated_nodes_history.append(self.category_activated_nodes[best_arm])
            self.simulation_price_history.append(self.category_price[best_arm])

            self.bids[best_arm] = self.bids[best_arm].next_elem()
            self.previous_gain = self.category_gain[best_arm]

            print(f"Greedy improvement: marginal gains are {marginal_gains}, the best is {best_arm} with gain {self.previous_gain}.")
            print(f"Now bids are: {self.bids}")

        self.category_gain = [0.0 for _ in range(constants.CATEGORIES)]
        self.already_increased = [False for _ in range(constants.CATEGORIES)]

    def plot_gain_history_in_single_day(self) -> None:
        plt.figure(0)
        plt.xlabel("Step")
        plt.ylabel("Marginal Gain")
        plt.plot([self.simulation_gain_history[i] - self.simulation_gain_history[i - 1] for i in range(1, len(self.simulation_gain_history))], 'r')
        plt.show()

        plt.figure(1)
        plt.xlabel("Step")
        plt.ylabel("Gain (total value - total price)")
        plt.plot(self.simulation_gain_history, 'r')
        plt.show()

        plt.figure(2)
        plt.xlabel("Step")
        plt.plot(self.simulation_activated_nodes_history, 'g')
        plt.plot(self.simulation_price_history, 'r')
        plt.legend(["Total value per step", "Total price per step"])
        plt.show()
        plt.figure(2)
