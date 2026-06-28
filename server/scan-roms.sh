#!/bin/bash
# Auto-detect ROMs in ~/ROMs/ and add them to Sunshine apps
ROMS="$HOME/ROMs"
APPS="$HOME/.config/sunshine/apps.json"
CORES="/usr/lib/x86_64-linux-gnu/libretro"

declare -A SYSTEM_CORES=(
  ["nes"]="nestopia_libretro.so"
  ["snes"]="snes9x_libretro.so"
  ["genesis"]="genesis_plus_gx_libretro.so"
  ["gba"]="mgba_libretro.so"
  ["gb"]="gambatte_libretro.so"
  ["psx"]="mednafen_psx_libretro.so"
)

# Read existing apps, keep non-ROM entries
python3 << 'PYEOF'
import json, os, glob

APPS = os.path.expanduser("~/.config/sunshine/apps.json")
ROMS = os.path.expanduser("~/ROMs")
CORES = "/usr/lib/x86_64-linux-gnu/libretro"

SYSTEM_CORES = {
    "nes": "nestopia_libretro.so",
    "snes": "snes9x_libretro.so",
    "genesis": "genesis_plus_gx_libretro.so",
    "gba": "mgba_libretro.so",
    "gb": "gambatte_libretro.so",
    "psx": "mednafen_psx_libretro.so",
}

with open(APPS) as f:
    data = json.load(f)

# Keep base apps (non-ROM, non-RetroArch)
base = [a for a in data["apps"] if "retroarch -L" not in a.get("cmd","")]
new_apps = []

# Add ROMs
for system, core in SYSTEM_CORES.items():
    dir_path = os.path.join(ROMS, system)
    if not os.path.isdir(dir_path):
        continue
    for rom in sorted(os.listdir(dir_path)):
        full = os.path.join(dir_path, rom)
        if not os.path.isfile(full):
            continue
        name = os.path.splitext(rom)[0].replace("_", " ").strip()
        core_path = os.path.join(CORES, core)
        if not os.path.exists(core_path):
            continue
        cmd = 'retroarch -L "{}" "{}"'.format(core_path, full)
        new_apps.append({"name": "[{}] {}".format(system.upper(), name), "cmd": cmd})
        print("  Added: [{}] {}".format(system.upper(), name))

data["apps"] = base + new_apps
with open(APPS, "w") as f:
    json.dump(data, f, indent=2)

print("Done! Total apps: {}".format(len(data["apps"])))
PYEOF

# Restart Sunshine
systemctl --user restart nebula-sunshine 2>/dev/null
echo "Sunshine restarted"
