#!/usr/bin/bash

python humidity.py &
flask --app web_server/web_server run --host=0.0.0.0
