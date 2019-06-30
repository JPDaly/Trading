import os
import re
import requests
from urllib.request import urlretrieve 
from bs4 import BeautifulSoup as bs
from io import StringIO
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class YahooStats:
	QUOTE_URL = "https://au.finance.yahoo.com/quote/"
	STATISTICS = ".AX/key-statistics"
	STATISTICS_TABLE_HEADING = "Valuation measures"
	PE_ROW_NAME = "Trailing P/E"
	MARKET_CAP_ROW_NAME = "Market cap (intra-day)" 
	N_STATS = 9
	ROW_TITLES = [
		"Market cap (intra-day)","Enterprise value","Trailing P/E",
		"Forward P/E","PEG ratio (5-yr expected)","Price/sales","Price/book",
		"Enterprise value/revenue","Enterprise value/EBITDA"
		]
	weird_row_titles = [0,1,3,4,7,8]

	def set_stock(self,stock):
		self.stock = stock
		#retrieving the response is the part that takes the longest to execute
		response = requests.get(self.QUOTE_URL + stock + self.STATISTICS)
		if not response:
			print("\nUnable to retrieve page for stock code: " + stock)
		page = bs(response.text, 'html.parser')
		for div in page.find_all("div"):
			if div.text.find(self.STATISTICS_TABLE_HEADING) != -1:
				self.table = div
				break


	def get_stats(self): # This isn't what is taking ages
		stats = []
		for i,tr in enumerate(self.table.find_all("tr")):
			if i == self.N_STATS:
				break
			for j,row in enumerate(self.ROW_TITLES):
				if tr.text.find(row) != -1:
					tds = tr.find_all("td")
					for td in tds:
						if td.find_all("span") == []:
							stats.append(self.clean_data(td.text,j))
							break
					break
			if len(stats) != i+1:
				# This is because fields that have N\A use span
				stats.append(np.NaN)

		return stats

	def clean_data(self,data,stat_type):
		if data == "N/A":
			return np.NaN
		return self.expand_num(data.replace(',',''))

	def expand_num(self, num):
		if num[-1] == 'm' or num[-1] == 'M':			
			return round(float(num[0:-1])*1000000)
		elif num[-1] == 'k' or num[-1] == 'K':
			return round(float(num[0:-1])*1000)
		elif num[-1] == 'b' or num[-1] == 'B':
			return round(float(num[0:-1])*1000000000)
		try:
			num = float(num)
		except:
			# print("\nCouldn't convert '{0}' to float".format(num))
			return np.NaN
		return float(num)



class YahooPrices:
	timeout = 2
	crumb_link = 'https://finance.yahoo.com/quote/{0}.AX/history?p={0}.AX'
	crumble_regex = r'CrumbStore":{"crumb":"(.*?)"}'
	quote_link = 'https://query1.finance.yahoo.com/v7/finance/download/{quote}.AX?period1={dfrom}&period2={dto}&interval=1d&events=history&crumb={crumb}'
	initialising_symbol = "COL" #using coles because they should last a while lol

	def __init__(self):
		#Although no parameters are passed in this is important because we need a new crumb every time
		self.session = requests.Session()
		self.get_crumb()
		

	def get_crumb(self):
		response = self.session.get(self.crumb_link.format(self.initialising_symbol), timeout=self.timeout)
		response.raise_for_status()
		match = re.search(self.crumble_regex, response.text)
		if not match:
			raise ValueError('Could not get crumb from Yahoo Finance')
		else:
			self.crumb = match.group(1)

	def get_quote(self,symbol,days_back):
		attempts = 0
		dt = timedelta(days=days_back)
		now = datetime.utcnow()
		dateto = int(now.timestamp())
		datefrom = int((now - dt).timestamp())
		url = self.quote_link.format(quote=symbol, dfrom=datefrom, dto=dateto, crumb=self.crumb)
		
		while(attempts < 5):
			response = self.session.get(url)
			if response.ok:
				return pd.read_csv(StringIO(response.text), parse_dates=['Date'])
			if attempts == 0:
				print()
			print("Error. Bad Response #{0}".format(attempts), end='\r')
			self.session = requests.Session()
			self.get_crumb()
			attempts+=1
		
		return pd.DataFrame()




