#!/usr/bin/python3
"""Sample BlueZ on the existing bar tick; reuse a pinned HID battery reader."""
import ctypes as C
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

BATTERY_INTERVAL = 300
BATTERY_MAX_AGE = 600
WORKER_TIMEOUT = 15


def find_trackpad(root=Path("/sys/class/hidraw")):
    """Match the native driver and Bluetooth hardware ID, never a personal name."""
    for entry in sorted(root.glob("hidraw*")):
        try:
            props = dict(line.split("=", 1) for line in
                         (entry / "device/uevent").read_text().splitlines() if "=" in line)
            identity = tuple(int(part, 16) for part in props.get("HID_ID", "").split(":"))
            if props.get("DRIVER") == "magicmouse" and identity == (5, 0x004C, 0x0265):
                return entry.name, str((entry / "device").resolve())
        except (OSError, ValueError):
            continue
    return None


class BlueZ:
    def __init__(self, root=Path("/sys/class/bluetooth")):
        self.root, self.library, self.bus = root, None, C.c_void_p()

    def close(self):
        if self.library is not None and self.bus.value:
            self.library.sd_bus_flush_close_unref(self.bus)
            self.bus = C.c_void_p()

    def sample(self):
        controllers = [entry.name for entry in self.root.glob("hci*")
                       if re.fullmatch(r"hci\d+", entry.name)]
        if not controllers:
            return "absent"
        try:
            if self.library is None:
                self.library = C.CDLL("libsystemd.so.0")
                self.library.sd_bus_open_system.argtypes = [C.POINTER(C.c_void_p)]
                self.library.sd_bus_open_system.restype = C.c_int
                self.library.sd_bus_set_method_call_timeout.argtypes = [C.c_void_p, C.c_uint64]
                self.library.sd_bus_set_method_call_timeout.restype = C.c_int
                self.library.sd_bus_get_property_trivial.argtypes = [
                    C.c_void_p, C.c_char_p, C.c_char_p, C.c_char_p, C.c_char_p,
                    C.c_void_p, C.c_char, C.c_void_p]
                self.library.sd_bus_get_property_trivial.restype = C.c_int
                self.library.sd_bus_flush_close_unref.argtypes = [C.c_void_p]
                self.library.sd_bus_flush_close_unref.restype = C.c_void_p
            if not self.bus.value:
                if self.library.sd_bus_open_system(C.byref(self.bus)) < 0:
                    return "unknown"
                if self.library.sd_bus_set_method_call_timeout(self.bus, 1000000) < 0:
                    self.close()
                    return "unknown"
            failed = False
            for controller in controllers:
                powered = C.c_int()
                result = self.library.sd_bus_get_property_trivial(
                    self.bus, b"org.bluez", ("/org/bluez/" + controller).encode(),
                    b"org.bluez.Adapter1", b"Powered", None, b"b", C.byref(powered))
                if result < 0:
                    failed = True
                elif powered.value:
                    return "on"
            if not failed:
                return "off"
        except (OSError, AttributeError):
            pass
        self.close()
        return "unknown"


def read_battery(node):
    """One read-only HID request, isolated from the bar's event loop."""
    if not re.fullmatch(r"hidraw\d+", node):
        return None
    found = find_trackpad()
    if found is None or found[0] != node:
        return None
    vendor = Path(__file__).resolve().parents[1] / "config/bluetooth/vendor/magic-trackpad-battery"
    if not vendor.is_file():
        vendor = Path.home() / ".local/lib/bgh-bluetooth/magic-trackpad-battery"
    loader = importlib.machinery.SourceFileLoader("trackpad_battery_vendor", str(vendor))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    try:
        sys.dont_write_bytecode = True
        loader.exec_module(module)
        descriptor = os.open("/dev/" + node, os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)
        try:
            return module.read_battery(descriptor)
        finally:
            os.close(descriptor)
    except OSError:
        return None


class BluetoothStatus:
    def __init__(self, query=None, finder=find_trackpad, clock=time.monotonic):
        self.source = BlueZ() if query is None else None
        self.query = self.source.sample if query is None else query
        self.finder, self.clock = finder, clock
        self.identity = self.worker = self.last = None
        self.started = self.next_read = 0
        self.failed = False

    def stop_reader(self):
        if self.worker is not None:
            if self.worker.poll() is None:
                self.worker.kill()
            self.worker.communicate()
            self.worker = None

    def close(self):
        self.stop_reader()
        if self.source is not None:
            self.source.close()

    def sample(self):
        now, adapter = self.clock(), self.query()
        found = self.finder() if adapter not in ("absent", "off") else None
        if found != self.identity:
            self.stop_reader()
            self.identity, self.last = found, None
            self.next_read, self.failed = 0, False
        state = {"adapter": adapter, "connected": found is not None,
                 "percentage": None, "charging": False, "stale": False}
        if adapter == "on" and found is not None:
            state["adapter"] = "connected"
        if found is None:
            return state
        if self.worker is not None:
            if self.worker.poll() is not None:
                output, _ = self.worker.communicate()
                self.worker = None
                self.failed = True
                try:
                    reading = json.loads(output)
                    if (isinstance(reading, list) and len(reading) == 2 and
                            type(reading[0]) is int and 0 <= reading[0] <= 100 and
                            type(reading[1]) is bool):
                        self.last, self.failed = (now, *reading), False
                except (ValueError, UnicodeError):
                    pass
            elif now - self.started >= WORKER_TIMEOUT:
                self.stop_reader()
                self.failed = True
        if self.worker is None and now >= self.next_read:
            self.started, self.next_read = now, now + BATTERY_INTERVAL
            try:
                self.worker = subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), "--read-battery", found[0]],
                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            except OSError:
                self.failed = True
        if self.last is not None and 0 <= now - self.last[0] <= BATTERY_MAX_AGE:
            state.update(percentage=self.last[1], charging=self.last[2],
                         stale=self.failed or now - self.last[0] > BATTERY_INTERVAL + WORKER_TIMEOUT)
        return state


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--read-battery":
        print(json.dumps(read_battery(sys.argv[2])))
    else:
        print("Usage: bluetooth-status.py --read-battery hidrawN", file=sys.stderr)
        sys.exit(2)
