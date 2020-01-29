import datetime 
import json
import requests
import pandas as pd
from pandas.io.json import json_normalize  
import numpy as np
import wrds

api_key = 'WAJ9IT2UEAO8G7P0'

# Define function to get data
def get_data(ticker, interval):

    """
    Main function for retreiving data from AlphaVantage. 

    ### Params - 
    ticker: stock ticker, string
    interval: interval of data, likely daily, but can be '5min' or '30min' for intraday information

    ### Returns -
    1. stock ticker, string
    2. pandas series where the name is the stock ticker, past 267 days of information (~1 year less days where market is closed)
    """
    
    daily_url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+ ticker +'&outputsize=full&apikey='+api_key
    response = requests.get(daily_url)
    index_list = response.json()
    index = 'Time Series (' + interval + ')'
    df = pd.DataFrame(index_list[index]).T
    df = df['4. close'].iloc[0:267].astype(float)
    series = pd.Series(df.pct_change(), name=ticker)[1:]

    return series


# Get the tickers we care about, all in the S&P
# tickers = [item for sublist in pd.read_csv('All_S&P_tickers.csv').values for item in sublist]
# n = len(tickers[0:5])
# i=0
# returns = pd.DataFrame()
# for ticker in tickers[0:5]:
#     returns[ticker] = get_data(ticker, 'Daily')
#     i += 1
#     print(round(i/n, 2))

# debugging_data = pd.read_csv('debugging_data.csv', index_col=0)

def time_series(series):
    # Time series scan
    if np.sum(series) > .1:
        return True
    else:
        return False

def cross_section(series):
    # Cross sectional scan
    bools = []
    Mean = np.mean(series)
    Std = np.std(series)
    for datapoint in series:
        if datapoint>Mean+Std:
            bools.append(True)
        else:
            bools.append(False)
    return bools

ts_bools = []
# for series in debugging_data:
#     ts_bools.append(time_series(debugging_data[series]))

# cs_bools = cross_section(debugging_data.iloc[0])

# Determine region of interest
today = datetime.datetime.now().strftime('%Y-%m-%d')
year_ago = (datetime.datetime.now() - datetime.timedelta(days = 366)).strftime('%Y-%m-%d')

# Load gv keys
df = pd.read_csv('C:/Users/turbo/Finance projects/Global factor premiums/Trading-algos/All_S&P_tickers.csv')
df[['gvkey','TICKER']]
gvkeys = str(tuple(df['gvkey'].values))

# Query WRDS
db = wrds.Connection()
query = db.raw_sql("""select datadate, gvkey, ajexdi, prccd from comp.sec_dprc where cast(gvkey as int) in {} and (iid = '01' and datadate between '{}' and '{}');""".format(gvkeys, year_ago, today))
query['datadate'] = query['datadate'].astype(str)
main = query.pivot_table(values=['ajexdi','prccd'], index=['gvkey', 'datadate'])

# main['mkt_val'] = main['cshoc']*main['prccd']
# main['return'] = main['mkt_val'].pct_change().dropna()
# print('query executed!')

# db = wrds.Connection()
# query = db.raw_sql("""select distinct gvkey from comp.sec_dprc where datadate between '{}' and '{}'""".format(year_ago, today))
# print(query)

# main = pd.read_csv('temp_main_data.csv', index_col=['gvkey','datadate'])

main['prc_adj'] = main['prccd']/main['ajexdi']
main['return'] = main['prc_adj'].pct_change().dropna()
main = main.drop(index='2019-01-28', level=1)
main = main.groupby(level=0).apply(lambda d: d.tail(-1))
#print(main['return'].sort_values())
#print(main.xs('2019-01-28', level='datadate'))
print(main.loc['014794'].iloc[190:210])











# This code retreives gvkeys
# query = db.raw_sql('select distinct gvkey, tic from comp.security')
# gv_df = pd.DataFrame(query, columns = ['gvkey','tic'])
# gv_df.to_csv('Tic_to_GVkey.csv')

