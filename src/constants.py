from typing import List

from src.slot import Slot

# Definition of the project constants

CATEGORIES = 5
SLATE_DIMENSION = 6
categories = [0, 1, 2, 3, 4]
click_propensities = [1, 1, 1, 1, 1]
network_connectivity = 0.4
floatingPointMargin = 0.001
bandit_quality_values = []
for i in range(1, 11, 1):
    j = i/10
    bandit_quality_values.append(j)

def get_slates() -> List[List[Slot]]:
    slates = []
    for current_category in range(CATEGORIES):
        slate = [Slot(slot_id, 0.80 ** (slot_id + 1)) for slot_id in range(SLATE_DIMENSION)]
        slates.append(slate)
    return slates