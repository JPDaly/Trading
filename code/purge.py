import os
from datetime import datetime
import pandas as pd

PURGING_AGE = 10

# Folders:
FOLDERS = ["../database/historical/asx/prices/","../database/historical/asx/stats/"]
SUB_FOLDER = "last_updated/{0}.txt"
DATE_FORMAT = '%Y-%m-%d'


def purge():
	today = datetime.today()
	for folder in FOLDERS:
		files = [f for f in os.listdir(folder) if os.path.isfile(folder+f)]
		print("\nChecking folder {0}".format(folder))
		for file in files:
			print("Checking file {0}".format(file), end="\r")
			try:
				df = pd.read_csv(folder+file)
			except:
				print("\nCouldn't read file")
				continue
			rows_to_drop = []
			for i,row in df.iterrows():
				if ((today-datetime.strptime(row['Date'],DATE_FORMAT)).days/365) > PURGING_AGE:
					rows_to_drop.append(i)
				else:
					break
			df.drop(rows_to_drop,inplace=True)
			if(df.empty):
				os.remove(folder+file)
				print("\nDeleted file {0}".format(file))
				last_updated_file = folder+(SUB_FOLDER.format(file.split('.')[0]))
				if os.path.isfile(last_updated_file):
					os.remove(last_updated_file)
					print("Deleted file {0}".format(last_updated_file.split('/')[-1]))
	print()

	#loop through each folder 
	#loop through each file in folder
	#if entry in file is older than "PURGING_AGE" delete entry 
	#if folder is now empty delete file and any other related files (eg last updated file)




if __name__ == "__main__":
	purge()