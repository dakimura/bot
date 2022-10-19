import logging
import os
import time
from datetime import datetime, timedelta
from logging import getLogger
from typing import Union, List

import schedule
from alpaca.common import RawData
from alpaca.data import TimeFrame
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.trading import TradeAccount, Position
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import MarketOrderRequest

logger = getLogger(__name__)

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
# quantity of the target coin for one order
trade_quantity: float = float(os.environ.get("TRADE_QUANTITY", "0.01"))


class Main:
    def __init__(self, trading_cli: TradingClient,
                 data_cli: CryptoHistoricalDataClient,
                 target_symbol: str):
        self.trading_cli: TradingClient = trading_cli
        self.data_cli: CryptoHistoricalDataClient = data_cli
        self.target_symbol: str = target_symbol

    def run(self):
        """
        main logic.
        Cryptocurrencies are traded on the assumption that
        there is an inverse correlation between the upcoming price movement of
        the and the price movement of 24 hours ago.
        (ref: https://note.com/hht/n/nea09d366be7c )
        :return: None
        """
        account: Union[TradeAccount, RawData] = self.trading_cli.get_account()
        logger.info("cash: %s", account.cash)

        positions: Union[
            List[Position], RawData] = self.trading_cli.get_all_positions()
        logger.info("positions: %s", positions)

        # get 1H bars of 24h ago
        now = datetime.utcnow()
        logger.info("utc_now={}".format(now))
        bar_24h_ago = self.data_cli.get_crypto_bars(
            CryptoBarsRequest(
                symbol_or_symbols=target_symbol,
                timeframe=TimeFrame.Hour,
                start=now + timedelta(hours=-24),
                end=now + timedelta(hours=-23),
            )
        )[target_symbol][0]
        logger.info("1H bar of 24hour ago: {}".format(bar_24h_ago))
        if bar_24h_ago.open > bar_24h_ago.close:
            try:
                logger.info("buy because the price decreased 24h ago")
                self.buy()
            except Exception as e:
                logger.info(e)
        if bar_24h_ago.open < bar_24h_ago.close:
            try:
                logger.info("sell because the price increased 24h ago")
                self.sell()
            except Exception as e:
                # sell fails if there is not enough position for the account, but just ignore it
                logger.info(e)
                pass

    def buy(self):
        """
        buy at market if there is enough cash in the account
        :return:
        """
        market_order_data = MarketOrderRequest(
            symbol=target_symbol,
            qty=trade_quantity,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.GTC
        )

        market_order = self.trading_cli.submit_order(
            order_data=market_order_data
        )
        logger.info("submitted a market order: {}".format(market_order))

    def sell(self):
        """
        sell(=liquidate) at market if there are enough positions
        :return:
        """
        # preparing orders
        market_order_data = MarketOrderRequest(
            symbol=target_symbol,
            qty=trade_quantity,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.GTC
        )

        # Market order
        market_order = self.trading_cli.submit_order(
            order_data=market_order_data
        )
        logger.info("submitted a market order: {}".format(market_order))


def main():
    # init logger
    logging.basicConfig(
        format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
        level=logging.INFO)

    trading_client = TradingClient(alpaca_api_key_id, alpaca_api_secret_key,
                                   paper=("paper" in alpaca_base_url),
                                   )

    data_client = CryptoHistoricalDataClient(
        api_key=alpaca_api_key_id,
        secret_key=alpaca_api_secret_key,
    )

    main = Main(trading_cli=trading_client, data_cli=data_client,
                target_symbol=target_symbol)
    logger.info("start: initialization done. Running the main routine...")

    schedule.every().hour.at(":00").do(main.run)

    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
