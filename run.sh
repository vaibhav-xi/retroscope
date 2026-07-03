#!/bin/bash

export DISPLAY=:1
export XAUTHORITY=/home/zero/.Xauthority

source ~/retroscope/venv/bin/activate

python3 ~/retroscope/main.py
