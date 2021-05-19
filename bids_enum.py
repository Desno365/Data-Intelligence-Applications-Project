from enum import Enum


# Specified in the project requirements: <<there is a finite number of bids (4 strictly positive values and 0, corresponding to turn off the campaign)>>.
class BidsEnum(Enum):
    OFF = 0
    VERY_SMALL = 0.2
    SMALL = 0.33
    MEDIUM = 0.5
    BIG = 0.75
