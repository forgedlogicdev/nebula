#!/bin/bash
# Nebula Server Restart — kills old processes and restarts all services
set -e

echo "=== Stopping old services ==="
kill $(pgrep sunshine) 2>/dev/null || true
kill $(pgrep -f nebula-hub) 2>/dev/null || true
kill $(pgrep -f xvfb-forwarder) 2>/dev/null || true
sleep 1

echo "=== Starting Xvfb ==="
export DISPLAY=:99
pgrep Xvfb >/dev/null || Xvfb :99 -screen 0 1920x1080x24 &
sleep 1
pgrep openbox >/dev/null || openbox --replace &
sleep 1

echo "=== Starting Sunshine ==="
nohup sunshine > /tmp/sunshine.log 2>&1 &
sleep 3

echo "=== Starting Controller Forwarder ==="
nohup python3 /home/gnor/nebula/server/xvfb-forwarder.py > /tmp/xvfb-forwarder.log 2>&1 &

echo "=== Starting Game Hub ==="
nohup python3 /home/gnor/nebula/server/nebula-hub.py > /tmp/hub.log 2>&1 &

sleep 2
echo "=== Status ==="
ss -tlnp | grep -E "47984|47989|8080" || echo "PORTS NOT UP"
pgrep -x sunshine && echo "sunshine: OK" || echo "sunshine: DOWN"
pgrep -f nebula-hub && echo "nebula-hub: OK" || echo "nebula-hub: DOWN"
pgrep -f xvfb-forwarder && echo "xvfb-forwarder: OK" || echo "xvfb-forwarder: DOWN"
