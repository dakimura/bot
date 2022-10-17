import os
import logging
from logging import getLogger
import asyncio
from typing import Union, List
import pickle
import schedule

from alpaca.common import RawData
from alpaca.data import CryptoHistoricalDataClient, CryptoLatestQuoteRequest
from alpaca.trading import TradeAccount, Position
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetClass
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestBarRequest, CryptoBarsRequest
import time

from xgboost import XGBRegressor

logger = getLogger(__name__)

# get the latest price data and predict every INTERVAL_SEC second
interval_sec: int = int(os.environ.get('INTERVAL_SEC', '10'))
# Alpaca API config
alpaca_api_key_id: str = os.environ.get('ALPACA_API_KEY_ID')
alpaca_api_secret_key: str = os.environ.get('ALPACA_API_SECRET_KEY')
alpaca_base_url: str = os.environ.get('ALPACA_BASE_URL',
                                      'https://paper-api.alpaca.markets')
# target crypto symbol
# TODO: support multiple symbols
target_symbol: str = os.environ.get("TARGET_SYMBOL", "BTC/USD")
model_pkl_path: str = os.environ.get("MODEL_FILEPATH",
                                     "./train/model/BTC_USD_model.pkl")


class MainRoutine:
    def __init__(self, trading_cli: TradingClient,
                 data_cli: CryptoHistoricalDataClient,
                 target_symbol: str,
                 model: XGBRegressor):
        self.trading_cli: TradingClient = trading_cli
        self.data_cli: CryptoHistoricalDataClient = data_cli
        self.target_symbol: str = target_symbol
        self.model: XGBRegressor = model

    async def run(self):
        """
        main routine
        :return: None
        """
        account: Union[TradeAccount, RawData] = self.trading_cli.get_account()
        logger.info("current cash: %s", account.cash)

        positions: Union[
            List[Position], RawData] = self.trading_cli.get_all_positions()
        logger.info("current positions: %s", positions)

        # get recent bars of a coin.
        latest_bar = self.data_cli.get_crypto_bars(
            CryptoBarsRequest(symbol_or_symbols=target_symbol)
        )
        print(latest_bar)


def load_value(load_from_path: str):
    """
    load a serialized object from the specified path
    :param load_from_path:
    :return:
    """
    f = open(load_from_path, "rb")
    value = pickle.load(f)
    f.close()
    return value


def main():
    # init logger
    logging.basicConfig(
        format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
        level=logging.INFO)
    logger.info("start initializing...")

    trading_client = TradingClient(alpaca_api_key_id, alpaca_api_secret_key,
                                   paper=("paper" in alpaca_base_url),
                                   )

    # keys required for stock historical data client
    data_client = CryptoHistoricalDataClient(
        api_key=alpaca_api_key_id,
        secret_key=alpaca_api_secret_key,
    )
    # load serialized model
    model:XGBRegressor = load_value(model_pkl_path)

    main_routine = MainRoutine(trading_cli=trading_client, data_cli=data_client,
                               target_symbol=target_symbol, model=model)
    logger.info("initialization done. bot started...")

    # main loop
    while True:
        asyncio.run(main_routine.run())
        time.sleep(interval_sec)


if __name__ == "__main__":
    main()
