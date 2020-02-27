import datetime
import pandas as pd
import os

VOTES_SECTOR = "../../database/votes/{0}"
VOTE_DIR = "../../database/votes/"
NUMBER_COLUMNS = ["Enterprise value","Trailing P/E",
                    "Forward P/E","PEG ratio (5-yr expected)","Price/sales","Price/book","Enterprise value/revenue",
                    "Enterprise value/EBITDA","triangle","flag","h&s","double_top","triple_top","mean"]
RANK_DIR = "../../database/ranks/{}"

def rank():
    files = [f for f in os.listdir(VOTE_DIR) if os.path.isfile(os.path.join(VOTE_DIR,f))]

    for file in files:
        df = pd.read_csv(VOTES_SECTOR.format(file))
        df[NUMBER_COLUMNS] = df[NUMBER_COLUMNS].apply(lambda x: x**3)
        df['date'] = datetime.datetime.now().strftime("%Y-%M-%d")
        df['stat rank'] = df[NUMBER_COLUMNS[:8]].sum(axis=1, skipna=True)
        df['total rank'] = df.sum(axis=1, skipna=True)
        df.sort_values('stat rank', axis=0, ascending=False, inplace=True, kind='quicksort', na_position='last')
        df.to_csv(RANK_DIR.format(file), mode='w', columns=['asx code', 'Market cap (intra-day)', 'date', 'stat rank', 'total rank'], index=False)
    print("Finished ranking companies.\nSee files in \\Trading\\database\\votes for the outputs")


if __name__ == "__main__":
    rank()


# This is obviously a very basic script but it could be more complex if machine learning was involved or if you wanted to
    # ignore certain scenarios. Eg you can't have a good H&S and flag (idk)
    # You also could weight the stat and graph votes differently
# For those reasons this gets a different folder and file
