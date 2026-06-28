#!/bin/bash
# Start the gamepad -> Android ADB forwarder
export PATH=$HOME/Android/platform-tools:$PATH
python3 -u "$(dirname "$0")/../forwarder/gamepad-forwarder.py"
