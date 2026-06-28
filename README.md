# Nebula — Controller-First Android Launcher & Game Hub

A custom Android launcher designed for controller navigation, cross-device game streaming, and a broken-grid modular home screen. Built for the **Huawei MediaPad 3** (AGS-L03) with a **Switch Pro Controller** bridged through an **HP Mini** headless server.

## Architecture

```
   Switch Controller                MediaPad 3 (Android 8)
        USB │                              │
            ▼                              │
   ┌─────────────────┐                     │
   │   HP MINI        │    ADB keyevents   │
   │  (Ubuntu 24.04)  │────────────────────┤
   │                  │                    │
   │  forwarder.py ───┤                    ▼
   │  sunshine ───────┤            ┌──────────────┐
   │  retroarch/games │            │ NEBULA       │
   └──────────────────┘            │ LAUNCHER     │
          │                        │              │
          │ Moonlight stream       │ 4 panels:    │
          ▼                        │ Code Games   │
   [any Moonlight client]          │ Home Music   │
                                   │ Dock + glyphs│
                                   └──────────────┘
```

## Components

### `launcher/` — Android Launcher APK

A minimal, zero-dependency Android launcher targeting API 26 (Android 8.0).

- **4 swipable panels**: Code, Games, Home (app grid), Music
- **Controller-first**: D-pad to navigate, A to launch, L/R bumpers to switch panels
- **Dock**: Messages / Termux / Spotify / Browser
- **Game hub panel**: Launch Moonlight, quick access to the Sunshine web UI
- **dispatchKeyEvent** handles all key sources (keyboard, gamepad, ADB-injected)
- No Kotlin, no Material, no RecyclerView — pure lightweight Java

Build:
```bash
cd launcher
./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

### `forwarder/` — Switch Controller → ADM Bridge

Reads raw evdev events from a connected Switch Pro Controller and forwards them as Android keyevents over ADB.

- Zero analog stick → dpad mapping (sticks ignored entirely)
- HAT/D-pad → dpad keyevents
- Face buttons → A/B/X/Y keyevents (with Toast feedback)
- Bumpers/triggers → panel switching
- Auto-reconnects if controller is unplugged

```bash
# On the HP Mini (with controller plugged in and tablet connected via USB ADB):
sudo setfacl -m u:$USER:r /dev/input/event11  # once
nohup python3 -u forwarder/gamepad-forwarder.py > /tmp/forwarder.log 2>&1 &
```

### `server/` — Sunshine Game Streaming

Headless game streaming server on Intel HD Graphics 630 with VA-API hardware encoding.

- **Xvfb** virtual display (1920x1080)
- **Sunshine** streaming server
- Clients connect via **Moonlight** (Android, iOS, PC, etc.)

```bash
server/start-sunshine.sh
```

## Hardware

| Device | Role | Specs |
|---|---|---|
| **HP Mini** | Server | i5-7500T, 11GB RAM, Intel HD 630, Ubuntu 24.04 |
| **MediaPad 3** | Client | AGS-L03, Android 8.0, 800x1280, ARM Cortex-A53 |
| **Switch Controller** | Input | Core (Plus) Wired Controller via USB |

## Button Mapping

| Controller | Launcher Action |
|---|---|
| A | Launch selected app |
| B | Home panel |
| X | Launch Termux |
| Y | Music panel |
| L | Games panel |
| R | Music panel |
| ZL | Expand notifications |
| D-pad | Navigate app grid / switch panels |
| Plus | Home panel |

## Customization

The launcher is designed for creative extension:
- **Broken-grid layout**: Widgets can overlap, rotate, bleed past borders
- **Glyph app shortcuts**: Floating line-art icons with beat-reactive pulses
- **Alien widget**: A transparent head-bobbing creature that reacts to music
- **Music visualizer panel**: EQ bars, waveform rings, BPM counter

## License

MIT

## Headless Sunshine Auto-Pairing

Since the HP Mini has no display or keyboard, `server/sunshine-auto-pair.sh` watches for Moonlight pairing requests and auto-accepts them. No need to touch the web UI.

```bash
server/sunshine-auto-pair.sh &
```

## Quick Start

```bash
# Terminal 1: Game streaming server
server/start-sunshine.sh &

# Terminal 2: Auto-pair daemon  
server/sunshine-auto-pair.sh &

# Terminal 3: Controller forwarder
server/start-forwarder.sh &

# On the tablet: install the launcher
cd launcher && ./gradlew assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk

# Open Moonlight, tap the HP Mini, pair (auto-accepted), stream.
```
