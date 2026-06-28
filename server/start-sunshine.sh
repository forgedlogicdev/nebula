#!/bin/bash
# Start headless Sunshine streaming server with software encoding
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2
echo "[sunshine] Xvfb started on :99"
export DISPLAY=:99
sunshine
