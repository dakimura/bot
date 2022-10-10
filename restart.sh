#!/usr/bin/env bash

sudo apt install pip
pip install -r requirements.txt
PID=$(ps -ef | grep "streamlit" | grep -v grep | awk '{print $2}')
if [ -n "$PID" ]; then
  sudo kill "$PID"
fi
sudo nohup streamlit run --server.port=80 src/bot.py >> bot.log 2>&1 &