import datetime 
import requests
import pandas as pd
import numpy as np
import wrds

# Determine region of interest
today = datetime.datetime.now().strftime('%Y-%m-%d')
yesterday = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime('%Y-%m-%d') 
year_ago = (datetime.datetime.now() - datetime.timedelta(days = 366)).strftime('%Y-%m-%d')

# Load gv keys
df = pd.read_csv('C:/Users/turbo/Finance projects/Global factor premiums/Trading-algos/All_S&P_tickers.csv', index_col='gvkey')
gvkeys = str(tuple(df.index.values))
print(gvkeys)

# # Query WRDS
# db = wrds.Connection()
# query = db.raw_sql("""select datadate, gvkey, ajexdi,cshoc, prccd from comp.sec_dprc where cast(gvkey as int) in {} and (iid = '01' and datadate between '{}' and '{}');""".format(gvkeys, year_ago, today))
# query['datadate'] = query['datadate'].astype(str)

# # Format pivot table
# main = query.pivot_table(values=['ajexdi','prccd','cshoc'], index=['gvkey', 'datadate'])
# main['prc_adj'] = main['prccd']/main['ajexdi']
# main['return'] = main['prc_adj'].pct_change().dropna()
# main = main.groupby(level=0).apply(lambda d: d.tail(-1))

# Temp for efficient execution
main = pd.read_csv('temp_main_data.csv',index_col=['gvkey','datadate'])

# Find the indices of the top 20% performing stocks in the S&P in the past month
xc_momentum_indices = main.groupby(level=0).tail(30).sum(level=0).sort_values(by='return',ascending=False).iloc[:100].index

# Find the indices of stocks who have cumulative 1 year trailing returns of over 10%
cumulative_returns = main.sum(level=0).sort_values(by='return', ascending=False)['return']
trend_indices = cumulative_returns[cumulative_returns > 0.1].index

# Find intersection of indices
def intersection(list1,list2):
    return [idx for idx in list1 if idx in list2]
 
# Get tickers of stocks to buy
test_indices = intersection(trend_indices,xc_momentum_indices)
tickers = df.loc[test_indices,['COMNAM','TICKER']]

buys_yesterday = pd.read_csv('buys_today.csv', index_col='gvkey')

# Companies we sell
sell_list = [row['COMNAM'] for index, row in buys_yesterday.iterrows() if index not in test_indices]

# Companies we buy
buy_list = df.loc[[index for index in test_indices if index not in buys_yesterday.index.values], 'COMNAM'].values

# Write todays buys to file after we have figured out what to buy for the day
#tickers.to_csv('buys_today.csv')

tickers.to_csv('buys_today.txt', header=None, index=None, sep=' ', mode='a')

email_string = """
Good Morning,

The algorithm has purchased {:}, and sold

""".format(*buy_list)
