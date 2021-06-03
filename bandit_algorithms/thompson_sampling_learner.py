import numpy as np

from bandit_algorithms.bandit_learner import BanditLearner


class ThompsonSamplingLearner(BanditLearner):
    # n_arms = number of arms the learner can pull.
    def __init__(self, n_arms):
        super().__init__(n_arms)
        self.beta_parameters = np.ones((n_arms, 2))

    # Select which arm to pull by sampling beta distribution.
    # We select the max value from the values sampled.
    def pull_arm(self):
        idx = np.argmax(np.random.beta(self.beta_parameters[:, 0], self.beta_parameters[:, 1]))
        return idx

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update(self, pulled_arm, reward):
        # Increment round.
        self.t += 1

        # Updates rewards lists.
        self.update_observations(pulled_arm, reward)

        # Update first beta parameter of Thompson Sampling.
        self.beta_parameters[pulled_arm, 0] = self.beta_parameters[pulled_arm, 0] + reward

        # Update second beta parameter of Thompson Sampling.
        self.beta_parameters[pulled_arm, 1] = self.beta_parameters[pulled_arm, 1] + 1 - reward
