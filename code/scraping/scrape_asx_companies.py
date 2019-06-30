import datetime
from statistics import get_statistics, append_stats
from companies import *
from prices import get_latest_prices



def scrape_asx_companies():
	print("\nStart time: " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
	# get_asx_companies()
	get_asx_companies()
	print("\nFinished getting the companies at " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
	
	today = datetime.date.today().strftime("%Y-%m-%d")
	get_statistics(today)
	print("\nFinished scraping stats at " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")

	print("Appending stats to the database...")
	append_stats(today)
	print("\n\nFinished appending stats at " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")	

	get_latest_prices()
	print("\n\nFinished scraping prices at " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")	

	
	# purge old data (see purge.py)	

if __name__ == "__main__":
	scrape_asx_companies()