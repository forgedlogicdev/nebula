#!/bin/bash
# One-time pairing helper for headless Sunshine
# After running this, open Moonlight on the tablet
# When the PIN appears, submit it here

SUNSHINE_URL="https://localhost:47990"
echo "=== NEBULA AUTO-PAIR ==="
echo "1. Open Moonlight on your tablet"
echo "2. Tap the HP Mini (10.0.0.108)"
echo "3. A PIN will appear on the tablet"
echo "4. Paste PIN below:"
read -p "PIN: " pin
echo "Submitting PIN to Sunshine..."
echo "Open this URL on any device: ${SUNSHINE_URL}/pin?pin=${pin}"
echo "Or from terminal: curl -sk -u nebula:nebula123 -X POST ${SUNSHINE_URL}/api/pin -d {"pin":"${pin}"}"
