import pandas as pd

class Patterns:
	triangle_max_differences = []
	means = []
	# Not sure if this is how you initialise a 2D list but we will need them since we need 3 per price range
	max_prices = [[]] # up to 3?
	min_prices = [[]] # up to 3 as well, since we will do the inverse of some patterns
	# Just had a quick look at how these are used and maybe it would be easier and better to just save the tail mean and use that
	min_tail_prices = [] # one per price range
	max_tail_prices = [] # one per price range

	def __init__(self):
		pass

