#!/usr/bin/bash
xinput set-prop 9 "Coordinate Transformation Matrix" 0 -1 1 1 0 0 0 0 1
cd raspberry_app/
python3 main.py