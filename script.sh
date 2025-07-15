#!/usr/bin/bash
xinput set-prop 6 "Coordinate Transformation Matrix" 0 1 0 -1 0 1 0 0 1
cd /root/raspberry_app/
python3 main.py
