#!/usr/bin/env bash

ALPACA_API_KEY_ID=$1
ALPACA_API_SECRET_KEY=$2

sudo apt install pip3
pip3 install -r requirements.txt
pgrep streamlit | sudo xargs kill
pgrep bot | sudo xargs kill
sudo nohup streamlit run --server.port=80 src/dashboard.py >>dashboard.log 2>&1 &
ALPACA_API_KEY_ID=$ALPACA_API_KEY_ID ALPACA_API_SECRET_KEY=$ALPACA_API_SECRET_KEY nohup python3 src/bot.py >>bot.log 2>&1 &
