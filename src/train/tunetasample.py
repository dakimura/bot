
import tuneta
#from tuneta.tune_ta import TuneTA
import pandas as pd
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame
from pandas_ta import percent_return
import datetime
from sklearn.model_selection import train_test_split

#import yfinance as yf

if __name__ == "__main__":
    X = yf.download("SPY", period ="10y", interval ="1d", auto_adjust = True)
    y = percent_return(X.Close, offset=-1)
    print(X)
