import asyncio
import datetime

import schedule
import streamlit as st
import random
from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame

TRADE_DATA = []

APCA_API_BASE_URL="https://paper-api.alpaca.markets"
API_KEY_ID="***"
API_SECRET_KEY="***"

async def main():
    # entry exit job
    def entry_job():
        # https://alpaca.markets/docs/trading/paper-trading/
        TRADE_DATA.append([datetime.datetime.now(), random.random()])

    def exit_job():
        for i in range(len(TRADE_DATA)):
            if TRADE_DATA[i][1] == 0:
                TRADE_DATA[i][1] = 1

    # schedule
    schedule.every(5).seconds.do(entry_job)
    schedule.every(15).seconds.do(exit_job)

    # ui
    st.markdown("# Trade (deploy test)")
    element1 = st.empty()

    # data update
    while True:
        schedule.run_pending()
        element1.dataframe(TRADE_DATA)


if __name__ == "__main__":
    asyncio.run(main())
    # client = CryptoHistoricalDataClient()
    #
    # request_params = CryptoBarsRequest(
    #     symbol_or_symbols="BTC/USD",
    #     timeframe=TimeFrame.Day,
    #     start=datetime.datetime(year=2022, month=9, day=1)
    # )
    #
    # bars = client.get_crypto_bars(request_params)
    # print(bars)

