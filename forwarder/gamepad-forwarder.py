#!/usr/bin/env python3
import struct, fcntl, os, subprocess, time, glob, sys

KEY_MAP = {
    0x130: 96,  0x131: 97,  0x132: 99,  0x133: 100,
    0x134: 96,  0x135: 97,  0x136: 102, 0x137: 103,
    0x138: 104, 0x139: 105, 0x13a: 109, 0x13b: 108,
    0x13c: 108, 0x13d: 106, 0x13e: 107,
    0x220: 19,  0x221: 20,  0x222: 21,  0x223: 22,
    # Hat/D-pad as ABS
    0x10: None, 0x11: None,
}

EVIOCGNAME = 0x82004506
ES = struct.calcsize("llHHi")
EV_KEY, EV_SYN = 0x01, 0x00

def find_gamepad():
    for ev in sorted(glob.glob("/dev/input/event*")):
        try:
            fd = os.open(ev, os.O_RDONLY)
            buf = bytearray(256)
            fcntl.ioctl(fd, EVIOCGNAME, buf)
            name = buf.decode(errors="ignore").rstrip("\0").lower()
            keywords = ["core", "gamepad", "joystick", "nintendo",
                       "switch", "xbox", "hid", "wired", "controller"]
            if any(k in name for k in keywords):
                return ev, name, fd
            os.close(fd)
        except:
            pass
    return None, None, None

def adb_key(keycode, action):
    a = "down" if action else "up"
    subprocess.run(
        ["/usr/bin/adb", "shell", "input", "keyevent", a, str(keycode)],
        capture_output=True, timeout=2
    )

print("SCANNING...", flush=True)
path, name, fd = find_gamepad()
while fd is None:
    time.sleep(2)
    path, name, fd = find_gamepad()
print("CONTROLLER: " + name, flush=True)

while True:
    try:
        raw = os.read(fd, ES * 4)
        for i in range(0, len(raw), ES):
            sec, usec, etype, code, value = struct.unpack("llHHi", raw[i:i+ES])
            if etype == EV_KEY and code in KEY_MAP:
                kc = KEY_MAP[code]
                adb_key(kc, value != 0)
                direction = "DOWN" if value else "UP"
                info = "code=0x{:03x} -> {} {}".format(code, kc, direction)
                print(info, flush=True)
    except OSError:
        time.sleep(0.01)
    except Exception as e:
        print("ERR: " + str(e), flush=True)
        if fd:
            os.close(fd)
        path, name, fd = find_gamepad()
        while fd is None:
            time.sleep(2)
            path, name, fd = find_gamepad()
        print("RECONNECTED: " + name, flush=True)
