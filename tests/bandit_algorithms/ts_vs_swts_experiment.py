from unittest import TestCase

import numpy as np
from matplotlib import pyplot as plt

from bandit_algorithms.sliding_window_thompson_sampling_learner import SlidingWindowThompsonSamplingLearner
from bandit_algorithms.thompson_sampling_learner import ThompsonSamplingLearner
from bandit_non_stationary_test_environment import BanditNonStationaryTestEnvironment


class TestThompsonSamplingVsSlidingWindowThompsonSamplingExperiment(TestCase):
    def test_perform_experiment(self):

        # ################ Setup experiment. ################ #

        # Environment.
        n_arms = 4
        p = np.array([[0.15, 0.1, 0.2, 0.35],
                      [0.45, 0.21, 0.2, 0.35],
                      [0.1, 0.1, 0.5, 0.15],
                      [0.1, 0.21, 0.1, 0.15]])

        # Horizon.
        time_horizon = 500

        # Experiment variables.
        n_experiments = 1000
        ts_rewards_per_experiment = []
        swts_rewards_per_experiment = []

        # Window size calibrated by trial and error by professor.
        # Without the "4 *" it works worse at start than the normal TS_Learner.
        window_size = 4 * int(time_horizon ** 0.5)

        # ################ Run experiment. ################ #

        for e in range(0, n_experiments):
            # Initialize environments and learners for experiment.
            ts_env = BanditNonStationaryTestEnvironment(n_arms=n_arms, probabilities=p, horizon=time_horizon)
            ts_learner = ThompsonSamplingLearner(n_arms=n_arms)
            swts_env = BanditNonStationaryTestEnvironment(n_arms=n_arms, probabilities=p, horizon=time_horizon)
            swts_learner = SlidingWindowThompsonSamplingLearner(n_arms=n_arms, window_size=window_size)

            for t in range(time_horizon):
                # Simulate interaction between environment and thompson sampling learner.
                pulled_arm = ts_learner.pull_arm()
                reward = ts_env.round(pulled_arm)
                ts_learner.update(pulled_arm, reward)

                # Simulate interaction between environment and sliding-window thompson sampling learner.
                pulled_arm = swts_learner.pull_arm()
                reward = swts_env.round(pulled_arm)
                swts_learner.update(pulled_arm, reward)

            # Store rewards of the experiment.
            ts_rewards_per_experiment.append(ts_learner.collected_rewards)
            swts_rewards_per_experiment.append(swts_learner.collected_rewards)

        # ################ Preprocess result. ################ #

        # Initialize TS and SWTS arrays of instantaneous regret to zero.
        ts_instantaneous_regret = np.zeros(time_horizon)
        swts_instantaneous_regret = np.zeros(time_horizon)

        # Get optimal for various phases of the Non_Stationary_Environment.
        n_phases = len(p)
        phase_len = int(time_horizon / n_phases)
        opt_per_phase = p.max(axis=1)

        # Compute the instantaneous regret of TS and SWTS for each round.
        optimum_per_round = np.zeros(time_horizon)
        for i in range(0, n_phases):
            t_index = range(i * phase_len, (i + 1) * phase_len)
            optimum_per_round[t_index] = opt_per_phase[i]
            ts_instantaneous_regret[t_index] = opt_per_phase[i] - np.mean(ts_rewards_per_experiment, axis=0)[t_index]
            swts_instantaneous_regret[t_index] = opt_per_phase[i] - np.mean(swts_rewards_per_experiment, axis=0)[t_index]

        # ################ Plot result 1. ################ #

        plt.figure(0)
        plt.plot(np.mean(ts_rewards_per_experiment, axis=0), 'r')
        plt.plot(np.mean(swts_rewards_per_experiment, axis=0), 'b')
        plt.plot(optimum_per_round, 'k--')
        plt.legend(["TS", "SW-TS", "Optimum"])
        plt.ylabel("Reward")
        plt.xlabel("t")
        plt.show()

        # We can see on the plot that the SW-TS works a lot better when there is an abrupt change,
        # as can be seen especially in the third phase.
        # While in TS the more changes there are the worse it performs,
        # since for example in the last fourth phase it is still considering data also of the first phase.

        # ################ Plot result 2. ################ #

        plt.figure(1)
        plt.plot(np.cumsum(ts_instantaneous_regret), 'r')
        plt.plot(np.cumsum(swts_instantaneous_regret), 'b')
        plt.legend(["TS", "SW-TS"])
        plt.ylabel("Regret")
        plt.xlabel("t")
        plt.show()
