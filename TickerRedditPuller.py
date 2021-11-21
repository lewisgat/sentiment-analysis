from  psaw import PushshiftAPI
import datetime
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import pandas_datareader as web
from dateutil import relativedelta

api = PushshiftAPI()
start_time = datetime.datetime(2021,9,30)
end_time = datetime.datetime(2021,10,31)




NASDAQ_df = pd.read_csv('NASDAQ.csv')
AMEX_df = pd.read_csv('AMEX.csv')
NYSE_df = pd.read_csv('NYSE.csv')

frames = [NASDAQ_df, AMEX_df, NYSE_df]
temp = pd.concat(frames)
cols = list(temp.columns)
temp.drop(cols[2:], axis = 1, inplace = True)
tickers = temp['Symbol'].tolist()

def stonk_mentions(start_time, end_time, tickers):
    
    start_time_int = int(start_time.timestamp())
    end_time_int = int(end_time.timestamp())
    next_month_time = end_time + relativedelta.relativedelta(months=1)
    
    submissions = api.search_submissions(after = start_time_int, before = end_time_int,
                                subreddit = 'wallstreetbets',
                                filter = ['url', 'author', 'title', 'subreddit'])
    
    df = pd.DataFrame({"Ticker" : tickers})
    
    mentions = []
    for submission in submissions:
        words = submission.title.split()
        cashtags = list(set(filter(lambda word: word.upper().startswith('$'), words)))
        
        if len(cashtags) > 0:
            for cashtag in cashtags:
                tick = cashtag.replace('$','')
                if tick in tickers:
                    mentions.append(tick)
    
    occurances = []
    returns_0m = []
    returns_1m = []
    vol_0m = []
    vol_1m = []
    for tick in tickers:
        try: 
            occurances.append(mentions.count(tick.upper()))
        except:
            pass 
        
    df['Mentions'] = occurances 
    df2 = df[df['Mentions'] > 20]
    df2 = df2.sort_values('Mentions', axis = 0, ascending = False)
    
    
    for tick in list(df2['Ticker']):
        try:
            price_0m = web.get_data_yahoo(tick,
                            start = start_time,
                            end = end_time)['Adj Close']
            returns_0m.append( (price_0m[-1]/price_0m[0]) - 1 )
            vol_0m.append( np.std(price_0m.pct_change()) ) 
        
            price_1m = web.get_data_yahoo(tick,
                            start = end_time,
                            end = next_month_time)['Adj Close']
            returns_1m.append( (price_1m[-1]/price_1m[0]) - 1 )
            vol_1m.append( np.std(price_1m.pct_change()) )
        except:
            pass 
    
    

    df2['Return 0M'] = returns_0m     #returns for the month we measured
    df2['Vol 0M'] = vol_0m
    df2['Return 1M'] = returns_1m     #returns for the month we measured
    df2['Vol 1M'] = vol_1m
    
    #df2 = df2[df2['Mentions'] > 20] 
    
    # plt.rcdefaults()
    # fig, ax = plt.subplots()
    # y_pos = np.arange(len(df2['Ticker']))
    # ax.barh(y_pos, df2['Mentions'], align = 'center')
    # ax.set_yticks(y_pos)
    # ax.set_yticklabels(df2['Ticker'])
    # ax.invert_yaxis()
    # ax.set_title('r/WallStreetBets Stonk Mentions')
    
        
    plt.show()
    return df, df2

df, df2 = stonk_mentions(start_time, end_time, tickers)

df2.reset_index(inplace = True)
df2.drop(columns = 'index', axis = 1, inplace = True)


np.corr(
