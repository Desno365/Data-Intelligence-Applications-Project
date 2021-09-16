import math

from src.slot import Slot

# Definition of the project constants

# set to true to enable debug printing
settings = {
    'auctionPrint': False,
    'adPrint': False,
    'advertiserPrint': False,
    'executionTimePrint': False
}

# the number of node categories in the network, each node is assigned a random category at creation
CATEGORIES = 5
categories = [0, 1, 2, 3, 4]
number_of_nodes = 300
average_number_neighbours = 2 * math.log(number_of_nodes)
sigma_neighbours = math.log(number_of_nodes)
connection_p_far = 0.05
connection_p_close = 0.1
edge_activation_p_far = 0.06
edge_activation_p_close = 0.10
edge_activation_p_same = 0.15
category_proportions = [625/9881, 1625/9881, 3225/9881, 5785/9881, 1]
do_drawings = True
# the number of ad slots in a slate
SLATE_DIMENSION = 6

# The probability of clicking a slot
SLOT_VISIBILITY = 0.50

# the probability that there is an edge between two nodes in the network
network_connectivity = 0.4

# margin for floating point value comparisons
floatingPointMargin = 0.001

# Number of iterations of the Monte Carlo simulation.
greedy_simulation_iterations = 3

# the number of bandit arms and their values
bandit_quality_values = [0.2, 0.4, 0.6, 0.8, 1.0]
# bandit_quality_values = [(i+1)/10 for i in range(10)]
bandit_activation_values = [0.03, 0.06, 0.09, 0.12, 0.15]  # [i*0.15/10 for i in range(10)]
number_of_bandit_arms_qualities = len(bandit_quality_values)
number_of_bandit_arms_activations = len(bandit_activation_values)

slates = []
for current_category in range(CATEGORIES):
    slate = []
    for slot_id in range(SLATE_DIMENSION):
        slot_prominence = ((1 - SLOT_VISIBILITY) ** slot_id) * SLOT_VISIBILITY
        slot = Slot(slot_id=slot_id, slot_prominence=slot_prominence)
        slate.append(slot)
    slates.append(slate)
