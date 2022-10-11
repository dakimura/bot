#!/usr/bin/env bash

sudo apt install pip
pip install -r requirements.txt
ps -ef | grep "streamlit" | grep -v grep | awk '{print $2}' | xargs kill
sudo nohup streamlit run --server.port=80 src/bot.py >> bot.log 2>&1 &