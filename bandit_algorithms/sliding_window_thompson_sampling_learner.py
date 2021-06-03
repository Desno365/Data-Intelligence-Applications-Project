import numpy as np

from bandit_algorithms.thompson_sampling_learner import ThompsonSamplingLearner


class SlidingWindowThompsonSamplingLearner(ThompsonSamplingLearner):
    # n_arms = number of arms the learner can pull.
    # window_size = size of the sliding window.
    def __init__(self, n_arms: int, window_size: int):
        super().__init__(n_arms)
        self.window_size = window_size
        self.pulled_arms = np.array([], dtype=np.int32)

    # pulled_arm = arm pulled.
    # reward = reward of arm pulled.
    def update(self, pulled_arm: int, reward: float) -> None:
        # Increment round.
        self.t += 1

        # Update rewards lists.
        self.update_observations(pulled_arm, reward)

        # Update pulled arms list.
        self.pulled_arms = np.append(self.pulled_arms, pulled_arm)

        # For each arm update the beta parameters (the sliding window affectes all arms).
        for arm in range(self.n_arms):
            # Number of rounds where the arm has been pulled in the sliding window.
            n_rounds_arm = self.number_of_times_arm_pulled_in_sliding_window(arm)

            # Cumulative reward obtained by the pulled arm in the last rounds.
            cumulative_reward = np.sum(self.rewards_per_arm[arm][-n_rounds_arm:]) if n_rounds_arm > 0 else 0

            # Update first beta parameter of Thompson Sampling.
            self.beta_parameters[arm, 0] = cumulative_reward + 1.0

            # Update second beta parameter of Thompson Sampling.
            self.beta_parameters[arm, 1] = n_rounds_arm - cumulative_reward + 1.0

    def number_of_times_arm_pulled_in_sliding_window(self, arm: int) -> int:
        pulled_arms_in_sliding_window = self.pulled_arms[-self.window_size:]
        return int(np.sum(pulled_arms_in_sliding_window == arm))
