# Update the user on what the program suggests 
# Let the user update what they have bought and sold

import pandas as pd
import numpy as np
import os

OWNED_STOCKS_DIR = "../../database/state/owned.csv"
COMPANIES_LIST_DIR = "../../database/companies/asx.csv"
RANKS_DIR = "../../database/ranks/"
MAX_MENU_OPTIONS = 3

class GUI:

	def __init__(self):
        
		self.owned_df = pd.read_csv(OWNED_STOCKS_DIR)
		self.functions = [self.print_owned, self.update, self.recommendations]
		self.companies = pd.read_csv(COMPANIES_LIST_DIR)

	def menu(self):
		while(True):
			print("\nMenu\n")
			
			print("Options:\n")
			print("1. See owned stocks.")
			print("2. Update owned stocks.")
			print("3. See recommendations.")
			print("0. Exit")
			try:
				choice = int(input("Input: "))
			except:
				print("\nThat isn't a number.")
				continue

			if choice == 0:
				self.owned_df.to_csv(OWNED_STOCKS_DIR,index=False)
				break
			elif choice > MAX_MENU_OPTIONS or choice < 0:
				print("That isn't an option.")
				continue
			self.functions[choice-1]()


	def recommendations(self):

		files = [f.split('.csv')[0] for f in os.listdir(RANKS_DIR) if os.path.isfile(os.path.join(RANKS_DIR,f))]

		print("\nEnter 0 to return to menu at any time.\n")
		while True:
			print("Choose a sector from below\n")
			for i,sector in enumerate(files):
				print("{0}. {1}".format(i+1,sector))
			choice = int(input("Input: "))
			if choice == 0:
				return
			elif choice >= len(files) or choice <= 0: 
				print("That wasn't an option.")
				continue
			print(pd.read_csv(RANKS_DIR+files[choice-1]+".csv"))
			input("Enter anything to finish reading.")


	def update(self):
		step = 0
		print("\nEnter 0 to return to menu at any time.\n")
		while True:
			if step == 0:
				user_input = input("\nDo you want to add (a) or remove (r) owned stocks: ")
				if user_input == '0':
					return
				if user_input not in ['a','r']:
					print("That wasn't an option.")
					continue
				step+=1
			elif step == 1 and user_input == 'a':
				sector = 1
				bought_stock = input("Enter stock code that you bought: ").upper()
				if bought_stock == '0':
					return
				if len(bought_stock) != 3:
					print("Invalid stock code.")
					continue
				if bought_stock not in self.companies['ASX code'].values:
					print("Couldn't find this stock in our list of companies.")
					decision = input("Enter \'y\' if you still want to add {} to your list. Otherwise type \'n\': ".format(bought_stock))
					if decision == 'n':
						continue
					elif decision != 'y':
						print("That wasn't an option.")
						continue
					sector = "Unknown"
					if sector not in self.owned_df.columns:
						self.owned_df[sector] = np.nan
				else:
					sector = self.companies.loc[self.companies['ASX code'] == bought_stock, 'GICS industry group']
				if not self.isNaN(self.owned_df[sector].values[0]) and bought_stock in self.owned_df[sector].values:
					# This will produce a warning if you're checking a column that's empty
					print("You already have {} listed.".format(bought_stock))
					continue

				self.owned_df.loc[len(self.owned_df[sector].dropna().values),sector] = bought_stock
				
				step=0
			elif step == 1 and user_input == 'r':
				stock_to_drop = input("Enter stock you want to remove: ").upper()
				if stock_to_drop == '0':
					return
				if len(stock_to_drop) != 3:
					print("Invalid stock code.")
					continue
				if stock_to_drop not in self.companies['ASX code'].values:
					sector = "Unknown"
				else:
					sector = self.companies.loc[self.companies['ASX code'] == stock_to_drop, 'GICS industry group']

				self.owned_df[self.owned_df[sector] == stock_to_drop] = np.nan

				step=0


	def print_owned(self):
		temp_df = self.owned_df.copy()
		print("\nCurrently owned stocks:")
		print(temp_df.transpose().fillna(""))

	def isNaN(self,value):
		return value != value


if __name__ == "__main__":
	pd.options.display.max_rows = 1000
	GUI().menu()