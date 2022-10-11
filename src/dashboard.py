import asyncio
import datetime
import random

import schedule
import streamlit as st

TRADE_DATA = []

APCA_API_BASE_URL = "https://paper-api.alpaca.markets"
API_KEY_ID = "***"
API_SECRET_KEY = "***"


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
