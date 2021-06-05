import random

from GreedyLearningAdvertiser import GreedyLearningAdvertiser
from Network import Node
from bids_enum import BidsEnum

greedy = GreedyLearningAdvertiser()



for j in range(6):
    greedy.participate_auction(1)
    nodes = [Node(random.randint(0, 4)) for _ in range(10)]
    bids_per_category = [random.choice(list(BidsEnum)) for _ in range(5)]
    cost_per_category = [bids_per_category[i].value for i in range(5)]
    #print(cost_per_category)
    greedy.network_results(100, nodes, cost_per_category)
