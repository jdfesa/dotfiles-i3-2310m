#!/usr/bin/python3
"""Three-finger workspace swipes using the existing XInput 2.4 server."""
import argparse
import ctypes as C
import math
from pathlib import Path
import re
import select
import signal
import subprocess
import sys


BEGIN, UPDATE, END = 30, 31, 32
HIERARCHY, GENERIC, SELECTION_CLEAR = 11, 35, 29
COMMANDS = {"left": "workspace next_on_output", "right": "workspace prev_on_output"}
IDENTITIES = {(0x0005, 0x004c, 0x0265), (0x0003, 0x05ac, 0x0265)}
MIN_DISTANCE = 100.0


class Cookie(C.Structure):
    _fields_ = [("type", C.c_int), ("serial", C.c_ulong), ("send_event", C.c_int),
                ("display", C.c_void_p), ("extension", C.c_int), ("evtype", C.c_int),
                ("cookie", C.c_uint), ("data", C.c_void_p)]


class Event(C.Union):
    _fields_ = [("type", C.c_int), ("cookie", Cookie), ("pad", C.c_long * 24)]


class Modifiers(C.Structure):
    _fields_ = [(name, C.c_int) for name in ("base", "latched", "locked", "effective")]


class Swipe(C.Structure):
    # ABI from libXi XInput2.h; Xlib Time/Window are unsigned long, not uint32.
    _fields_ = Cookie._fields_[:6] + [
        ("time", C.c_ulong), ("deviceid", C.c_int), ("sourceid", C.c_int),
        ("detail", C.c_int), ("root", C.c_ulong), ("event", C.c_ulong),
        ("child", C.c_ulong)] + [(name, C.c_double) for name in (
            "root_x", "root_y", "event_x", "event_y", "delta_x", "delta_y",
            "delta_unaccel_x", "delta_unaccel_y")] + [
        ("flags", C.c_int), ("mods", Modifiers), ("group", Modifiers)]


class AnyClass(C.Structure):
    _fields_ = [("type", C.c_int), ("sourceid", C.c_int)]


class DeviceInfo(C.Structure):
    _fields_ = [("deviceid", C.c_int), ("name", C.c_char_p), ("use", C.c_int),
                ("attachment", C.c_int), ("enabled", C.c_int), ("num_classes", C.c_int),
                ("classes", C.POINTER(C.POINTER(AnyClass)))]


class Mask(C.Structure):
    _fields_ = [("deviceid", C.c_int), ("mask_len", C.c_int),
                ("mask", C.POINTER(C.c_ubyte))]


class GrabModifier(C.Structure):
    _fields_ = [("modifiers", C.c_int), ("status", C.c_int)]


class XError(C.Structure):
    _fields_ = [("type", C.c_int), ("display", C.c_void_p), ("resourceid", C.c_ulong),
                ("serial", C.c_ulong), ("error_code", C.c_ubyte),
                ("request_code", C.c_ubyte), ("minor_code", C.c_ubyte)]


def event_mask(device, events):
    bits = (C.c_ubyte * 5)()
    for event in events:
        bits[event // 8] |= 1 << (event % 8)
    return Mask(device, len(bits), bits)


def is_trackpad(node, root=Path("/sys/class/input")):
    if not re.fullmatch(r"/dev/input/event[0-9]+", node):
        return False
    try:
        device = root / Path(node).name / "device"
        identity = tuple(int((device / "id" / key).read_text(), 16)
                         for key in ("bustype", "vendor", "product"))
        return (identity in IDENTITIES and
                (device / "device/driver").resolve(strict=True).name == "magicmouse")
    except (OSError, ValueError):
        return False


class Recognizer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.source = None
        self.dx = self.dy = 0.0

    def feed(self, kind, source, fingers, dx=0.0, dy=0.0, cancelled=False):
        if kind == BEGIN:
            self.reset()
            if fingers == 3 and not cancelled:
                self.source = source
        if self.source != source:
            return None
        if cancelled or fingers != 3 or not all(map(math.isfinite, (dx, dy))):
            self.reset()
            return None
        self.dx += dx
        self.dy += dy
        if kind != END:
            return None
        horizontal = abs(self.dx) >= MIN_DISTANCE and abs(self.dx) > 2 * abs(self.dy)
        direction = ("left" if self.dx < 0 else "right") if horizontal else None
        self.reset()
        return direction


def switch_workspace(direction):
    result = subprocess.run(["i3-msg", "-q", COMMANDS[direction]],
                            stdin=subprocess.DEVNULL, capture_output=True, timeout=2)
    if result.returncode:
        raise RuntimeError("i3 could not switch the workspace.")


class XInput:
    def __init__(self):
        self.x = C.CDLL("libX11.so.6")
        self.xi = C.CDLL("libXi.so.6")
        ptr, integer, ulong = C.c_void_p, C.c_int, C.c_ulong
        ip, up = C.POINTER(integer), C.POINTER(ulong)
        self.bind(self.x, "XOpenDisplay", ptr, [C.c_char_p])
        self.bind(self.x, "XCloseDisplay", integer, [ptr])
        self.bind(self.x, "XDefaultRootWindow", ulong, [ptr])
        self.bind(self.x, "XConnectionNumber", integer, [ptr])
        self.bind(self.x, "XQueryExtension", integer, [ptr, C.c_char_p, ip, ip, ip])
        self.bind(self.x, "XInternAtom", ulong, [ptr, C.c_char_p, integer])
        self.bind(self.x, "XFree", integer, [ptr])
        self.bind(self.x, "XPending", integer, [ptr])
        self.bind(self.x, "XNextEvent", integer, [ptr, C.POINTER(Event)])
        self.bind(self.x, "XGetEventData", integer, [ptr, C.POINTER(Cookie)])
        self.bind(self.x, "XFreeEventData", None, [ptr, C.POINTER(Cookie)])
        self.bind(self.x, "XGetSelectionOwner", ulong, [ptr, ulong])
        self.bind(self.x, "XSetSelectionOwner", integer, [ptr, ulong, ulong, ulong])
        self.bind(self.x, "XCreateSimpleWindow", ulong,
                  [ptr, ulong, integer, integer, C.c_uint, C.c_uint, C.c_uint, ulong, ulong])
        self.bind(self.x, "XSync", integer, [ptr, integer])
        handler_type = C.CFUNCTYPE(integer, ptr, C.POINTER(XError))
        self.errors = []
        self.error_handler = handler_type(self.on_error)
        self.bind(self.x, "XSetErrorHandler", ptr, [handler_type])
        self.x.XSetErrorHandler(self.error_handler)
        self.bind(self.xi, "XIQueryVersion", integer, [ptr, ip, ip])
        self.bind(self.xi, "XIQueryDevice", C.POINTER(DeviceInfo), [ptr, integer, ip])
        self.bind(self.xi, "XIFreeDeviceInfo", None, [C.POINTER(DeviceInfo)])
        self.bind(self.xi, "XIGetProperty", integer,
                  [ptr, integer, ulong, C.c_long, C.c_long, integer, ulong,
                   up, ip, up, up, C.POINTER(ptr)])
        self.bind(self.xi, "XISelectEvents", integer, [ptr, ulong, C.POINTER(Mask), integer])
        self.bind(self.xi, "XIGrabSwipeGestureBegin", integer,
                  [ptr, integer, ulong, integer, integer, integer, C.POINTER(Mask),
                   integer, C.POINTER(GrabModifier)])
        self.bind(self.xi, "XIUngrabSwipeGestureBegin", integer,
                  [ptr, integer, ulong, integer, C.POINTER(GrabModifier)])
        self.display = self.x.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError("An authenticated local Xorg display is required.")
        self.targets = set()

    @staticmethod
    def bind(library, name, restype, argtypes):
        function = getattr(library, name)
        function.restype, function.argtypes = restype, argtypes

    def setup(self):
        major, minor = C.c_int(2), C.c_int(4)
        opcode, event, error = C.c_int(), C.c_int(), C.c_int()
        if not self.x.XQueryExtension(self.display, b"XInputExtension",
                                      C.byref(opcode), C.byref(event), C.byref(error)):
            raise RuntimeError("XInput is unavailable.")
        if self.xi.XIQueryVersion(self.display, C.byref(major), C.byref(minor)) or (
                major.value, minor.value) < (2, 4):
            raise RuntimeError("XInput 2.4 or newer is required.")
        self.opcode = opcode.value
        self.bad_device = error.value  # XI BadDevice is extension error base + 0.
        self.root = self.x.XDefaultRootWindow(self.display)
        self.node_atom = self.x.XInternAtom(self.display, b"Device Node", True)
        self.selection = self.x.XInternAtom(self.display, b"_BGH_TRACKPAD_GESTURES", False)

    def on_error(self, display, error):
        self.errors.append(error.contents.error_code)
        return 0

    def sync(self, ignored=()):
        self.x.XSync(self.display, False)
        errors, self.errors = self.errors, []
        if any(code not in (self.bad_device, *ignored) for code in errors):
            raise RuntimeError("An XInput request failed; gestures stopped safely.")
        # A device removed between query and request is normal during hotplug.
        return not errors

    def device_node(self, device):
        if not self.node_atom:
            return ""
        actual, fmt, count, after, data = C.c_ulong(), C.c_int(), C.c_ulong(), C.c_ulong(), C.c_void_p()
        try:
            status = self.xi.XIGetProperty(self.display, device, self.node_atom, 0, 256,
                                           False, 31, C.byref(actual), C.byref(fmt),
                                           C.byref(count), C.byref(after), C.byref(data))
            valid = self.sync()
            if valid and not status and actual.value == 31 and fmt.value == 8 and not after.value and data:
                return C.string_at(data, count.value).rstrip(b"\0").decode("ascii")
        except UnicodeDecodeError:
            pass
        finally:
            if data:
                self.x.XFree(data)
        return ""

    def devices(self):
        count = C.c_int()
        info = self.xi.XIQueryDevice(self.display, 0, C.byref(count))
        live, targets = set(), set()
        try:
            for device in info[:count.value] if info else ():
                live.add(device.deviceid)
                if (device.use == 3 and device.enabled and
                        any(device.classes[i].contents.type == 9 for i in range(device.num_classes))
                        and is_trackpad(self.device_node(device.deviceid))):
                    targets.add(device.deviceid)
        finally:
            if info:
                self.xi.XIFreeDeviceInfo(info)
        return live, targets

    def refresh(self):
        live, targets = self.devices()
        grabbed = set()
        modifier = GrabModifier(-2147483648, 0)  # XIAnyModifier
        # Rebuild even when an unplug/replug reused the same X ID before dispatch.
        for device in self.targets & live:
            self.xi.XIUngrabSwipeGestureBegin(self.display, device, self.root, 1, C.byref(modifier))
        self.sync(ignored=(8,))  # BadMatch: a reused ID no longer has gestures.
        for device in targets:
            mask = event_mask(device, (BEGIN, UPDATE, END))
            # Passive swipe grab only; never grab keys, buttons, motion or pinch.
            failed = self.xi.XIGrabSwipeGestureBegin(self.display, device, self.root, 1, 1, False,
                                                    C.byref(mask), 1, C.byref(modifier))
            if not self.sync():
                continue
            if failed:
                raise RuntimeError("Another client owns the trackpad swipe gestures.")
            grabbed.add(device)
        self.targets = grabbed
        self.sync()

    def claim(self):
        if self.x.XGetSelectionOwner(self.display, self.selection):
            return False
        window = self.x.XCreateSimpleWindow(self.display, self.root, 0, 0, 1, 1, 0, 0, 0)
        self.x.XSetSelectionOwner(self.display, self.selection, window, 0)
        self.x.XSync(self.display, False)
        return self.x.XGetSelectionOwner(self.display, self.selection) == window

    def stop(self):
        self.x.XSetSelectionOwner(self.display, self.selection, 0, 0)
        self.x.XSync(self.display, False)

    def run(self, dry_run=False):
        if not self.claim():
            print("Trackpad gestures are already running on this display.")
            return
        mask = event_mask(0, (HIERARCHY,))
        self.xi.XISelectEvents(self.display, self.root, C.byref(mask), 1)
        self.refresh()
        recognizer = Recognizer()
        event = Event()
        print(f"Trackpad gestures ready ({len(self.targets)} matching device(s)).", flush=True)
        while True:
            if not self.x.XPending(self.display):
                select.select([self.x.XConnectionNumber(self.display)], [], [])
            self.x.XNextEvent(self.display, C.byref(event))
            if event.type == SELECTION_CLEAR:
                return
            cookie = event.cookie
            if event.type != GENERIC or cookie.extension != self.opcode or cookie.send_event:
                continue
            if not self.x.XGetEventData(self.display, C.byref(cookie)):
                continue
            try:
                if cookie.evtype == HIERARCHY:
                    recognizer.reset()
                    self.refresh()
                elif cookie.evtype in (BEGIN, UPDATE, END):
                    swipe = C.cast(cookie.data, C.POINTER(Swipe)).contents
                    if swipe.sourceid not in self.targets:
                        continue
                    # Recheck hardware on begin; X IDs and event nodes can be reused.
                    if cookie.evtype == BEGIN and not is_trackpad(self.device_node(swipe.sourceid)):
                        recognizer.reset()
                        continue
                    direction = recognizer.feed(cookie.evtype, swipe.sourceid, swipe.detail,
                                                swipe.delta_x, swipe.delta_y, bool(swipe.flags & 1))
                    if cookie.evtype == END and dry_run:
                        print(COMMANDS[direction] if direction else "Swipe ignored.", flush=True)
                    elif direction:
                        try:
                            switch_workspace(direction)
                        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
                            print(str(error), file=sys.stderr)
            finally:
                self.x.XFreeEventData(self.display, C.byref(cookie))

    def close(self):
        self.x.XCloseDisplay(self.display)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    options = parser.add_mutually_exclusive_group()
    options.add_argument("--check", action="store_true", help="check XInput and matching hardware; do not grab gestures")
    options.add_argument("--dry-run", action="store_true", help="capture swipes and print actions without changing workspaces")
    options.add_argument("--stop", action="store_true", help="stop the listener on this X display")
    args = parser.parse_args()
    connection = None
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        connection = XInput()
        connection.setup()
        if args.stop:
            connection.stop()
        elif args.check:
            _, devices = connection.devices()
            print(f"XInput 2.4 available; {len(devices)} compatible Magic Trackpad 2 device(s).")
        else:
            connection.run(args.dry_run)
        return 0
    except (OSError, RuntimeError) as error:
        print(f"Trackpad gestures: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 0
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
