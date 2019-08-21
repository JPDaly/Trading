import pandas as pd
import numpy as np

class Pattern:
	SHORTEST_PATTERN = 5 # days (working week)
	LONGEST_PATTERN = 66 # days (average working days in 3 months)

	MIN_TRIANGLE_TIME = 15

	means = []
	# Not sure if this is how you initialise a 2D list but we will need them since we need 3 per price range
	max_prices = [] # up to 3?
	min_prices = [] # up to 3 as well, since we will do the inverse of some patterns
	tail_means = []
	sum_area_below_baseline = []
	sum_area_above_baseline = []

	def __init__(self, prices):
		self.n_prices = len(prices)
		self.find_features(prices)
		self.baseline = prices[-1]
		self.prices = prices

	def find_features(self,prices):
		for max_period in range(SHORTEST_PATTERN,LONGEST_PATTERN+1):
			self.sum_area_below_baseline.append(0)
			self.sum_area_above_baseline.append(0)
			sub_prices = prices[-max_period:]
			n_sub_prices = len(sub_prices)
			
			total = 0
			for i,price in enumerate(sub_prices):
				total += price
				diff = abs(price-self.baseline)
				if price > self.baseline:
					sum_area_above_baseline[-1] += diff
				else:
					sum_area_below_baseline[-1] += diff
			
			self.means.append(total/n_sub_prices)

			# Sort to easily get the min and max prices zipped into form (price,index)
			prices_sorted = sorted(zip(sub_prices,range(n_sub_prices)), reverse=True)
			self.max_prices.append(prices_sorted[:3])
			self.min_prices.append(prices_sorted[-3:])
			# Get tail mean
			if 2*max_period >= self.n_prices:
				self.tail_means.append(sum(prices[:-max_period])/len(prices[:-max_period]))
			else:
				self.tail_means.append(sum(prices[:-max_period])/len(prices[-2*max_period:-max_period]))


	def res_triangle(self,max_time=MIN_TRIANGLE_TIME):
		resemblance = 0
		data_index = MIN_TRIANGLE_TIME - SHORTEST_PATTERN

		if max_time > LONGEST_PATTERN or max_time > self.n_prices:
			return resemblance


		if abs(self.max_prices[data_index][0][0] - self.baseline) > abs(self.max_prices[data_index][0][0] - self.baseline):
			max_diff = self.max_prices[data_index][0]
		else:
			max_diff = self.min_prices[data_index][0]

		if max_diff[1] > 0.5*max_time:
			# doesn't resemble a triangle at all
			return self.res_triangle(max_time+1)

		# How symmetric about the baseline is the triangle
		resemblance += (((self.sum_area_above_baseline[data_index]+self.sum_area_below_baseline[data_index])-abs(self.sum_area_below_baseline[data_index]-self.sum_area_above_baseline[data_index]))/(self.sum_area_above_baseline[data_index]+self.sum_area_below_baseline[data_index])/3)
		# Bigger the difference between the tail mean and the triangle mean the better
		resemblance += (((abs(self.tail_means[data_index]-self.means[data_index]))**2)/3)
		# Percentage of values within the triangle
		resemblance += ((within_triangle(max_diff,self.prices[-max_time:]))/3)

		# If the tail is above the mean then the triangle indicates a sell
		if self.tail_means[data_index] > self.baseline:
			resemblance *= -1

		next_resemblance = self.res_triangle(max_time+1)
		if resemblance > abs(next_resemblance):
			return resemblance
		else:
			return next_resemblance



	def res_flag(self):
		# same deal as triangle
		pass

	def res_head_and_shoulders(self):
		# upside down return 1 
		# normal return -1
		pass

	def res_double_top(self):
		# same deal as head and shoulders
		pass



	def within_triangle(self,max_diff,min_time):
		gradient = max_diff[0]/(len(prices)-max_diff[1])
		y_intercept = gradient*max_diff[0] + max_diff[0]
		count = 0
		for i,price in enumerate(prices):
			if abs(price-prices[-1]) < (-gradient*i + y_intercept):
				count += 1

		return count/len(prices[:-1])








if __name__ == '__main__':
	pattern = Pattern([26,10,19,28,10,14,15,30,9,16,7,16,8,14,20,30,15,27,25,5,26,11,12,2,15,12,16,3,28,9])
	print(pattern.means)