from pandas.io.json import json_normalize  
import json



# This code retreives gvkeys
# query = db.raw_sql('select distinct gvkey, tic from comp.security')
# gv_df = pd.DataFrame(query, columns = ['gvkey','tic'])
# gv_df.to_csv('Tic_to_GVkey.csv')

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

