
import tuneta
#from tuneta.tune_ta import TuneTA
import pandas as pd

from pandas_ta import percent_return

from sklearn.model_selection import train_test_split

#import yfinance as yf

if __name__ == "__main__":
    X = yf.download("SPY", period ="10y", interval ="1d", auto_adjust = True)
    y = percent_return(X.Close, offset=-1)
    print(X)

    client = CryptoHistoricalDataClient()

    request_params = CryptoBarsRequest(
        symbol_or_symbols="BTC/USD",
        timeframe=TimeFrame.Day,
        start=datetime.datetime(year=2022, month=9, day=1)
    )

    bars = client.get_crypto_bars(request_params)
    print(bars)
