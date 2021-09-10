from enum import Enum


# Specified in the project requirements: <<there is a finite number of bids (4 strictly positive values and 0,
# corresponding to turn off the campaign)>>.
class BidsEnum(Enum):
    OFF = 0
    VERY_SMALL = 0.2
    SMALL = 0.33
    MEDIUM = 0.5
    MAX = 0.75

    def next_elem(self) -> 'BidsEnum':
        if self == BidsEnum.MAX:
            print("Cannot increment a max bid")
            return BidsEnum.MAX
        # print('debug bids enum: current bid', list(BidsEnum)[list(BidsEnum).index(self)], 'next one',list(BidsEnum)[list(BidsEnum).index(self)+1])
        return list(BidsEnum)[list(BidsEnum).index(self) + 1]
