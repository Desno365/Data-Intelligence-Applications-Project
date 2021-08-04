from advertiser import Advertiser
from bids_enum import BidsEnum
from src import network


class GreedyLearningAdvertiser(Advertiser):
    """This whole class is not thread safe."""

    def __init__(self, quality=None, value=0.5):
        super().__init__(quality, value)
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
                if not self.already_increased[i] and self.bids[i].value == BidsEnum.MAX.value:
                    # Found the first non increased element
                    print(f"Chosen category {self.to_increment} with the vector being {self.already_increased}")
                    self.improved_bids = self.bids.copy()
                    self.improved_bids[i].next_elem()
                    # Montecarlo simulation

                    activated_nodes, seeds = self.network.MC_pseudoNodes_freshSeeds(self.ad.ad_quality)

                    self.category_gain[i] = activated_nodes * self.ad.advalue

                    for seed in seeds:
                        self.category_gain[i] -= self.improved_bids[
                            seed.category]  # TODO: wrong maybe. the price is determined by the publisher
                    self.already_increased[i] = True

            # Here all the bids have been improved one time and the gain is noted.

            if not self.already_increased.count(True) == 5:
                raise ValueError(f"Control should not go here.")

            self.improve()

    def improve(self):
        marginal_gains = [elem - self.previous_gain for elem in self.category_gain]

        if all(marg < 0 for marg in marginal_gains):
            # TODO: STOP ALGORITHM?
            print("\n")
            print(f"ALL MARGINAL GAINS ARE NEGATIVE. Marginal gains: {marginal_gains}")
            print(f"Previous gain is {self.previous_gain}")
            print(f"Bids are {self.bids}")
            print(f"Continuing anyway...")
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
