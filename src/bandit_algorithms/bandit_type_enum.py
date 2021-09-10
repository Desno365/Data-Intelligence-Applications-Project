from enum import Enum

from src.bandit_algorithms.bandit_learner import BanditLearner
from src.bandit_algorithms.sliding_window_thompson_sampling_learner import SlidingWindowThompsonSamplingLearner
from src.bandit_algorithms.sliding_window_ucb1_learner import SlidingWindowUCB1Learner
from src.bandit_algorithms.thompson_sampling_learner import ThompsonSamplingLearner
from src.bandit_algorithms.ucb1_learner import UCB1Learner


class BanditTypeEnum(Enum):
    UCB1 = 0
    THOMPSON_SAMPLING = 1
    SLIDING_WINDOW_UCB1 = 2
    SLIDING_WINDOW_THOMPSON_SAMPLING = 3

    def instantiate_bandit(self, n_arms: int, window_size: int or None) -> BanditLearner:
        if self == BanditTypeEnum.UCB1:
            return UCB1Learner(n_arms=n_arms)
        if self == BanditTypeEnum.THOMPSON_SAMPLING:
            return ThompsonSamplingLearner(n_arms=n_arms)
        if self == BanditTypeEnum.SLIDING_WINDOW_UCB1:
            assert window_size is not None
            return SlidingWindowUCB1Learner(n_arms=n_arms, window_size=window_size)
        if self == BanditTypeEnum.SLIDING_WINDOW_THOMPSON_SAMPLING:
            assert window_size is not None
            return SlidingWindowThompsonSamplingLearner(n_arms=n_arms, window_size=window_size)
        raise ValueError("BanditType not recognized.")