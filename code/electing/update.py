# Update the user on what the program suggests 
# Let the user update what they have bought and sold

import pandas as pd

OWNED_STOCKS_DIR = "../../database/state/owned.csv"
MAX_MENU_OPTIONS = 3

class GUI:

	def __init__(self):
		self.owned_df = pd.read_csv(OWNED_STOCKS_DIR)
		self.functions = [self.print_owned, self.update, self.recommendations]

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
				break
			elif choice > MAX_MENU_OPTIONS or choice < 0:
				print("That isn't an option.")
				continue
			self.functions[choice-1]()


	def recommendations(self):
		# They can either see the top n stocks for each sector (and choose what market cap or just the top without worrying about that)
		# Or they can see a single sector and then look at what market cap they care about
		pass

	def update(self):
		# Ask if you want to sell or buy (or return to menu)
		# If sell give them a numbered list of what they can sell
		# If buy let them type the stock, check if it's 3 characters and if it's in the list of companies. 
			# If it isn't in the list, ask if they still want to add it to the owned list.
		pass

	def print_owned(self):
		print("\nCurrently owned stocks:")
		print(self.owned_df.transpose())



if __name__ == "__main__":
	GUI().menu()