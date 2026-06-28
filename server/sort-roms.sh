#!/usr/bin/env python3
"""ROM Auto-Sorter — drops files into correct ~/ROMs/<system>/ by extension.
Then runs the scanner to update Sunshine apps."""

import os, shutil, sys

HOME = os.path.expanduser("~")
ROMS = os.path.join(HOME, "ROMs")
INCOMING = os.path.join(ROMS, "incoming")

EXT_MAP = {
    # Nintendo
    ".nes": "nes",
    ".fds": "nes",
    ".smc": "snes", ".sfc": "snes",
    ".n64": "n64", ".z64": "n64", ".v64": "n64",
    ".gb": "gb", ".gbc": "gb",
    ".gba": "gba",
    ".nds": "nds",
    # Sega
    ".bin": "genesis", ".md": "genesis", ".gen": "genesis", ".sms": "genesis",
    ".gg": "genesis", ".sg": "genesis",
    ".32x": "genesis",
    # Sony
    ".iso": "psx", ".cue": "psx", ".img": "psx", ".pbp": "psx",
    ".chd": "psx",
    # NEC
    ".pce": "pce",
    # Other
    ".vb": "vb",
    ".ws": "wswan", ".wsc": "wswan",
}

moved = 0
errors = []

for system in EXT_MAP.values():
    os.makedirs(os.path.join(ROMS, system), exist_ok=True)
os.makedirs(INCOMING, exist_ok=True)

for root, dirs, files in os.walk(INCOMING):
    for fname in sorted(files):
        src = os.path.join(root, fname)
        ext = os.path.splitext(fname)[1].lower()
        
        if ext not in EXT_MAP:
            # Maybe a multi-disc game or .bin without .cue — skip for manual
            if ext == ".bin" and any(x.endswith(".cue") for x in files):
                continue  # skip .bin if .cue exists (PS1)
            errors.append(f"{fname} (unknown ext)")
            continue
        
        system = EXT_MAP[ext]
        dst = os.path.join(ROMS, system, fname)
        
        # Don't overwrite existing
        if os.path.exists(dst):
            errors.append(f"{fname} (already exists in {system})")
            continue
        
        shutil.move(src, dst)
        print(f"  [{system.upper()}] {fname}")
        moved += 1

if errors:
    print(f"\nSkipped {len(errors)} files:")
    for e in errors:
        print(f"  - {e}")

print(f"\nSorted {moved} ROMs into ~/ROMs/")

if moved > 0:
    print("Running scanner to update Sunshine...")
    scanner = os.path.join(HOME, "nebula", "server", "scan-roms.sh")
    if os.path.exists(scanner):
        os.system("bash " + scanner)
