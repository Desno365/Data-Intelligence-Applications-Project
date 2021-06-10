import collections
from unittest import TestCase

import numpy as np
from matplotlib import pyplot as plt

from src.bandit_algorithms.sliding_window_ucb1_learner import SlidingWindowUCB1Learner
from src.bandit_algorithms.ucb1_learner import UCB1Learner
from src.tests.bandit_algorithms.environments.bandit_non_stationary_test_environment import \
    BanditNonStationaryTestEnvironment


class TestUCB1VsSlidingWindowUCB1Experiment(TestCase):
    def test_perform_experiment(self):

        # ################ Setup experiment. ################ #

        # Environment.
        n_arms = 4
        p = np.array([[0.15, 0.1, 0.2, 0.35],
                      # [0.45, 0.21, 0.2, 0.25],
                      # [0.1, 0.1, 0.5, 0.15],
                      # [0.1, 0.25, 0.1, 0.15],
                      # [0.40, 0.1, 0.15, 0.1],
                      # [0.1, 0.2, 0.50, 0.1],
                      # [0.1, 0.45, 0.2, 0.30],
                      # [0.1, 0.1, 0.15, 0.50],
                      # [0.15, 0.1, 0.2, 0.35],
                      # [0.45, 0.21, 0.2, 0.25],
                      # [0.1, 0.1, 0.5, 0.15],
                      # [0.1, 0.25, 0.1, 0.15],
                      # [0.40, 0.1, 0.15, 0.1],
                      # [0.1, 0.2, 0.50, 0.1],
                      # [0.1, 0.45, 0.2, 0.30],
                      [0.1, 0.1, 0.15, 0.50]]
        )

        # Horizon.
        time_horizon = 200

        # Experiment variables.
        n_experiments = 2000
        ucb1_rewards_per_experiment = []
        swucb1_rewards_per_experiment = []
        ucb1_pulled_arms_per_time_step = [[] for _ in range(time_horizon)]
        swucb1_pulled_arms_per_time_step = [[] for _ in range(time_horizon)]

        # Window size calibrated by trial and error.
        # window_size = 3 * int(time_horizon ** 0.5)
        window_size = 100#int((time_horizon / len(p)) * 1.50)

        # ################ Run experiment. ################ #

        for e in range(0, n_experiments):
            # Initialize environments and learners for experiment.
            ucb1_env = BanditNonStationaryTestEnvironment(n_arms=n_arms, probabilities=p, horizon=time_horizon)
            ucb1_learner = UCB1Learner(n_arms=n_arms)
            swucb1_env = BanditNonStationaryTestEnvironment(n_arms=n_arms, probabilities=p, horizon=time_horizon)
            swucb1_learner = SlidingWindowUCB1Learner(n_arms=n_arms, window_size=window_size)

            for t in range(time_horizon):
                # Simulate interaction between environment and UCB1 learner.
                pulled_arm = ucb1_learner.pull_arm()
                reward = ucb1_env.round(pulled_arm)
                ucb1_learner.update(pulled_arm, reward)
                ucb1_pulled_arms_per_time_step[t].append(pulled_arm)

                # Simulate interaction between environment and sliding-window UCB1 learner.
                pulled_arm = swucb1_learner.pull_arm()
                reward = swucb1_env.round(pulled_arm)
                swucb1_learner.update(pulled_arm, reward)
                swucb1_pulled_arms_per_time_step[t].append(pulled_arm)

            # Store rewards of the experiment.
            ucb1_rewards_per_experiment.append(ucb1_learner.collected_rewards)
            swucb1_rewards_per_experiment.append(swucb1_learner.collected_rewards)

        # ################ Preprocess result. ################ #

        # Initialize UCB1 and SWUCB1 arrays of instantaneous regret to zero.
        ucb1_instantaneous_regret = np.zeros(time_horizon)
        swucb1_instantaneous_regret = np.zeros(time_horizon)

        # Get optimal for various phases of the Non_Stationary_Environment.
        n_phases = len(p)
        phase_len = int(time_horizon / n_phases)
        opt_per_phase = p.max(axis=1)

        # Compute the instantaneous regret of TS, SWTS and SWUCB1 for each round.
        optimum_reward_per_round = np.zeros(time_horizon)
        optimum_pulled_arm_per_round = np.zeros(time_horizon)
        for i in range(0, n_phases):
            t_index = range(i * phase_len, (i + 1) * phase_len)
            optimum_pulled_arm_per_round[t_index] = p.argmax(axis=1)[i]
            optimum_reward_per_round[t_index] = opt_per_phase[i]
            ucb1_instantaneous_regret[t_index] = opt_per_phase[i] - np.mean(ucb1_rewards_per_experiment, axis=0)[t_index]
            swucb1_instantaneous_regret[t_index] = opt_per_phase[i] - np.mean(swucb1_rewards_per_experiment, axis=0)[t_index]

        # Get most frequent pulled arm for each time step.
        ucb1_most_frequent_pulled_arm_per_time_step = [collections.Counter(ucb1_pulled_arms_per_time_step[i]).most_common(1)[0][0] for i in range(time_horizon)]
        swucb1_most_frequent_pulled_arm_per_time_step = [collections.Counter(swucb1_pulled_arms_per_time_step[i]).most_common(1)[0][0] for i in range(time_horizon)]

        # ################ Plot result 1. ################ #

        plt.rcParams["figure.figsize"] = (8, 6)
        plt.figure(0)
        plt.plot(np.mean(ucb1_rewards_per_experiment, axis=0), 'r')
        plt.plot(np.mean(swucb1_rewards_per_experiment, axis=0), 'b')
        plt.plot(optimum_reward_per_round, 'k--')
        plt.legend(["UCB1", "SW-UCB1", "Optimum"])
        plt.ylabel("Reward")
        plt.xlabel("t")
        plt.show()

        # ################ Plot result 2. ################ #

        plt.rcParams["figure.figsize"] = (8, 6)
        plt.figure(1)
        plt.plot(np.cumsum(ucb1_instantaneous_regret), 'r')
        plt.plot(np.cumsum(swucb1_instantaneous_regret), 'b')
        plt.legend(["UCB1", "SW-UCB1"])
        plt.ylabel("Regret")
        plt.xlabel("t")
        plt.show()

        # ################ Plot result 3. ################ #

        plt.rcParams["figure.figsize"] = (8, 6)
        plt.figure(2)
        plt.plot(ucb1_most_frequent_pulled_arm_per_time_step, 'r')
        plt.plot(swucb1_most_frequent_pulled_arm_per_time_step, 'b')
        plt.plot(optimum_pulled_arm_per_round, 'k--')
        plt.legend(["UCB1", "SW-UCB1", "Optimum"])
        plt.ylabel("Pulled arm")
        plt.xlabel("t")
        plt.show()
