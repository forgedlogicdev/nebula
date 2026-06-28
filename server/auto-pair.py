#!/usr/bin/env python3
"""Auto-accept Sunshine pairing PINs via -0 stdin/stdout."""

import subprocess
import sys
import os
import re
import time

def main():
    print("[auto-pair] Starting Sunshine with auto-pin mode...", flush=True)
    
    # Start Sunshine with -0 flag
    proc = subprocess.Popen(
        ["sunshine", "-0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
        env={**os.environ, "DISPLAY": ":99"}
    )
    
    print("[auto-pair] Sunshine PID: " + str(proc.pid), flush=True)
    print("[auto-pair] Waiting for pairing requests...", flush=True)
    
    # Read stdout line by line, looking for a 4-digit PIN
    for line in proc.stdout:
        line = line.strip()
        if not line:
            continue
        
        # PIN is a 4-digit number on its own line
        match = re.match(r'^(\d{4})$', line)
        if match:
            pin = match.group(1)
            print(f"[auto-pair] PIN detected: {pin}", flush=True)
            
            # Write PIN back to stdin to confirm
            proc.stdin.write(pin + "\n")
            proc.stdin.flush()
            print(f"[auto-pair] Auto-accepted PIN: {pin}", flush=True)
            print("[auto-pair] Pairing complete!", flush=True)
            continue
        
        # Log non-PIN lines to stderr for debugging
        if any(kw in line.lower() for kw in ["error", "fatal", "warning"]):
            print(f"[sunshine] {line}", file=sys.stderr, flush=True)

    print("[auto-pair] Sunshine exited", flush=True)

if __name__ == "__main__":
    main()
