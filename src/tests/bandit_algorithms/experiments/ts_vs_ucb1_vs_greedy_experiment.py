from unittest import TestCase

import numpy as np
from matplotlib import pyplot as plt

from src.bandit_algorithms.thompson_sampling_learner import ThompsonSamplingLearner
from src.bandit_algorithms.ucb1_learner import UCB1Learner
from src.tests.bandit_algorithms.environments.bandit_test_environment import BanditTestEnvironment
from src.tests.bandit_algorithms.greedy_learner import GreedyLearner
from src.tests.bandit_algorithms.random_learner import RandomLearner


class TestThompsonSamplingVsUCB1VsGreedyExperiment(TestCase):
    def test_perform_experiment(self):

        # ################ Setup experiment. ################ #

        # Environment.
        p = np.array([0.15, 0.1, 0.1, 0.35])
        n_arms = len(p)
        opt = np.max(p)  # Real optimal.

        # Horizon.
        # Note: we needed to increase the horizon to see effect of UCB1.
        time_horizon = 200

        # Experiment variables.
        n_experiments = 100
        ts_rewards_per_experiment = []
        gr_rewards_per_experiment = []
        random_rewards_per_experiment = []
        ucb1_rewards_per_experiment = []

        # ################ Run experiment. ################ #

        for e in range(0, n_experiments):
            # Initialize environment and learners for experiment.
            env = BanditTestEnvironment(n_arms=n_arms, probabilities=p)
            ts_learner = ThompsonSamplingLearner(n_arms=n_arms)
            gr_learner = GreedyLearner(n_arms=n_arms)
            random_learner = RandomLearner(n_arms=n_arms)
            ucb1_learner = UCB1Learner(n_arms=n_arms)

            for i in range(time_horizon):
                # Simulate interaction between environment and thompson sampling learner.
                pulled_arm = ts_learner.pull_arm()
                reward = env.round(pulled_arm)
                ts_learner.update(pulled_arm, reward)

                # Simulate interaction between environment and greedy learner.
                pulled_arm = gr_learner.pull_arm()
                reward = env.round(pulled_arm)
                gr_learner.update(pulled_arm, reward)

                # Simulate interaction between environment and random learner.
                pulled_arm = random_learner.pull_arm()
                reward = env.round(pulled_arm)
                random_learner.update(pulled_arm, reward)

                # Simulate interaction between environment and UCB1 learner.
                pulled_arm = ucb1_learner.pull_arm()
                reward = env.round(pulled_arm)
                ucb1_learner.update(pulled_arm, reward)

            # Store rewards of the experiment.
            ts_rewards_per_experiment.append(ts_learner.collected_rewards)
            gr_rewards_per_experiment.append(gr_learner.collected_rewards)
            random_rewards_per_experiment.append(random_learner.collected_rewards)
            ucb1_rewards_per_experiment.append(ucb1_learner.collected_rewards)

        # ################ Preprocess result. ################ #

        # Mean over the regret of all n_experiments experiments, for TS, Greedy and UCB1.
        ts_mean_regrets = np.mean(opt - ts_rewards_per_experiment, axis=0)
        gr_mean_regrets = np.mean(opt - gr_rewards_per_experiment, axis=0)
        random_mean_regrets = np.mean(opt - random_rewards_per_experiment, axis=0)
        ucb1_mean_regrets = np.mean(opt - ucb1_rewards_per_experiment, axis=0)

        # ################ Plot result. ################ #

        plt.figure(0)
        plt.xlabel("t")
        plt.ylabel("Regret")
        plt.plot(np.cumsum(ts_mean_regrets), 'r')
        plt.plot(np.cumsum(gr_mean_regrets), 'g')
        plt.plot(np.cumsum(random_mean_regrets), 'c')
        plt.plot(np.cumsum(ucb1_mean_regrets), 'b')
        plt.legend(["TS", "Greedy", "Random", "UCB1"])
        plt.show()

        # We can see that:
        # Regret of greedy increase linearly.
        # While instantaneous regret of TS decreases as the number of rounds increases.
