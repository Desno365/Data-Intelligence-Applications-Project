import abc

import numpy as np


# This is an abstract class that specifies how a concrete implementation of a bandit algorithm should behave.
class BanditLearner(metaclass=abc.ABCMeta):
    # n_arms = number of arms the learner can pull.
    def __init__(self, n_arms: int):
        self.n_arms = n_arms
        self.t = 0  # current round.
        self.rewards_per_arm = [[] for _ in range(n_arms)]  # List of lists (using python list), example rewards_per_arm[0] contains the list of pulled rewards from arm 0.
        self.collected_rewards = np.array([])  # Numpy array containing all rewards.

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update_observations(self, pulled_arm: int, reward: float) -> None:
        self.rewards_per_arm[pulled_arm].append(reward)
        self.collected_rewards = np.append(self.collected_rewards, reward)

    @abc.abstractmethod
    def pull_arm(self) -> int:
        pass

    @abc.abstractmethod
    def update(self, pulled_arm: int, reward: float) -> None:
        pass
