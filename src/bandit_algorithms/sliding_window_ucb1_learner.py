import statistics

import numpy as np

from src.bandit_algorithms.ucb1_learner import UCB1Learner


class SlidingWindowUCB1Learner(UCB1Learner):
    def __init__(self, n_arms: int, window_size: int):
        super().__init__(n_arms)
        assert window_size > 1
        self.window_size = window_size
        self.pulled_arms_sliding_window = np.array([], dtype=np.int32)
        self.rewards_per_arm_sliding_window = [[] for _ in range(n_arms)]

    def update(self, pulled_arm: int, reward: float) -> None:
        # Increment round.
        self.t += 1

        # Updates rewards lists.
        self.update_observations(pulled_arm, reward)

        # Update sliding window of pulled arms list.
        self.pulled_arms_sliding_window = np.append(self.pulled_arms_sliding_window, pulled_arm)

        # Update sliding window of rewards per arm.
        self.rewards_per_arm_sliding_window[pulled_arm].append(reward)

        # If sliding window array is bigger than window, keep only recent values.
        if len(self.pulled_arms_sliding_window) > self.window_size:
            old_pulled_arm = self.pulled_arms_sliding_window[0].item()
            self.pulled_arms_sliding_window = self.pulled_arms_sliding_window[-self.window_size:]
            assert len(self.pulled_arms_sliding_window) == self.window_size
            self.rewards_per_arm_sliding_window[old_pulled_arm].pop(0)

        # Update empirical mean.
        self.empirical_means[pulled_arm] = statistics.mean(self.rewards_per_arm_sliding_window[pulled_arm])

        # Update confidence
        for a in range(self.n_arms):
            times_pulled_in_sliding_window = max(0.0001,  len(self.rewards_per_arm_sliding_window[a]))  # max() to avoid division by zero.
            self.confidence[a] = (2 * np.log(self.t) / times_pulled_in_sliding_window) ** 0.5
