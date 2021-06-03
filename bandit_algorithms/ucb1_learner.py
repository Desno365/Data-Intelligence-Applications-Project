import numpy as np

from bandit_algorithms.bandit_learner import BanditLearner


class UCB1Learner(BanditLearner):
    def __init__(self, n_arms: int):
        super().__init__(n_arms)
        self.empirical_means = np.zeros(n_arms)
        self.confidence = np.array([np.inf] * n_arms)

    def pull_arm(self) -> int:
        if self.t < self.n_arms:
            arm = self.t
        else:
            upper_bound = self.empirical_means + self.confidence
            arm = np.random.choice(np.where(upper_bound == upper_bound.max())[0])
        return arm

    def update(self, pulled_arm: int, reward: float) -> None:
        # Increment round.
        self.t += 1

        # Update empirical mean.
        # num_of_rewards = self.t  # Done by professor. In my opinion bug here: empirical mean on all rounds? Shouldn't it be only on times arm observed?
        num_of_rewards = len(self.rewards_per_arm[pulled_arm]) + 1  # Done by us. Plus 1 because new reward still not appended to list.
        self.empirical_means[pulled_arm] = ((self.empirical_means[pulled_arm] * (num_of_rewards - 1)) + reward) / num_of_rewards

        # Update confidence
        for a in range(self.n_arms):
            times_pulled = max(0.0001, len(self.rewards_per_arm[a]))  # max() to avoid division by zero.
            self.confidence[a] = (2 * np.log(self.t) / times_pulled) ** 0.5

        # Updates rewards lists. Must be done later than computing new confidence.
        self.update_observations(pulled_arm, reward)
