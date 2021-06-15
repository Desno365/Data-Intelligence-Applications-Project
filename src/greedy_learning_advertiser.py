from advertiser import Advertiser
from bids_enum import BidsEnum


class GreedyLearningAdvertiser(Advertiser):
    """This whole class is not thread safe."""

    def __init__(self, quality=None, value=0.5):
        super().__init__(quality, value)
        self.already_increased = [False for _ in range(5)]  # This list will keep track of which bid has already been
        # increased
        self.to_increment = 0  # This will keep track of the category bid that the learner should try to
        # increase.
        self.waiting_results = False  # Indicates whether the advertiser is currently waiting for the results of the
        # auction
        self.category_gain = [0 for _ in
                              range(5)]  # The marginal gain after having increased that category bid
        self.previous_category_gain = [0 for _ in
                                       range(5)]

    def participate_auction(self):
        if self.waiting_results:
            raise Exception("Greedy learner is waiting for results.")
        self.incr_bids = self.bids.copy()  # Reset the bids to the original value

        if self.already_increased.count(True) == 5:  # All bids have been increased, I think the control should not
            # normally go here.
            # TODO: the control can go here if bids are almost all at maximum and the last to increment is 5
            raise ValueError(f"The value next_to_increment should not be {self.to_increment}.")

        else:  # If all bids have not been increased
            self.to_increment = self.already_increased.index(False)  # Find the first category bid not already
            # increased
            print(f"Chosen category {self.to_increment} with the vector being {self.already_increased}")
            if self.incr_bids[self.to_increment].value != BidsEnum.MAX.value:  # If the bid has not yet reached the
                # maximum value possible
                self.incr_bids[self.to_increment].next_elem()
                self.waiting_results = True
            else:  # This category bid has reached the maximum value possible, trying the next value
                self.already_increased[self.to_increment] = True
                return self.participate_auction()
                # This is not an endless recursion because finally the list already_increase should be all True

        self.ad.setbids(self.incr_bids)
        return self.ad

    def notify_results(self, category_won):
        print(f"Greedy learner won in categories {category_won}")
        self.waiting_results = False

        for category in category_won:
            self.category_gain[category] += self.advalue - self.incr_bids[category].value

        self.already_increased[self.to_increment] = True
        if self.already_increased.count(
                True) == 5:  # If every category bid has already been increased, then improve the algorithm
            self.improve()

    """
    Function to notify the advertiser how many nodes became seeds (or became active at some point)
    Alternative to notify_results. Might merge the two if needed.
    """

    def network_results(self, activated_nodes, seeds, cost_per_category):
        self.waiting_results = False

        self.category_gain[self.to_increment] = activated_nodes * self.advalue

        for seed in seeds:
            self.category_gain[self.to_increment] -= cost_per_category[seed.category]
        self.already_increased[self.to_increment] = True
        # print(f"Results: improved bid of {self.to_increment} and noted a gain of {activated_nodes}")
        print(
            f"Greedyadv results: improved bid of {self.to_increment} and noted a gain of {self.category_gain[self.to_increment]}")

        if self.already_increased.count(True) == 5:
            self.improve()

    def improve(self):
        best = self.category_gain.index(max(self.category_gain))
        if self.category_gain[best] > self.previous_category_gain[best]:
            # If it is better than preceding gain
            self.bids[best] = self.bids[best].next_elem()
            self.previous_category_gain[best] = self.category_gain[best]
        else:
            print("Chose not to improve because gain is smaller than before.")


        print(f"Improvement: gains are {self.category_gain}, the best is {best}.")
        print(f"Now bids are: {self.bids}")
        self.category_gain = [0 for _ in range(5)]
        self.already_increased = [False for _ in range(5)]
