import pandas as pd
import numpy as np

companies_loc = "../../database/companies/asx.csv"
stats = "../../database/historical/asx/stats/{0}.csv"

COLUMNS = ["asx code","Date","sector","Market cap (intra-day)",
			"Enterprise value","Trailing P/E","Forward P/E","PEG ratio (5-yr expected)",
			"Price/sales","Price/book","Enterprise value/revenue","Enterprise value/EBITDA"
			]

companies = pd.read_csv(companies_loc)

for i,company in companies.iterrows():
	comp_df = pd.read_csv(stats.format(company['ASX code']))
	# print(comp_df.isin(["inf"]))
	# exit()
	for column in COLUMNS:
		if comp_df[comp_df[columhn]]
	if not comp_df.isin(["inf"]).any():
		print(comp_df)
		exit()



		# This is here so that I can remove any data entries that have "inf" however it might just be worth starting again since I only have 2 entries for stats