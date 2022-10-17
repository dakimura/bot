from datetime import datetime, timedelta, date, time
from logging import getLogger
from typing import List, Union, Dict, Optional

import japanize_matplotlib
import numpy as np
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
from xgboost.sklearn import XGBRegressor

japanize_matplotlib.japanize()

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


def ffill_index(symbol_bars: Dict[str, pd.DataFrame], timeframe_str: str) -> \
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
        ret[symbol] = symbol_bars[symbol].resample(timeframe_str).ffill()
        # drop first 1 row because the first row may have nan value because of the ffill
        ret[symbol].drop(ret[symbol].head(1).index, inplace=True)
    return ret


def close_percent_return_train_test_bars(
        bars: pd.DataFrame, offset: int = -5,
        test_size: float = 0.3
) -> (pd.DataFrame, pd.DataFrame, pd.Series, pd.Series):
    """
    assume that the label is the percent_return of "close" column value of bars,
    split the bars data to X_train, X_test, y_train, y_test
    :param bars: pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],
    :param offset: e.g. when bars = 1Min OHLCV data and offset=-5,
     y(index="2022-10-12 01:10:00") value =
    the percent of "close" price increase between "2022-10-12 01:10:00" and "2022-10-12 01:15:00"
    :param test_size: what percent of data is used for testing, not training.
    must be a number between 0 and 1.0.
    :return: X_train,X_test, y_train, y_test
    """
    X = bars
    # e.g. when bars = 1Min OHLCV data and offset=-5,
    # y(index="2022-10-12 01:10:00") value =
    #   the percent of price increase between "2022-10-12 01:10:00" and "2022-10-12 01:15:00"
    y = percent_return(X["close"], offset=offset)

    # the last "offset" rows have "nan" value because
    # we can't calculate the return for the latest data.
    # drop them from both the training and label data
    X.drop(X.tail(-1 * offset).index, inplace=True)  # drop last n rows
    y.drop(y.tail(-1 * offset).index, inplace=True)  # drop last n rows

    # first test_size*100[%] data are used for training
    X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                        test_size=test_size,
                                                        shuffle=False)
    return X_train, X_test, y_train, y_test


def fit_tuneta(X: pd.DataFrame, y: pd.Series, n_jobs: int = 4,
               indicators=None,
               ranges=None, trials: int = 50, early_stop: int = 10,
               max_inter_correlation: float = 0.7) -> (
        pd.DataFrame, TuneTA):
    """
    select features using tuneTA https://github.com/jmrichardson/tuneta
    :param X: training data. pd.DataFrame[index=['timestamp'](datetime64[ns, UTC]),
    columns=['open'(float64), 'high'(float64), 'low'(float64), 'close'(float64), 'volume'(float64) ],
    :param y: label data for the training data.

    :return: TuneTA object after fitting.
    """
    if ranges is None:
        ranges = [(3, 180)]
    if indicators is None:
        indicators = ['all']

    tt = TuneTA(n_jobs=n_jobs, verbose=True)
    # X: Historical dataset
    # y: Target used to measure correlation.  Can be a subset index of X
    # trials: Number of optimization trials per indicator set
    # indicators: List of indicators to optimize
    # ranges: Parameter search space
    # early_stop: Max number of optimization trials before stopping
    tt.fit(X, y,
           indicators=indicators,
           # indicators=['tta.RSI'],
           ranges=ranges,
           trials=trials,
           early_stop=early_stop,
           )

    tt.prune(max_inter_correlation=max_inter_correlation)
    return tt


def save_model(model: XGBRegressor, save_to_path: str):
    """
    save a trained XGBRegressor model to the specified path
    :param model:
    :param save_to_path:
    :return:
    """
    import pickle
    # import os
    # os.makedirs(save_to_path, exist_ok=True)
    with open(save_to_path, "wb") as f:
        pickle.dump(model, f)


def main():
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", None)
    pd.set_option('display.max_colwidth', None)

    # --- [data] config----
    # symbol_or_symbols = ["BTC/USD", "ETH/USD"]
    symbol_or_symbols = ["BTC/USD"]
    today_beginning: datetime = datetime.combine(date.today(), time())
    start = today_beginning + timedelta(days=-365 * 3)  # use 3-year data
    timeframe: TimeFrame = TimeFrame(amount=15, unit=TimeFrameUnit.Minute)
    timeframe_str: str = "15Min"
    offset = -4  # predict value after n timeframes

    # --- [Tune-TA, feature selection] config---
    # values are just copied from: https://data-analysis-stats.jp/%E3%83%87%E3%83%BC%E3%82%BF%E5%89%8D%E5%87%A6%E7%90%86/tuneta%E3%81%AE%E8%A7%A3%E8%AA%AC%EF%BC%88%E6%99%82%E7%B3%BB%E5%88%97%EF%BC%9A%E7%9B%AE%E7%9A%84%E3%81%AE%E5%A4%89%E6%95%B0%E3%81%AE%E6%9C%80%E9%81%A9%E5%8C%96%EF%BC%89/
    save_model_dir = "./model"
    test_size = 0.3
    search_ranges = [(4, 30)]
    indicators = ['all']
    #indicators = ['tta.RSI']  # to make debugging faster
    n_jobs = 10
    trials = 100
    #trials = 10  # to make debugging faster
    early_stop = 10
    max_inter_correlation = 0.7

    # --- [XGBRegressor, learner] config ---
    # values are just copied from: https://github.com/AlpacaDB/jquants-api-sample/blob/main/20220915_jquantsapi_uki_predictor.ipynb
    max_depth: Optional[int] = 6
    learning_rate: Optional[float] = 0.01
    n_estimators: int = 3000
    n_jobs_xgbr: Optional[int] = -1
    colsample_bytree: Optional[float] = 0.1

    # download crypto data
    symbol_bars: Dict[str, pd.DataFrame] = download_crypto_data(
        timeframe=timeframe, start=start, symbol_or_symbols=symbol_or_symbols)
    logger.info("downloaded crypto data")

    # preprocess
    symbol_bars: Dict[str, pd.DataFrame] = ffill_index(symbol_bars,
                                                       timeframe_str)
    for symbol in symbol_bars:
        logger.info(f"start processing {symbol} data")

        # prepare train data
        X_train, X_test, y_train, y_test = close_percent_return_train_test_bars(
            symbol_bars[symbol], offset, test_size)

        # select features
        tune_ta = fit_tuneta(
            X_train, y_train, n_jobs=n_jobs, indicators=indicators,
            ranges=search_ranges,
            trials=trials, early_stop=early_stop,
            max_inter_correlation=max_inter_correlation,
        )
        # feature values for training
        train_features = tune_ta.transform(X_train)
        logger.info("features are selected.", train_features.columns)

        # train
        model: XGBRegressor = XGBRegressor(max_depth=max_depth,
                                           learning_rate=learning_rate,
                                           n_estimators=n_estimators,
                                           n_jobs=n_jobs_xgbr,
                                           colsample_bytree=colsample_bytree,
                                           random_state=0)
        model.fit(train_features, y_train)
        logger.info(f"training for {symbol} is done")

        # save model
        # when symbol="BTC/USD", then filepath would be "BTC_USD_model.pickle"
        save_model(model,
                   f"{save_model_dir}/{symbol.replace('/', '_')}_model.pickle")

        # predict and draw graphs
        test_features: pd.Series = tune_ta.transform(X_test)
        predict_result: np.ndarray = model.predict(test_features)

        data_for_plot = pd.DataFrame(
            {
                f"[label] return[%] after {offset * -1} * {timeframe_str}": y_test * 100,
                f"[predict] return[%] after {offset * -1} * {timeframe_str}": predict_result * 100,
            })
        data_for_plot[-200:-100].plot(
            title=f"{symbol} return[%] prediction using Tune-TA & XGBRegressor")
        plt.show()


if __name__ == "__main__":
    main()
