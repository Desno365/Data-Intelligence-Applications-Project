import numpy as np


class BanditLearner:
    # n_arms = number of arms the learner can pull.
    def __init__(self, n_arms):
        self.n_arms = n_arms
        self.t = 0  # current round.
        self.rewards_per_arm = [[] for i in range(n_arms)]  # List of lists (using python list), example rewards_per_arm[0] contains the list of pulled rewards from arm 0.
        self.collected_rewards = np.array([])  # Numpy array containing all rewards.

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update_observations(self, pulled_arm, reward):
        self.rewards_per_arm[pulled_arm].append(reward)
        self.collected_rewards = np.append(self.collected_rewards, reward)
