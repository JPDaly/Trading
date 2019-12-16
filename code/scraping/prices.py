import os
import requests
import pandas as pd
from datetime import date, datetime
from urllib.request import urlretrieve 
from Yahoo import YahooPrices
import keyboard
import time

CRUMB_LOC = "./resources/crumb.txt"
COMPANIES_LIST_LOCATION = "../../database/companies/asx.csv"
DATABASE_LOC = "../../database/historical/asx/prices/{0}.csv"
LAST_UPDATED_LOG = "../../database/historical/asx/prices/last_updated/{0}.txt"
DATE_FORMAT = '%Y-%m-%d'

def get_latest_prices():
    yahoo = YahooPrices()
    companies = pd.read_csv(COMPANIES_LIST_LOCATION)
    n_rows = companies.shape[0]
    today = datetime.today()
    pause = False
    
    print("Press 'p' to pause and 'r' resume")
    for i,company in companies.iterrows():
        while(True):
            if pause or keyboard.is_pressed('p'):
                pause = True
            if not pause or keyboard.is_pressed('r'):
                pause = False
                break
            time.sleep(2)
        
        print("Downloading prices " + str(i+1) + "/" + str(n_rows), end="\r")
        code = company['ASX code']
        last_updated = '2012-01-01'    #random max last date doesn't work with 1970
        if os.path.isfile(LAST_UPDATED_LOG.format(code)):
            with open(LAST_UPDATED_LOG.format(code)) as file:
                last_updated = file.read()

        days_back = (today-datetime.strptime(last_updated,DATE_FORMAT)).days
        if days_back == 0:
            continue
        
        df = yahoo.get_quote(code,days_back)
        if df.empty:
            print("\nCouldn't get prices for {0}".format(code))
            continue
        
        append_data(df,code,today.strftime(DATE_FORMAT))
            
def append_data(dataframe,code,today):
    
    if os.path.isfile(DATABASE_LOC.format(code)):
        temp = pd.read_csv(DATABASE_LOC.format(code))
        dataframe = temp.append(dataframe,ignore_index=True)
    
    dataframe['Date'] = pd.to_datetime(dataframe.Date)
    dataframe['Date'] = dataframe['Date'].dt.strftime(DATE_FORMAT)    
    dataframe.drop_duplicates(subset='Date',keep="first",inplace=True)
    dataframe.to_csv(DATABASE_LOC.format(code),index=False)

    with open(LAST_UPDATED_LOG.format(code),'w') as f:
        f.write(today)


if __name__ == "__main__":
    get_latest_prices()