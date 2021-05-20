import random

from Advertiser import Advertiser
from bids_enum import BidsEnum


class StochasticAdvertiser(Advertiser):

	def __init__(self, quality=0.5, value=0.5):
		super().__init__(quality, value)
		self.bids = [random.choice(list(BidsEnum)) for _ in range(5)]
		print(self.bids)



StochasticAdvertiser()
print(list(BidsEnum)[2])
print(BidsEnum.MEDIUM.next_elem().next_elem())
