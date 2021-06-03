import numpy as np
from numpy import ndarray


class BanditTestEnvironment:
    # n_arms = number of arms.
    # probabilities = probability distributions of the arms.
    def __init__(self, n_arms: int, probabilities: ndarray):
        self.n_arms = n_arms
        self.probabilities = probabilities

    # pulled_arm = arm chosen.
    # Returns stochastic reward.
    # Note: binomial distribution with param 1 it's bernoulli.
    def round(self, pulled_arm: int) -> float:
        p = self.probabilities[pulled_arm]
        reward = np.random.binomial(1, p)
        return reward
