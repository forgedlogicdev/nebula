#!/usr/bin/env python3
"""Forward Switch controller events to Xvfb display via xdotool / uinput.
Reads /dev/input/event11 and injects keyboard/mouse events to DISPLAY=:99."""

import struct, os, subprocess, time, glob

DEV = "/dev/input/event11"
DISPLAY = ":99"

# Map evdev buttons to xdotool keys
KEY_MAP = {
    # Face buttons -> keyboard keys that RetroArch uses
    0x130: "z",     # A -> z (RetroArch default A)
    0x131: "x",     # B -> x (RetroArch default B)
    0x132: "a",     # C -> a
    0x133: "s",     # X -> s (RetroArch default X)
    0x134: "d",     # Y -> d
    0x135: "c",     # extra
    # D-pad -> arrow keys
    0x220: "Up",
    0x221: "Down",
    0x222: "Left",
    0x223: "Right",
    # Bumpers/triggers
    0x136: "q",     # L
    0x137: "w",     # R
    0x138: "e",     # ZL
    0x139: "r",     # ZR
    # Start/Select
    0x13a: "Return",  # Select
    0x13b: "Escape",  # Start
}

# Hat/ABS D-pad
HAT_MAP = {
    (-1, 0): "Left",
    (1, 0): "Right",
    (0, -1): "Up",
    (0, 1): "Down",
}

EVENT_SIZE = struct.calcsize("llHHi")
EV_KEY, EV_ABS, EV_SYN = 0x01, 0x03, 0x00
AXIS_HAT_X, AXIS_HAT_Y = 16, 17

env = {**os.environ, "DISPLAY": DISPLAY}

def xdotool(action, key):
    """Simulate key press or release on the Xvfb display."""
    args = ["xdotool", "key" if action == "key" else action, key]
    subprocess.run(args, env=env, capture_output=True, timeout=0.5)

def main():
    if not os.path.exists(DEV):
        print(f"Controller not found at {DEV}")
        return

    fd = os.open(DEV, os.O_RDONLY)
    print(f"Forwarding {DEV} -> Xvfb {DISPLAY}")

    pressed = set()
    last_hat = (0, 0)
    last_hat_time = 0

    while True:
        try:
            data = os.read(fd, EVENT_SIZE * 4)
            for i in range(0, len(data), EVENT_SIZE):
                sec, usec, etype, code, value = struct.unpack("llHHi", data[i:i+EVENT_SIZE])

                if etype == EV_KEY:
                    if code in KEY_MAP:
                        key = KEY_MAP[code]
                        if value == 1 and code not in pressed:
                            xdotool("keydown", key)
                            pressed.add(code)
                        elif value == 0 and code in pressed:
                            xdotool("keyup", key)
                            pressed.discard(code)

                elif etype == EV_ABS:
                    now = time.time()
                    if code == AXIS_HAT_X:
                        # Only process when hat actually changes from center
                        new_x = 1 if value > 0 else (-1 if value < 0 else 0)
                        if new_x != last_hat[0] and now - last_hat_time > 0.1:
                            # Release old direction
                            if last_hat[0] < 0: xdotool("keyup", "Left")
                            elif last_hat[0] > 0: xdotool("keyup", "Right")
                            # Press new direction
                            if new_x < 0: xdotool("keydown", "Left")
                            elif new_x > 0: xdotool("keydown", "Right")
                            last_hat = (new_x, last_hat[1])
                            last_hat_time = now
                    elif code == AXIS_HAT_Y:
                        new_y = 1 if value > 0 else (-1 if value < 0 else 0)
                        if new_y != last_hat[1] and now - last_hat_time > 0.1:
                            if last_hat[1] < 0: xdotool("keyup", "Up")
                            elif last_hat[1] > 0: xdotool("keyup", "Down")
                            if new_y < 0: xdotool("keydown", "Up")
                            elif new_y > 0: xdotool("keydown", "Down")
                            last_hat = (last_hat[0], new_y)
                            last_hat_time = now

        except OSError:
            time.sleep(0.01)
        except Exception as e:
            print(f"ERR: {e}")

if __name__ == "__main__":
    main()
