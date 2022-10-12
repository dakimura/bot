#!/usr/bin/env bash

sudo apt install pip
pip install -r requirements.txt
pgrep streamlit | sudo xargs kill
pgrep bot | sudo xargs kill
sudo nohup streamlit run --server.port=80 src/dashboard.py >>dashboard.log 2>&1 &
sudo nohup python src/bot.py >>bot.log 2>&1 &
