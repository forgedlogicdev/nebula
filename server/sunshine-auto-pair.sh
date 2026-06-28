#!/bin/bash
# Auto-accept Moonlight pairing requests for headless Sunshine
# Polls Sunshine API every 3 seconds and auto-accepts any pending PIN

SUNSHINE_URL="https://localhost:47990"
USERNAME="nebula"
PASSWORD="nebula123"

echo "[auto-pair] Starting..." 

# Wait for Sunshine to be ready
while ! curl -sk "$SUNSHINE_URL" >/dev/null 2>&1; do
    sleep 2
done
echo "[auto-pair] Sunshine is up"

# Login and get session
login() {
    curl -sk -c /tmp/sunshine_cookies -X POST "$SUNSHINE_URL/api/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}" >/dev/null 2>&1
}

login

while true; do
    # Check for pending pair requests
    RESP=$(curl -sk -b /tmp/sunshine_cookies "$SUNSHINE_URL/api/pending" 2>/dev/null)
    
    if echo "$RESP" | grep -q pin; then
        PIN=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get(pin,))" 2>/dev/null)
        if [ -n "$PIN" ]; then
            echo "[auto-pair] Accepting pin: $PIN"
            curl -sk -b /tmp/sunshine_cookies -X POST "$SUNSHINE_URL/api/pin" \
                -H "Content-Type: application/json" \
                -d "{\"pin\":\"$PIN\"}" >/dev/null 2>&1
            echo "[auto-pair] Pairing accepted!"
        fi
    fi
    sleep 3
done
