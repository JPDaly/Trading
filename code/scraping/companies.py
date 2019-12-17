import os
from urllib.request import urlretrieve 
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import zipfile

COMPANIES_LIST = "https://www.asx.com.au/asx/research/ASXListedCompanies.csv"
FILE_LOCATION = "../../database/companies/"
FILE_NAME = "asx.csv"

USEFUL_URL = "https://www.asxhistoricaldata.com/"
DOWNLOAD_URL_FORMAT = "https://www.asxhistoricaldata.com/data/week"
ZIP_FILE_LOCATION = "../../database/companies/temp.zip"


def get_asx_companies():
    all_companies = download_all_companies()
    useful = download_useful_companies()
    rows_before = all_companies.shape[0]

    companies_to_drop = []
    for i,company in all_companies.iterrows():
        if company['ASX code'] not in useful[0].values:
            companies_to_drop.append(i)
        elif company['ASX code'] == "PRN": #This is an invalid file name in Windows. Add others as you find them (more trouble than it's worth to include it)
            companies_to_drop.append(i)

    all_companies.drop(all_companies.index[companies_to_drop], inplace=True)
    all_companies.to_csv(FILE_LOCATION+FILE_NAME,index=False)

    print("Removed {0} companies".format(rows_before-all_companies.shape[0]))



#This is no longer working because you require a header when using urlretrieve which isn't defined. 
#Go to https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url to see how to maybe do it with requests
def download_useful_companies():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
    #The above is required otherwise the website doesn't give you access. I found this by going to the network tab in the dev tools in chrome 
    #     and searched (not filtered) for user-agent
    response = requests.get(USEFUL_URL,headers=headers)
    if not response.ok:
        raise ValueError("Unable to retrieve page.")
    page = bs(response.text, 'html.parser')

    for a in page.find_all('a', href=True):
        if DOWNLOAD_URL_FORMAT in a['href']:
            r = requests.get(a['href'], headers=headers)
            if not r.ok:
                print("Error, couldn't retrieve zip file")
                exit()
            with open(ZIP_FILE_LOCATION,'wb') as f:
                f.write(r.content)
            #urlretrieve(a['href'],ZIP_FILE_LOCATION)
            break

    archive = zipfile.ZipFile(ZIP_FILE_LOCATION, 'r')
    file_content = archive.open(archive.namelist()[0])

    return pd.read_csv(file_content, header=None, usecols=[0])
    


def download_all_companies():
    if not os.path.exists(FILE_LOCATION):
        raise ValueError("Error. Couldn't find directory.")

    if os.path.isfile(FILE_LOCATION+FILE_NAME):
        os.remove(FILE_LOCATION+FILE_NAME)

    urlretrieve(COMPANIES_LIST,FILE_LOCATION + FILE_NAME)

    # Just to remove the extra space in the 
    df = pd.read_csv(FILE_LOCATION + FILE_NAME,skiprows=2)
    df.to_csv(FILE_LOCATION+FILE_NAME,index=False)

    # may not need this return statement if I end up only using this function
    return df


if __name__ == "__main__":
    # download_all_companies()
    get_asx_companies()