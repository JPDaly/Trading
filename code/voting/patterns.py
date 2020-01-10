import pandas as pd
import numpy as np

class Pattern:
    SHORTEST_PATTERN = 5 # days (working week)
    LONGEST_PATTERN = 66 # days (average working days in 3 months)
    
    MIN_FLAG_TIME = 5 # 1 week
    MAX_FLAG_TIME = 20 # 4 weeks

    MIN_TRIANGLE_TIME = 15

    means = []
    # Not sure if this is how you initialise a 2D list but we will need them since we need 3 per price range
    max_prices = [] # up to 3?
    min_prices = [] # up to 3 as well, since we will do the inverse of some patterns
    tail_maxs = []
    tail_mins = []
    tail_means = []
    sum_area_below_baseline = []
    sum_area_above_baseline = []
    not_enough_prices = False

    def __init__(self, prices):
        self.n_prices = len(prices)
        self.baseline = prices[-1]
        self.prices = prices
        self.find_features()
        #print("maxs" + str(self.max_prices))
        #print("mins" + str(self.min_prices))
        #print("tailmaxs" + str(self.tail_maxs))
        #print("tailsmins" + str(self.tail_mins))
        #print("tailmeans" + str(self.tail_means))
        #print("below" + str(self.sum_area_below_baseline))
        #print("above" + str(self.sum_area_above_baseline))
        #print("mean" + str(self.means))

    def find_features(self):
        for max_period in range(self.SHORTEST_PATTERN,self.LONGEST_PATTERN+1):
            if max_period >= self.n_prices:
                if max_period == self.SHORTEST_PATTERN:
                    not_enough_prices = True
                break
            self.sum_area_below_baseline.append(0)
            self.sum_area_above_baseline.append(0)
            sub_prices = self.prices[-max_period:]
            n_sub_prices = len(sub_prices)
            
            total = 0
            for i,price in enumerate(sub_prices):
                total += price
                diff = abs(price-self.baseline)
                if price > self.baseline:
                    self.sum_area_above_baseline[-1] += diff
                else:
                    self.sum_area_below_baseline[-1] += diff
            self.means.append(total/n_sub_prices)
            
            # Sort to easily get the min and max prices zipped into form (price,index)
            prices_sorted = sorted(zip(sub_prices,range(n_sub_prices)), reverse=True)
            self.max_prices.append(prices_sorted[:3])
            self.min_prices.append(prices_sorted[-3:])
            # Get tail mean
            if 2*max_period >= self.n_prices:
                self.tail_means.append(sum(self.prices[:-max_period])/len(self.prices[:-max_period]))
                tail_sorted = sorted(zip(self.prices[:-max_period], range(len(self.prices[:-max_period]))), reverse=True)                
            else:
                self.tail_means.append(sum(self.prices[-2*max_period:-max_period])/len(self.prices[-2*max_period:-max_period]))
                tail_sorted = sorted(zip(self.prices[-2*max_period:-max_period], range(len(self.prices[-2*max_period:-max_period]))), reverse=True)
            self.tail_maxs.append(tail_sorted[0])
            self.tail_mins.append(tail_sorted[-1])

    def res_triangle(self):
        max_resem = (0,0) # time resem
        for max_time in range(self.MIN_TRIANGLE_TIME,self.LONGEST_PATTERN):
            resemblance = 0
            data_index = max_time - self.SHORTEST_PATTERN            
            
            if max_time >= self.n_prices:
                break
            # Just to make it to easier to read the equations
            Aa = self.sum_area_above_baseline[data_index]
            Ab = self.sum_area_below_baseline[data_index]
            
            if abs(self.max_prices[data_index][0][0] - self.baseline) > abs(self.min_prices[data_index][0][0] - self.baseline):
                max_diff = (abs(self.max_prices[data_index][0][0] - self.baseline), self.max_prices[data_index][0][1])
            else:
                max_diff = (abs(self.min_prices[data_index][0][0] - self.baseline), self.min_prices[data_index][0][1])

            if max_diff[1] > 0.5*max_time or self.tail_means[data_index] == self.baseline:
                # doesn't resemble a triangle at all
                continue

            # How symmetric about the baseline is the triangle
            if Aa != 0 and Ab != 0: # required for the scenario that both are 0 (division by 0)
                resemblance += (1 - (abs(Aa - Ab)/(Aa + Ab)))/3.0
            # Bigger the difference between the tail mean and the triangle mean the better
            if abs(self.tail_means[data_index]-self.means[data_index]) > max_diff[1]:
                resemblance += 1/3.0
            else:
                resemblance += abs(self.tail_means[data_index]-self.means[data_index])/(3.0*max_diff[0])
            # Percentage of values within the triangle
            resemblance += ((self.within_triangle(max_diff,self.prices[-max_time:]))/3.0)

            # If the tail is above the mean then the triangle indicates a sell
            if self.tail_means[data_index] > self.baseline:
                resemblance *= -1

            if abs(resemblance) > abs(max_resem[1]):
                max_resem = (max_time, resemblance)
        
        return max_resem

    def res_flag(self):
        max_resem = (0,0)
        
        for max_time in range(self.MIN_FLAG_TIME, self.MAX_FLAG_TIME):
            resemblance = 0
            data_index = max_time - self.SHORTEST_PATTERN

            if max_time >= self.n_prices:
                break

            min_flag_price = self.min_prices[data_index][-1][0]
            max_flag_price = self.max_prices[data_index][0][0]
            flag_height = max_flag_price - min_flag_price
            tail_mean = self.tail_means[data_index]
            max_tail_price = self.tail_maxs[data_index][0]
            min_tail_price = self.tail_mins[data_index][0]

            tail_height = max_tail_price - min_tail_price
            if tail_height == 0:
                tail_height = flag_height
            resemblance += (1 - (flag_height/tail_height))/2.0
            if max_tail_price > max_flag_price and min_tail_price > min_flag_price:
                # bear flag
                overlap = max_flag_price - min_tail_price 
                if overlap <= 0:
                    resemblance -= 0.5
                else: 
                    resemblance += -1 + (flag_height/overlap)
            elif max_tail_price < max_flag_price and min_tail_price < min_flag_price:
                # bull flag
                overlap = max_tail_price - min_flag_price 
                if overlap <= 0:
                    resemblance += 0.5
                else: 
                    resemblance += 1 - (flag_height/overlap)
            if abs(resemblance) > abs(max_resem[1]):
                max_resem = (max_time, resemblance)
        return max_resem

    def res_head_and_shoulders(self):
        max_resem = (0,0)
        
        for max_time in range(self.MIN_TRIANGLE_TIME, self.LONGEST_PATTERN):
            resemblance = 0
            bear_hs = True
            if max_time >= self.n_prices:
                break
            data_index = max_time - self.SHORTEST_PATTERN
            
            # is it a bear or bull h&s pattern.
            if self.tail_means[data_index] > self.means[data_index]:
                bear_hs = False
            
            # Sort by time index eg max_sorted[1,2,3] correspond to lshoulder,head,rshoulder
            max_sorted = sorted(self.max_prices[data_index],key = lambda x:x[1])
            min_sorted = sorted(self.min_prices[data_index],key = lambda x:x[1])
            if bear_hs:
                gap = max_sorted[1][0] - min(min_sorted[0][0],min_sorted[1][0])
            else:
                gap = min_sorted[1][0] - max(max_sorted[0][0],max_sorted[1][0])
            
            if gap == 0:
                continue
            
            # Just checking that it resembles a h&s pattern. ie the max_sorted[1] is the largest followed by shoulders and max_sorted[1] is not = shoulders and neither are equal to necks.
            if (bear_hs == True and (max_sorted[1][0] < max_sorted[0][0] or max_sorted[1][0] < max_sorted[2][0])) or (bear_hs == False and (max_sorted[1][0] > max_sorted[0][0] or max_sorted[1][0] > max_sorted[2][0])) or max_sorted[1][0] == min_sorted[0][0] or max_sorted[1][0] == min_sorted[1][0] or max_sorted[0] == min_sorted[0] or max_sorted[0] == min_sorted[1] or max_sorted[2] == min_sorted[0] or max_sorted[2] == min_sorted[1]:
                continue
                
            # The largest gap (biggest value minus the smallest
            if bear_hs:
                resemblance += (max_sorted[1][0] - max(max_sorted[0][0],max_sorted[2][0]))/(4*gap)
                resemblance += (max(max_sorted[0][0],max_sorted[2][0]) - max(min_sorted[0][0],min_sorted[1][0]))/(4*gap)
                resemblance += (1 - (abs(max_sorted[2][0] - max_sorted[0][0])/gap))/4            
                resemblance += (1 - (((max_sorted[1][1]-max_sorted[0][1]) - (max_sorted[2][1]-max_sorted[1][1]))/gap))/4
            else:
                resemblance -= (min_sorted[1][0] - min(min_sorted[0][0],min_sorted[2][0]))/(4*gap)
                resemblance -= (min(min_sorted[0][0],min_sorted[2][0]) - min(min_sorted[0][0],min_sorted[1][0]))/(4*gap)
                resemblance -= (1 - (abs(min_sorted[2][0] - min_sorted[0][0])/gap))/4            
                resemblance -= (1 - (((min_sorted[1][1]-min_sorted[0][1]) - (min_sorted[2][1]-min_sorted[1][1]))/max_time))/4
            
            
            if abs(resemblance) > abs(max_resem[1]):
                max_resem = (max_time, resemblance)
        
        return max_resem
    
    def res_double_top(self):
        max_resem = (0,0)
        
        for max_time in range(self.MIN_TRIANGLE_TIME, self.LONGEST_PATTERN):
            resemblance = 0
            bear_dt = True
            
            if max_time >= self.n_prices:
                break

            data_index = max_time - self.SHORTEST_PATTERN            
            
            # max_prices,min_price,mean = double_top_features(prices[-min_time:])
            mean = self.means[data_index]
            
            if self.means[data_index] < self.tail_means[data_index]:
                bear_dt = False
                min_price = sorted(self.min_prices[data_index][-2:], key = lambda x:x[1])
                max_prices = self.max_prices[data_index][0]
            else:
                max_prices = sorted(self.max_prices[data_index][:2], key = lambda x:x[1])
                min_price = self.min_prices[data_index][-1]

            if bear_dt:
                if min_price[1] > max(max_prices[1][1],max_prices[0][1]) or min_price[1] < min(max_prices[1][1],max_prices[0][1]):
                    continue
                resemblance -= (1-(abs(max_prices[1][0] - max_prices[0][0])/max(max_prices[1][0],max_prices[0][0])))/3
                time_distances = (abs(max_prices[1][1] - min_price[1]), abs(max_prices[0][1] - min_price[1]))
                resemblance -= (1-((time_distances[1] - time_distances[0])/max(time_distances[1],time_distances[0])))/3
                max_price_ave = (max_prices[1][0] + max_prices[0][0])/2
                distances_from_mean = (abs(max_price_ave - mean), abs(min_price[0] - mean))
                if distances_from_mean[0] != 0 or distances_from_mean[1] != 0:
                    resemblance -= (1-(abs(distances_from_mean[1]-distances_from_mean[0])/max(distances_from_mean[1], distances_from_mean[0])))/3
            else:
                if max_prices[1] > min(min_price[1][1],min_price[0][1]) or max_prices[1] < max(min_price[1][1],min_price[0][1]):
                    continue
                resemblance += (1-(abs(min_price[1][0] - min_price[0][0])/min(min_price[1][0],min_price[0][0])))/3
                time_distances = (abs(min_price[1][1] - max_price[1]), abs(min_price[0][1] - max_prices[1]))
                resemblance += (1-((time_distances[1] - time_distances[0])/min(time_distances[1],time_distances[0])))/3
                min_price_ave = (min_price[1][0] + min_price[0][0])/2
                distances_from_mean = (abs(min_price_ave - mean), abs(max_prices[0] - mean))
                if distances_from_mean[0] != 0 or distances_from_mean[1] != 0:
                    resemblance += (1-(abs(distances_from_mean[1]-distances_from_mean[0])/min(distances_from_mean[1], distances_from_mean[0])))/3
            
            if abs(resemblance) > abs(max_resem[1]):
                max_resem = (max_time, resemblance)
                
        return max_resem

    def within_triangle(self,max_diff,sub_prices):
        gradient = max_diff[0]/(len(sub_prices)-max_diff[1])
        y_intercept = gradient*len(sub_prices)
        count = 0
        for i,price in enumerate(self.prices):
            if abs(price-self.prices[-1]) < (-gradient*i + y_intercept):
                count += 1

        return count/len(sub_prices)




def get_patterns(companies):
    COLUMNS = ["asx code","triangle","flag","h&s","double_top","triple_top","mean"]
    PRICES_LOC = "../../database/historical/asx/prices/{0}.csv"
    patterns_df = pd.DataFrame(columns=COLUMNS)
    n_companies = len(companies)
    for i,company in enumerate(companies):
        print("Working on company: {0}/{1}".format(i+1,n_companies), end='\r')
        try:
            prices_df = pd.read_csv(PRICES_LOC.format(company))
        except:
            continue
        #I suspect that maybe my methods are just bad. I'm now passing in a list that doesn't contain nan s
        pattern = Pattern(prices_df['Close'].dropna().tolist())
        #print(prices_df['Close'].dropna().tolist())
        patterns_df.loc[i,COLUMNS[0]] = company
        if pattern.not_enough_prices:
            patterns_df.loc[i,COLUMNS[1]] = 0
            patterns_df.loc[i,COLUMNS[2]] = 0
            patterns_df.loc[i,COLUMNS[3]] = 0
            patterns_df.loc[i,COLUMNS[4]] = 0
        else:
            patterns_df.loc[i,COLUMNS[1]] = pattern.res_triangle()[1]
            patterns_df.loc[i,COLUMNS[2]] = pattern.res_flag()[1]
            patterns_df.loc[i,COLUMNS[3]] = pattern.res_head_and_shoulders()[1]
            patterns_df.loc[i,COLUMNS[4]] = pattern.res_double_top()[1]
        #print("triangle: " + str(pattern.res_triangle()))
        #print("flag" + str(pattern.res_flag()))
        #print("h&s" + str(pattern.res_head_and_shoulders()))
        #print("double top" + str(pattern.res_double_top()))
        #if i == 0:
        #    exit()
    return patterns_df



if __name__ == '__main__':
    pattern = Pattern([26,10,19,28,10,14,15,30,9,16,7,16,8,14,20,30,15,27,25,5,26,11,12,2,15,12,16,3,28,9])
    # print(pattern.means)
    print("triangle: " + str(pattern.res_triangle()))
    print("flag" + str(pattern.res_flag()))
    print("h&s" + str(pattern.res_head_and_shoulders()))
    print("double top" + str(pattern.res_double_top()))
    pattern = Pattern([44,28,50,73,25,18,66,60,2,13,24,34,8,81,90,71,4,86,33,17,34,64,96,51,45,39,5,79,62,68,56,10,5,50,81,6,65,87,96,99,81,63,57,47,36,38,40,52,57,14,59,10,28,97,6,41,40,11,9,71,20,62,8,4,39,3,97,59,51,56,77,15,77,42,3,37,86,99,36,72,30,55,87,63,17,63,59,42,18,73,12,51,47,12,5,32,92,8,1,9,1,826,1,8,6,12,5,86,73,21,57,91,98,41,48,48,8,29,1,6,4,4,7,6,9575,270,6,9,5,7,2,2,9,1,7,5,6,7,1,1,6,7,2,2,9,1,9,8,169,9,15,28,1,73,50,67,12,74,85,83,22,28,71,8,3,5,20])
    # print(pattern.means)
    print("triangle: " + str(pattern.res_triangle()))
    print("flag" + str(pattern.res_flag()))
    print("h&s" + str(pattern.res_head_and_shoulders()))
    print("double top" + str(pattern.res_double_top()))
    
    
    
    