#!/usr/bin/bash
xinput set-prop 7 "Coordinate Transformation Matrix" 0 -1 1 1 0 0 0 0 1
cd /home/admin/raspberry_app/
python3 main.py