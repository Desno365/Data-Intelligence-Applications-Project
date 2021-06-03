import numpy as np

from bandit_test_environment import BanditTestEnvironment


# It uses phases (so Abrupt Changes).
class BanditNonStationaryTestEnvironment(BanditTestEnvironment):
    # n_arms = number of arms.
    # probabilities = probability distributions of the arms for every phase.
    # horizon = horizon of environment (for phases)
    def __init__(self, n_arms, probabilities, horizon):
        super().__init__(n_arms, probabilities)
        self.t = 0  # Current round (to understand current phase)
        n_phases = len(self.probabilities)
        self.phase_size = horizon / n_phases  # Size of each phase (equal size)

    # Overrides round of Environment.
    # pulled_arm = arm chosen.
    # Returns stochastic reward.
    # Note: binomial distribution with param 1 it's bernoulli.
    def round(self, pulled_arm):
        current_phase = int(self.t / self.phase_size)
        p = self.probabilities[current_phase][pulled_arm]
        self.t += 1
        return np.random.binomial(1, p)
