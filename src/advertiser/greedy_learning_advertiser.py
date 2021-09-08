from src.advertiser.advertiser import Advertiser
from src.bids_enum import BidsEnum


class GreedyLearningAdvertiser(Advertiser):
    """This whole class is not thread safe."""

    def __init__(self, network, quality=None, value=0.5):
        super().__init__(network, quality, value)
        self.stop_improving = False
        self.already_increased = [False for _ in range(5)]  # This list will keep track of which bid has already been
        # increased
        self.to_increment = 0  # This will keep track of the category bid that the learner should try to
        # increase.
        self.waiting_results = False  # Indicates whether the advertiser is currently waiting for the results of the
        # auction
        self.category_gain = [0 for _ in
                              range(5)]  # The marginal gain after having increased that category bid
        self.previous_gain = 0

    def participate_auction(self):
        self.stop_improving = False
        self.category_gain = [0 for _ in
                              range(5)]
        self.previous_gain = 0

        if self.waiting_results:
            raise Exception("Greedy learner is waiting for results.")
        self.find_optimal_bids()
        self.ad.setbids(self.bids)
        return self.ad

    def find_optimal_bids(self):
        self.bids = [BidsEnum.OFF for _ in range(5)]  # Reset the bids to zero
        self.improved_bids = self.bids.copy()

        while not self.stop_improving:

            for i in range(len(self.bids)):
                if not self.already_increased[i] and not self.bids[i].value == BidsEnum.MAX.value:
                    # Found the first non increased element
                    #print(f"Chosen category {self.to_increment} with the vector being {self.already_increased}")
                    self.improved_bids = self.bids.copy()
                    self.improved_bids[i].next_elem()
                    # Montecarlo simulation

                    activated_nodes, seeds = self.network.estimateSocialInfluence(self.ad.ad_quality)
                    print(f"Simulated the network. Nodes activated: {activated_nodes}. Seeds: {seeds}")

                    self.category_gain[i] = activated_nodes * self.ad.ad_bid
                    print(f"Gain from activated nodes: {self.category_gain[i]}")

                    # The price the advertiser must pay. Seeds are returned in a dictionary indexed by category.
                    # To calculate the payment, for each category take its bid and multiply it by the number of seeds
                    # in that category.
                    # TODO: the price should be determined by the auction. This however is just a simulation.
                    for category in seeds.keys():
                        self.category_gain[i] -= self.improved_bids[category].value * seeds[category]
                    self.already_increased[i] = True
                    print(f"Gain after payment: {self.category_gain[i]}")


            # Here all the bids have been improved one time and the gain is noted.

            if not self.already_increased.count(True) == 5:
                raise ValueError(f"Control should not go here.")

            self.improve()

    def improve(self):
        # TODO: Here I update each marginal gain with current gain - previous gain. Current gain depends on category,
        # but previous gain is the maximum gain of the preceding step. This often results in marginal gains being all
        # negative and the improvement stops after one step. Consider reworking this.
        marginal_gains = [elem - self.previous_gain for elem in self.category_gain]

        if all(marg < 0 for marg in marginal_gains):
            print("\n")
            print(f"ALL MARGINAL GAINS ARE NEGATIVE. Marginal gains: {marginal_gains}")
            print(f"Previous gain is {self.previous_gain}")
            print(f"Bids are {self.bids}")
            #print(f"Continuing anyway...")
            print("\n")
            self.stop_improving = True

        else:
            # Improve, since there is at least one positive marginal gain.
            best_arm = marginal_gains.index(max(marginal_gains))
            self.bids[best_arm] = self.bids[best_arm].next_elem()
            self.previous_gain = self.category_gain[best_arm]

            print(
                f"Improvement: marginal gains are {marginal_gains}, the best is {best_arm} with gain {self.previous_gain}.")
            print(f"Now bids are: {self.bids}")

        self.category_gain = [0 for _ in range(5)]
        self.already_increased = [False for _ in range(5)]
