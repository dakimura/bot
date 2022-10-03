import asyncio
import datetime

import schedule
import streamlit as st
import random

TRADE_DATA = []


async def main():
    # entry exit job
    def entry_job():
        TRADE_DATA.append([datetime.datetime.now(), random.random()])

    def exit_job():
        for i in range(len(TRADE_DATA)):
            if TRADE_DATA[i][1] == 0:
                TRADE_DATA[i][1] = 1

    # schedule
    schedule.every(5).seconds.do(entry_job)
    schedule.every(15).seconds.do(exit_job)

    # ui
    st.markdown("# Trade")
    element1 = st.empty()

    # data update
    while True:
        schedule.run_pending()
        element1.dataframe(TRADE_DATA)


if __name__ == "__main__":
    asyncio.run(main())
