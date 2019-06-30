import os
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from Yahoo import YahooStats
import re
import datetime


COMPANIES_LIST_LOCATION = "../../database/companies/asx.csv"
STATISTICS_LOCATION = "../../database/daily/asx.csv"

STATS_DATABASE_LOC = "../../database/historical/asx/stats/{0}.csv"
LAST_UPDATED = "../../database/historical/asx/stats/last_updated/{0}.txt"


def get_statistics(date):
	yahoo = YahooStats()
	columns = ['asx code', 'Date', 'sector'] + yahoo.ROW_TITLES

	companies = pd.read_csv(COMPANIES_LIST_LOCATION)
	n_rows = companies.shape[0]
	
	statistics_df = pd.DataFrame(columns=columns)

	for i,company in companies.iterrows():
		print("Scraping stock " + str(i+1) + "/" + str(n_rows), end="\r")
		yahoo.set_stock(company['ASX code'])
		statistics_df = statistics_df.append(pd.DataFrame([[yahoo.stock,date,company['GICS industry group']] + yahoo.get_stats()],columns=columns),ignore_index=True)

	if os.path.isfile(STATISTICS_LOCATION):
		os.remove(STATISTICS_LOCATION)

	statistics_df.drop_duplicates().to_csv(STATISTICS_LOCATION,index=False)



def append_stats(date):
	df = pd.read_csv(STATISTICS_LOCATION)
	columns = df.columns
	# there's no check for the last time this was updated. Instead it's possible to use drop_duplicates() as shown in https://jamesrledoux.com/code/drop_duplicates
	# to avoid dealing with them later on
	for i,company in df.iterrows():
		if os.path.isfile(STATS_DATABASE_LOC.format(company['asx code'])):
			temp = pd.read_csv(STATS_DATABASE_LOC.format(company['asx code']))
			temp = temp.append(company,ignore_index=True)
			temp.to_csv(STATS_DATABASE_LOC.format(company['asx code']),index=False)
		else:
			temp = pd.DataFrame([company.values],columns=columns)
			temp.to_csv(STATS_DATABASE_LOC.format(company['asx code']),index=False)

		#currently only doing this in case I want to use it in the future for something 
		with open(LAST_UPDATED.format(company['asx code']),"w") as f:
			f.write(date)


if __name__ == "__main__":
	get_statistics(datetime.date.today().strftime("%Y-%m-%d"))
	append_stats(datetime.date.today().strftime("%Y-%m-%d"))