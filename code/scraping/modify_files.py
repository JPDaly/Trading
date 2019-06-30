import os 
import pandas as pd

directory = "../../database/historical/asx/stats/"

files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory,f))]

for file in files:
	pass
	# df = pd.read_csv(directory+file)
	# df.drop_duplicates(subset='Date',keep="last",inplace=True)
	# df.to_csv(directory+file,index=False)
	# with open(directory+file,"w") as f:
	# 	f.write("2019-05-15")