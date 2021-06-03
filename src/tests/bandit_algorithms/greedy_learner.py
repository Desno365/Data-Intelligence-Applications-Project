import numpy as np

from bandit_algorithms.bandit_learner import BanditLearner


class GreedyLearner(BanditLearner):
    # n_arms = number of arms the learner can pull.
    def __init__(self, n_arms: int):
        super().__init__(n_arms)
        self.expected_rewards = np.zeros(n_arms)

    # Select which arm to pull by maximizing the expected reward,
    # but we want that each arm is pulled at leats once.
    def pull_arm(self) -> int:
        if self.t < self.n_arms:
            return self.t  # Guarantees that each arm is pulled once.

        # Get arms that have max expected value.
        idxs = np.argwhere(self.expected_rewards == self.expected_rewards.max()).reshape(-1)

        # Get only one arm from the arms that have max expected value.
        pulled_arm = np.random.choice(idxs)
        return pulled_arm

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update(self, pulled_arm: int, reward: float) -> None:
        # Increment round.
        self.t += 1

        # Updates rewards lists.
        self.update_observations(pulled_arm, reward)

        # Update expected rewards as average of collected rewards for each arm.
        self.expected_rewards[pulled_arm] = (self.expected_rewards[pulled_arm] * (self.t - 1) + reward) / self.t
