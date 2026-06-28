#!/bin/bash
# Start headless Sunshine streaming server
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
export DISPLAY=:99
sunshine
