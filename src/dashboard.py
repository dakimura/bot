import asyncio
import json
import logging
from typing import Dict

import streamlit as st

logger = logging.getLogger(__name__)


async def main():
    @st.cache(ttl=30)  # sec
    def load_data(filepath: str) -> Dict:
        try:
            with open(filepath, "r") as f:
                data = f.readline()
                return json.loads(data)
        except FileNotFoundError as e:
            logger.error("status json file not found", e)
            return {"equity":0, "order_history":[]}

    # entry exit job
    def entry_job():
        pass
        # https://alpaca.markets/docs/trading/paper-trading/
        # .append([datetime.datetime.now(), random.random()])

    # schedule
    # schedule.every(5).seconds.do(entry_job)

    # ui
    st.title('Bot Dashboard')
    st.markdown("# Equity")
    status = load_data(filepath="./src/status.json")

    col1, col2 = st.columns(2)
    col1.metric("Equity", status["equity"], "+0")
    col2.metric("Buying Power", "$199997.28", "+$0.89")

    st.markdown("# Order History")
    st.table(status["order_history"])

    # data update
    # while True:
    #   schedule.run_pending()
    #   equity_elem.dataframe(TRADE_DATA)


if __name__ == "__main__":
    # init logger
    logging.basicConfig(
        format='[%(asctime)s - %(name)s - %(levelname)s] %(message)s',
        level=logging.INFO)
    asyncio.run(main())
