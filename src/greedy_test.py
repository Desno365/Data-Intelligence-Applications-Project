import random

from src.greedy_learning_advertiser import GreedyLearningAdvertiser
from src.network import Node
from src.bids_enum import BidsEnum

greedy = GreedyLearningAdvertiser()

for j in range(10000):
    greedy.participate_auction()
    nodes = [Node(random.randint(0, 4)) for _ in range(10)]
    bids_per_category = [random.choice(list(BidsEnum)) for _ in range(5)]
    cost_per_category = [bids_per_category[i].value for i in range(5)]
    # print(cost_per_category)
    activated_nodes = random.randint(90,100)
    greedy.network_results(activated_nodes, nodes, cost_per_category)