from datetime import datetime, timedelta
from typing import List, Union, Dict

# from tuneta.tune_ta import TuneTA
import pandas as pd
from alpaca.common import RawData
from alpaca.data import BarSet, Bar
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from matplotlib import pyplot as plt
from pandas_ta import percent_return
from sklearn.model_selection import train_test_split
from tuneta.tune_ta import TuneTA
from logging import getLogger
logger = getLogger(__name__)

def download_crypto_data(
        timeframe: TimeFrame = TimeFrame.Minute,
        start: datetime = datetime.now() + timedelta(days=-1),
        symbol_or_symbols=None,
) -> Dict[str, pd.DataFrame]:
    """
    :param timeframe:
    :param start:
    :param symbol_or_symbols:
    :return: key:symbol, value=pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],
    """
    if symbol_or_symbols is None:
        symbol_or_symbols = ["BTC/USD", "ETH/USD"]

    client = CryptoHistoricalDataClient()
    request_params = CryptoBarsRequest(
        symbol_or_symbols=symbol_or_symbols,
        timeframe=timeframe,
        start=start,
        ent=datetime.now(),
    )
    bars = client.get_crypto_bars(request_params)
    return to_ohlcv_df(bars)


# def download_latest_crypto_data():
#     client = Crypto()

def to_ohlcv_df(bars: Union[BarSet, RawData]) -> Dict[str, pd.DataFrame]:
    """
    convert CryptoBars API response to a dict of OHLCV dataframe
    :param bars: response of Alpaca CryptoBars request
    :return: key=symbol, value=pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],
        index: The closing timestamp of the bar.
        open: The opening price of the interval.
        high: The high price during the interval.
        low: The low price during the interval.
        close: The closing price of the interval.
        volume: The volume traded over the interval.
    """
    ret = {}
    col_names = ["timestamp", "open", "high", "low", "close", "volume"]
    for symbol in bars.data:
        data = []
        bars_symbol: List[Bar] = bars.data[symbol]
        for bar in bars_symbol:
            data.append([bar.timestamp, bar.open, bar.high, bar.low, bar.close,
                         bar.volume])

        df: pd.DataFrame = pd.DataFrame(data, columns=col_names)
        df = df.set_index(pd.DatetimeIndex(df["timestamp"]))
        df = df.drop(["timestamp"], axis=1)

        ret[symbol] = df

    return ret


def ffill_index(symbol_bars: Dict[str, pd.DataFrame], timeframe: TimeFrame) -> \
Dict[str, pd.DataFrame]:
    """
    CryptoBars API responses may be missing some time data.
    Fill in the gap data by ffill and return the data
    :param symbol_bars:
    :return: key=symbol, value=pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],
    """
    ret = {}
    for symbol in symbol_bars:
        ret[symbol] = symbol_bars[symbol].resample(timeframe.value).ffill()
    return ret


def train_tuneta(bars:pd.DataFrame, offset:int=-5,test_size:float=0.3):
    """
    train using tuneTA https://github.com/jmrichardson/tuneta

    :param bars: pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],

    :return:
    """

    X = bars
    # e.g. when bars = 1Min OHLCV data and offset=-5,
    # y(index="2022-10-12 01:10:00") value =
    #   the percent of price increase between "2022-10-12 01:10:00" and "2022-10-12 01:15:00"
    y = percent_return(X["close"], offset=offset)
    # ref:
    # https://data-analysis-stats.jp/%E3%83%87%E3%83%BC%E3%82%BF%E5%89%8D%E5%87%A6%E7%90%86/tuneta%E3%81%AE%E8%A7%A3%E8%AA%AC%EF%BC%88%E6%99%82%E7%B3%BB%E5%88%97%EF%BC%9A%E7%9B%AE%E7%9A%84%E3%81%AE%E5%A4%89%E6%95%B0%E3%81%AE%E6%9C%80%E9%81%A9%E5%8C%96%EF%BC%89/

    # the last "offset" rows have "nan" value.
    # drop them from both the training and label data
    X.drop(X.tail(-1*offset).index, inplace=True)  # drop last n rows
    y.drop(y.tail(-1*offset).index, inplace=True)  # drop last n rows

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size,
                                                        shuffle=False)
    tt = TuneTA(n_jobs=6, verbose=True)
    # X: Historical dataset
    # y: Target used to measure correlation.  Can be a subset index of X
    # trials: Number of optimization trials per indicator set
    # indicators: List of indicators to optimize
    # ranges: Parameter search space
    # early_stop: Max number of optimization trials before stopping
    tt.fit(X_train, y_train, indicators=['all'], ranges=[(4, 30)], trials=100, early_stop=10,)
    tt.fit_times()
    tt.report(target_corr=True, features_corr=True)
    tt.prune(max_inter_correlation=.7)
    features = tt.transform(X_train)
    X_train = pd.concat([X_train, features], axis=1)
    print(features)



if __name__ == "__main__":
    # --- config ---
    pd.set_option('display.max_rows', None)
    max_inter_correlation = 0.7
    now = datetime.now()
    start = now + timedelta(days=-1)
    timeframe: TimeFrame = TimeFrame(amount=1, unit=TimeFrameUnit.Minute)
    # --------------

    symbol_bars: Dict[str, pd.DataFrame] = download_crypto_data(
        timeframe=timeframe, start=start)

    symbol_bars = ffill_index(symbol_bars, timeframe)
    for symbol in symbol_bars:
        train_tuneta(symbol_bars[symbol])
        exit()

