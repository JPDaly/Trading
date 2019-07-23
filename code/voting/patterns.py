import pandas as pd
import numpy as np

class Pattern:
	SHORTEST_PATTERN = 5 # days (working week)
	LONGEST_PATTERN = 66 # days (average working days in 3 months)
	means = []
	# Not sure if this is how you initialise a 2D list but we will need them since we need 3 per price range
	max_prices = [] # up to 3?
	min_prices = [] # up to 3 as well, since we will do the inverse of some patterns
	tail_means = []

	def __init__(self, prices):
		self.n_prices = len(prices)
		self.find_features(prices)

	def find_features(self,prices):
		for max_period in range(SHORTEST_PATTERN,LONGEST_PATTERN+1):
			sub_prices = prices[-max_period:]
			n_sub_prices = len(sub_prices)
			prices_sorted = sorted(zip(sub_prices,range(n_sub_prices), reverse=True)
			self.means.append(sum(sub_prices)/n_sub_prices)
			self.max_prices.append(prices_sorted[:3])
			self.min_prices.append(prices_sorted[-3:])

			if 2*max_period >= self.n_prices:
				tail_means.append(sum(prices[:-max_period])/len(prices[:-max_period]))
			else:
				tail_means.append(sum(prices[:-max_period])/len(prices[-2*max_period:-max_period]))
