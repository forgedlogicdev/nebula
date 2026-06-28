#!/usr/bin/env python3
"""Auto-accept Sunshine PIN. Only matches solo 4-digit lines (not timestamps)."""

import subprocess, os, sys, re, time, select

print("[auto-pair] Starting Sunshine -0...", flush=True)

proc = subprocess.Popen(
    ["sunshine", "-0"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=0,
    env={**os.environ, "DISPLAY": ":99"}
)

print(f"[auto-pair] PID={proc.pid}, waiting for pairing...", flush=True)

buf = ""

while True:
    r, _, _ = select.select([proc.stdout], [], [], 2.0)
    if r:
        try:
            chunk = proc.stdout.read(1)
            if not chunk:
                break
            buf += chunk
            while "\n" in buf:
                line, buf = buf.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                # Only match a line that is EXACTLY a 4-digit PIN (nothing else)
                m = re.match(r'^(\d{4})$', line)
                if m:
                    pin = m.group(1)
                    t0 = time.time()
                    print(f"[PIN] {pin} - auto-accepting...", flush=True)
                    proc.stdin.write(pin + "\n")
                    proc.stdin.flush()
                    elapsed = time.time() - t0
                    print(f"[DONE] Pairing accepted in {elapsed:.2f}s!", flush=True)
        except:
            break
    if proc.poll() is not None:
        print(f"[auto-pair] Sunshine exited (code={proc.returncode})", flush=True)
        break

print("[auto-pair] Stopped", flush=True)
