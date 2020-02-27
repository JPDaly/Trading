from sklearn import preprocessing
import pandas as pd
import warnings
import numpy as np
from patterns import *


COMPANIES_LIST = "../../database/companies/asx.csv"
STATS = "../../database/historical/asx/stats/{0}.csv"
PRICES = "../../database/historical/asx/prices/{0}.csv"
VOTES_SECTOR = "../../database/votes/{0}.csv"

COLUMNS = ["asx code","Date","sector","Market cap (intra-day)",
            "Enterprise value","Trailing P/E","Forward P/E","PEG ratio (5-yr expected)",
            "Price/sales","Price/book","Enterprise value/revenue","Enterprise value/EBITDA"
            ]

def voting():
    companies = pd.read_csv(COMPANIES_LIST)
    min_max = preprocessing.MinMaxScaler()
    warnings.filterwarnings("error")

    for n_sectors,sector in enumerate(companies['GICS industry group'].drop_duplicates()):
        # create empty dataframe with columns just for the stats part
        print("Working on sector: {0} ({1}/{2})".format(sector, n_sectors+1,len(companies['GICS industry group'].drop_duplicates())))
        sector_df = pd.DataFrame(columns=COLUMNS)
        for i,company in companies[companies['GICS industry group'] == sector].iterrows():
            # append most recent stats data from file to above df
            try:
                sector_df = sector_df.append(pd.read_csv(STATS.format(company['ASX code'])).tail(1),ignore_index=True)
            except:
                continue
        #Change stat values to indicate worth
        sector_df = stat_calculations(sector_df)
        # run normalise_stats() and any other stats related functions
        sector_df = normalise_stats(sector_df,min_max)
        # run pattern recognition on the prices and append results to end of dataframe created with the stats function
        sector_df = categorise_cap(sector_df)
        # I think it's a good idea to call the price_patterns functions here
        sector_df = sector_df.merge(get_patterns(companies[companies['GICS industry group'] == sector]['ASX code'].values),on='asx code')
        # save pre_processed df to file marked sector.csv
        sector_df.to_csv(VOTES_SECTOR.format(sector),index=False)

#See the notes in stats.txt in documentation for the logic behind this function    
def stat_calculations(df):
    df["Enterprise value"] = df["Market cap (intra-day)"] - df["Enterprise value"]
    df["Enterprise value/EBITDA"] = 10 - df["Enterprise value/EBITDA"]
    
    for i,value in enumerate(df["Enterprise value/EBITDA"].values):
        if value < 0:
            df.loc[i,"Enterprise value/EBITDA"] = value - 10
        else:
            df.loc[i,"Enterprise value/EBITDA"] = 10 - value
        
    
    for column in df.columns.values[4:]:
        if column == "Enterprise value" or column == "Enterprise value/EBITDA":
            continue
        max = df[column].max()
        for i,value in enumerate(df[column]):
            if value <= 0:
                df.loc[i,column] = value*-1 + max
        df[column].fillna(df[column].max()+1)
        df[column] = 1/df[column]
    return df


def normalise_stats(df,min_max):
    for column in df.columns.values[4:]:
        data = df[column].values.astype(float)
        try:
            df.loc[:,column] = min_max.fit_transform(data.reshape(-1,1))
        except:
            print(end="")
    return df 

def categorise_cap(df):
    # For ease of reading, the large numbers below are 300M,2B,10B,200B
    df['Market cap (intra-day)'] = pd.cut(df['Market cap (intra-day)'],[0,300000000,2000000000,10000000000,200000000000,np.inf],labels=["micro","small","mid","large","mega"])
    return df


if __name__ == "__main__":
    voting()