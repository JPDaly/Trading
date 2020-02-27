import sys
import os

sys.path.append('./scraping')
sys.path.append('./voting')
sys.path.append('./electing')
sys.path.append('./user_interaction')

from scrape_asx_companies import *
from vote import *
from rank import *
from update import *


separator = "----------------------------{}----------------------------"

print(separator.format("SCRAPING"))
os.chdir("./scraping")
scrape_asx_companies()
print(separator.format("VOTING"))
os.chdir("../voting")
voting()
print(separator.format("RANKING"))
os.chdir("../electing")
rank()
#print(separator.format("UPDATING"))
#os.chdir("../user_interaction")
#pd.options.display.max_rows = 1000
#GUI().menu()
print(separator.format("DONE"))