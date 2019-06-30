import os 

for file in os.listdir("../../database/historical/asx/prices/last_updated/"):
	with open("../../database/historical/asx/prices/last_updated/"+file,"w") as f:
		f.write("2019-05-15")