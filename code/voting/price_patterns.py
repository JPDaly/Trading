import pandas as pd
import numpy as np
from price_features import *

COLUMNS = ["asx code","triangle","flag","h&s","double_top","triple_top","mean"]
PRICES_LOC = "../../database/historical/asx/prices/{0}.csv"
MAX_TRIANGLE_TIME = 66 # got this by multiplying the average amount of work days in a month (approximately 22) by 3 (for 3 months)
MIN_TRIANGLE_TIME = 15 # 3 weeks

MIN_FLAG_TIME = 5 # 1 week
MAX_FLAG_TIME = 20 # 4 weeks

MIN_DOUBLE_TOP_TIME = 15 # 3 weeks
MAX_DOUBLE_TOPF_TIME = 66 # average number of work days in 3 months


def find_patterns(companies):
	patterns_df = pd.DataFrame(columns=COLUMNS)
	for i,company in enumerate(companies):
		prices_df = pd.read_csv(PRICES_LOC.format(company))
		patterns_df.loc[i,COLUMNS[0]] = company
		patterns_df.loc[i,COLUMNS[1]] = triangle(MIN_TRIANGLE_TIME,prices_df['Close'].values)
		patterns_df.loc[i,COLUMNS[2]] = flag(MIN_FLAG_TIME,prices_df['Close'].values)
		print(head_and_shoulders(MIN_TRIANGLE_TIME,prices_df['Close'].values))
	
		
	
	return patterns_df


# Read the investors book before writing all these functions.
# There is more than just the pattern to consider.
# For example in the triple top/bottom paragraph it mentions something about volumes which could be handy since we have scraped volume data with the price data

def triangle(min_time,prices):
	resemblance = 0
	n_prices = len(prices)
	if min_time > MAX_TRIANGLE_TIME or min_time >= n_prices:
		return resemblance
	# resemblance is divided by three because we want the resemblance value between 0 and 1 
	max_diff,mean,resemblance = get_triangle_features(prices[-min_time:])
	resemblance /= 3
	if max_diff[0] > 0.5*min_time:
		# Return triangle because we aren't at the max size yet but we know that the resemblance for this one is 0 (aka return max_num(0,triangle(...)) )
		return triangle(min_time + 1,prices)

	if (2*min_time) >= n_prices:
		resemblance += get_tail_resemblance(prices[:-min_time],mean)/3
		# print("resemblance #2: {}".format(resemblance))
	else:
		resemblance += get_tail_resemblance(prices[-(2*min_time):-min_time],mean)/3
		# print("resemblance #2.1: {}".format(resemblance))
	
	resemblance += count_within_triangle(prices[-min_time:],max_diff)/3
	# print("resemblance #3: {}".format(resemblance))
	return max_num(resemblance,triangle(min_time+1,prices))

def flag(min_time,prices):
	resemblance = 0
	n_prices = len(prices)
	if min_time > MAX_FLAG_TIME or min_time >= n_prices:
		return resemblance

	min_flag_price,max_flag_price = get_min_max(prices[-min_time:])
	flag_height = max_flag_price - min_flag_price

	if n_prices < 2*min_time:
		min_tail_price,max_tail_price = get_min_max(prices[:-min_time])
	else:
		min_tail_price,max_tail_price = get_min_max(prices[-(2*min_time):-min_time])

	tail_height = max_tail_price - min_tail_price
	if max_tail_price > max_flag_price and min_tail_price > min_flag_price:
		# bear flag
		overlap = max_flag_price - min_tail_price 
		if overlap <= 0:
			resemblance += 0.5
		else: 
			resemblance += -1 + (flag_height/overlap)
	elif max_tail_price < max_flag_price and min_tail_price < min_flag_price:
		# bull flag
		overlap = max_tail_price - min_flag_price 
		if overlap <= 0:
			resemblance += 0.5
		else: 
			resemblance += 1 - (flag_height/overlap)
	resemblance += (1 - (flag_height/tail_height))/2
	return max_num(resemblance,flag(min_time+1,prices))

def rectangle():
	# Probably pass on this one since it's so similar to flag
	pass

# Going to use the triangle time formation range since apparently they can form together
def head_and_shoulders(min_time,prices):
	resemblance = 0
	n_prices = len(prices)
	if min_time > MAX_TRIANGLE_TIME or min_time >= n_prices:
		return resemblance

	lshoulder,left_neck,head,right_neck,rshoulder,mean = get_head_and_shoulders_points(prices[-min_time:])

	if head[1] < lshoulder[1] or head[1] < rshoulder[1] or head[0] < lshoulder[0] or head[0] > rshoulder[0]:
		# aka doesn't resemble a head and shoulders pattern at all
		return head_and_shoulders(min_time+1,prices)


	gap = head[1] - min_num(left_neck[1],right_neck[1])

	resemblance += (head[1] - max_num(lshoulder[1],rshoulder[1]))/(5*gap)
	resemblance += (max_num(lshoulder[1],rshoulder[1]) - max_num(left_neck[1],right_neck[1]))/(5*gap)
	resemblance += (1 - abs(rshoulder[1] - lshoulder[1]))/5
	resemblance += (1 - abs((head[0]-lshoulder[0]) - (rshoulder[0]-head[0])))/5
	if (2*min_time) >= n_prices:
		resemblance += get_tail_resemblance(prices[:-min_time],mean)/5
		# print("resemblance #2: {}".format(resemblance))
	else:
		resemblance += get_tail_resemblance(prices[-(2*min_time):-min_time],mean)/5
	return max_num(resemblance,head_and_shoulders(min_time+1,prices))

def double_top(min_time, prices):
	resemblance = 0
	n_prices = len(prices)

	if min_time > MAX_DOUBLE_TOP_TIME and min_time >= n_prices:
		return resemblance

	max_prices,min_price,mean = double_top_features(prices[-min_time:])

	if min_price[0] > max_num(max_prices[0][0],max_prices[1][0]) or min_price[0] < min_num(max_prices[0][0],max_prices[1][0]):
		return double_top(min_time+1,prices)

	resemblance += (1-(abs(max_prices[0][1] - max_prices[1][1])/max_num(max_prices[0][1],max_prices[1][1])))

	time_distances = (abs(max_prices[0][0] - min_price[0]), abs(max_prices[1][0] - min_price[0]))

	resemblance += (1-((time_distances[0] - time_distances[1])/max_num(time_distances[0],time_distances[1])))

	max_price_ave = (max_prices[0][1] + max_prices[1][1])/2
	distances_from_mean = (abs(max_price_ave - mean), abs(min_price[1] - mean))

	resemblance += (1-(abs(distances_from_mean[0]-distances_from_mean[1])/max_num(distances_from_mean[0], distances_from_mean[1])))

	return max_num(resemblance/3,double_top(min_time+1,prices))




def triple_top():
	# Possibly too similar to the head and shoulders 
	pass

def max_num(a,b):
	return (a>=b)*a + (b>a)*b

def min_num(a,b):
	return (a<=b)*a + (b<a)*b


if __name__ == "__main__":
	find_patterns(['1AD']) # for testing only. Uncomment the line below when finished
	# print("This file can't be run on it's own.\nThe functions within were made for preprocessing.py")