#!/usr/bin/env python3
"""One coordinated read-only Linux probe; only whitelisted keys/rfkill are emitted.

Development-only, not a startup script. Linux v6.12 input-event-codes.h constants.
No key injection, input grabs, radio writes, shell commands or persistent service.
"""
import argparse
import json
import os
from pathlib import Path
import re
import select
import struct
import time

KEYS = {87: "KEY_F11", 238: "KEY_WLAN", 247: "KEY_RFKILL",
        464: "KEY_FN", 476: "KEY_FN_F11"}
INPUT = struct.Struct("@llHHi")
RFKILL = struct.Struct("=IBBBB")


def selected_key(event_type, code, value):
    if event_type == 1 and code in KEYS:
        return {"kind": "key", "key": KEYS[code], "code": code, "value": value}
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="/dev/input/event0")
    parser.add_argument("--seconds", type=float, default=45)
    args = parser.parse_args()
    if not 0 < args.seconds <= 45:
        parser.error("duration must be >0 and <=45 seconds")
    if not re.fullmatch(r"/dev/input/event[0-9]+", args.device):
        parser.error("expected an explicit /dev/input/eventN")
    name = (Path("/sys/class/input") / Path(args.device).name / "device/name").read_text().strip()
    if name != "AT Translated Set 2 keyboard":
        parser.error("refusing to inspect a device other than the verified integrated keyboard")
    start = time.monotonic()

    def emit(row):
        print(json.dumps(dict(t=round(time.monotonic() - start, 3), **row)), flush=True)

    descriptors = {}
    try:
        for path, kind in ((args.device, "input"), ("/dev/rfkill", "rfkill")):
            descriptors[os.open(path, os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)] = kind
        emit({"kind": "ready", "duration": args.seconds, "keyboard": name,
              "allowed_keys": list(KEYS.values())})
        deadline = time.monotonic() + args.seconds
        while (remaining := deadline - time.monotonic()) > 0:
            ready, _, _ = select.select(list(descriptors), [], [], remaining)
            for fd in ready:
                layout = INPUT if descriptors[fd] == "input" else RFKILL
                data = os.read(fd, layout.size * 64)
                if not data or len(data) % layout.size:
                    raise RuntimeError("incomplete device event stream")
                for event in layout.iter_unpack(data):
                    if descriptors[fd] == "input":
                        row = selected_key(*event[2:])
                        if row is not None:
                            emit(row)
                    else:
                        idx, kind, operation, soft, hard = event
                        if kind == 1:  # WLAN only; no SSID, MAC or network payload.
                            emit({"kind": "rfkill", "idx": idx, "op": operation,
                                  "soft": soft, "hard": hard})
        emit({"kind": "finished"})
    finally:
        for fd in descriptors:
            os.close(fd)


if __name__ == "__main__":
    main()
