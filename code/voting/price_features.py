import numpy as np

def get_triangle_features(prices):
	area_above = 0
	area_below = 0
	max_diff = (0,0)
	baseline = prices[-1]
	total = 0
	for i,price in enumerate(prices):
		diff = abs(price - baseline)
		if price < baseline:
			area_below += diff
		elif price > baseline:
			area_above += diff
		if diff > max_diff[1]:
			max_diff = (i,diff)
		total += price
	resemblance = ((area_above+area_below)-abs(area_below-area_above))/(area_above+area_below)
	return max_diff,total/(i+1),resemblance



def get_tail_resemblance(tail_prices,triangle_mean):
	count=0
	for price in tail_prices:
		if price <= triangle_mean:
			count+=1
	return count/len(tail_prices)


def count_within_triangle(prices,max_diff):
	gradient = max_diff[1]/(len(prices)-max_diff[0])
	y_intercept = gradient*max_diff[0] + max_diff[1]
	count = 0
	for i,price in enumerate(prices):
		if abs(price-prices[-1]) < (-gradient*i + y_intercept):
			count += 1

	return count/len(prices[:-1])

def get_min_max(prices):
	max_price = 0
	min_price = np.inf
	for price in prices:
		if price > max_price:
			max_price = price
		if price < min_price:
			min_price = price
	return min_price,max_price



def get_head_and_shoulders_points(prices):
	#why are the points not () tuples. Do I refer to the index in the function that calls this
	min_prices = [np.inf,np.inf]
	max_prices = [(0,0),(0,0),(0,0)]
	total = 0

	for i,price in enumerate(prices):
		total += price
		point = (i,price)
		for j,max_price in enumerate(max_prices):
			if price > max_price[1]:
				temp = max_price
				max_prices[j] = point
				point = temp

	# Is this creating a 2D array like this variable is originally declared?
	min_prices[0] = [min(prices[max_prices[0][0]:max_prices[1][0]+1]),min(prices[max_prices[1][0]:max_prices[2][0]+1])]

	return max_prices[0],min_prices[0],max_prices[1],min_prices[1],max_prices[2],total/len(prices)


def double_top_features(prices):
	min_price = (0,np.inf)
	max_prices = [(0,0),(0,0)]
	total = 0
	for i,price in enumerate(prices):
		total += price
		point = (i,price)
		if price < min_price[1]:
			min_price = (i,price)
		for j,max_price in enumerate(max_prices):
			if price > max_price[1]:
				temp = max_price
				max_prices[j] = point
				point = temp


	return max_prices,min_price,total/len(prices)

