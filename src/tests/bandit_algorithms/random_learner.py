import random

from src.bandit_algorithms.bandit_learner import BanditLearner


class RandomLearner(BanditLearner):
    # n_arms = number of arms the learner can pull.
    def __init__(self, n_arms: int):
        super().__init__(n_arms)

    # Select which arm to pull randomly.
    def pull_arm(self) -> int:
        if self.t < self.n_arms:
            return self.t  # Guarantees that each arm is pulled once.

        return random.randint(0, self.n_arms-1)  # randint(a, b) return a random integer N such that a <= N <= b.

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update(self, pulled_arm: int, reward: float) -> None:
        # Increment round.
        self.t += 1

        # Updates rewards lists.
        self.update_observations(pulled_arm, reward)
