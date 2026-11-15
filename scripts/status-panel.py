#!/usr/bin/python3
"""Toggle fixed i3 panels; short-lived IPC subscription, no polling."""
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import struct
import subprocess
import sys
import time

PANELS = {"calendar": ("BGH-Calendar", "bgh-calendar"),
          "resources": ("BGH-Resources", "bgh-resources"),
          "trackpad": ("BGH-Trackpad-Speed", "bgh-trackpad-speed"),
          "audio": ("BGH-Audio-Volume", "bgh-audio-volume")}
HEADER = struct.Struct("=6sII")
WINDOW_EVENT = 0x80000003


class IPC:
    def __init__(self, stream):
        self.stream = stream
        self.deadline = time.monotonic() + 4
        self.events = []

    def read_exact(self, size):
        data = bytearray()
        while len(data) < size:
            remaining = self.deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("Panel IPC deadline exceeded")
            self.stream.settimeout(remaining)
            chunk = self.stream.recv(size - len(data))
            if not chunk:
                raise OSError("i3 IPC disconnected")
            data.extend(chunk)
        return data

    def receive(self):
        magic, size, kind = HEADER.unpack(self.read_exact(HEADER.size))
        if magic != b"i3-ipc" or size > 4 * 1024 * 1024:
            raise ValueError("Invalid i3 IPC packet")
        return kind, json.loads(self.read_exact(size))

    def request(self, kind, payload=""):
        data = payload.encode()
        self.stream.sendall(HEADER.pack(b"i3-ipc", len(data), kind) + data)
        while True:
            response, value = self.receive()
            if response == kind:
                return value
            if response == WINDOW_EVENT:
                self.events.append(value)

    def next_window(self):
        if self.events:
            return self.events.pop(0)
        while True:
            kind, value = self.receive()
            if kind == WINDOW_EVENT:
                return value


def find_panel(node, identity, frame=None):
    if node.get("type") == "floating_con":
        frame = node.get("rect")
    properties = node.get("window_properties", {})
    if (node.get("window") and
            (properties.get("class"), properties.get("instance")) == identity):
        return node, frame or node["rect"]
    for child in node.get("nodes", []) + node.get("floating_nodes", []):
        found = find_panel(child, identity, frame)
        if found is not None:
            return found
    return None


def choose_output(outputs, x, y):
    possible = [o["rect"] for o in outputs if o.get("active") and
                o["rect"]["x"] <= x < o["rect"]["x"] + o["rect"]["width"] and
                o["rect"]["y"] <= y < o["rect"]["y"] + o["rect"]["height"]]
    return possible[0] if possible else None


def target_position(output, panel, x, bottom):
    left, top = output["x"], output["y"]
    right, lower = left + output["width"], top + output["height"]
    return (max(left, min(x - panel["width"] // 2, right - panel["width"])),
            max(top, min(bottom + 4, lower - panel["height"])))


def container_id(panel):
    value = panel.get("id")
    if type(value) is not int or value <= 0:
        raise ValueError("Invalid panel container")
    return value


def launch_command(name):
    gtk_helpers = {"calendar": "calendar-popup.py", "trackpad": "open-trackpad-speed.py",
                   "audio": "audio-volume.py"}
    if name in gtk_helpers:
        source = Path.home() / "scripts" / gtk_helpers[name]
        if not os.access(source, os.X_OK):
            raise RuntimeError(f"{name.capitalize()} helper is not installed.")
        return [str(source)]
    if name != "resources":
        raise ValueError("Unknown panel")
    terminal, btop = shutil.which("kitty"), shutil.which("btop")
    if terminal is None or btop is None:
        raise RuntimeError("Resource monitor requires Kitty and btop.")
    return [terminal, "--class=BGH-Resources", "--name=bgh-resources", "--title=System monitor",
            "--override=tab_bar_min_tabs=2", "--override=confirm_os_window_close=0",
            "-e", btop, "--update", "2000"]


def open_panel(name, anchor=None):
    identity = PANELS[name]
    path = os.environ.get("I3SOCK") or subprocess.check_output(
        ["i3", "--get-socketpath"], text=True, timeout=2).strip()
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as stream:
        stream.settimeout(1)
        stream.connect(path)
        ipc = IPC(stream)
        if not ipc.request(2, '["window"]').get("success"):
            raise RuntimeError("i3 window subscription failed")
        tree = ipc.request(4)
        existing = find_panel(tree, identity)
        if existing is not None:
            panel, _ = existing
            cid = container_id(panel)
            result = ipc.request(0, f"[con_id={cid}] kill")
            if not result or not all(item.get("success") for item in result):
                raise RuntimeError("Could not close panel")
            while True:
                event = ipc.next_window()
                if event.get("change") == "close" and event.get("container", {}).get("id") == cid:
                    return
        if name == "audio" and anchor is None:
            spec = importlib.util.spec_from_file_location("audio_position", Path(__file__).with_name("audio-position.py"))
            position = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(position)
            anchor = position.keyboard_anchor(ipc, tree)
        output = choose_output(ipc.request(3), *anchor) if anchor is not None else None
        command = launch_command(name)
        subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, umask=0o077)
        while True:
            event = ipc.next_window()
            if event.get("change") != "new" or find_panel(event.get("container", {}), identity) is None:
                continue
            if output is None:
                return
            current = find_panel(ipc.request(4), identity)
            if current is None:
                return
            panel, frame = current
            x, y = target_position(output, frame, *anchor)
            result = ipc.request(0, f"[con_id={container_id(panel)}] move absolute position {x} {y}")
            if not result or not all(item.get("success") for item in result):
                raise RuntimeError("Could not position panel")
            return


def toggle_panel(name, anchor=None):
    if name not in PANELS:
        raise ValueError("Unknown panel")
    runtime = Path(os.environ["XDG_RUNTIME_DIR"])
    info = runtime.stat()
    if runtime.is_symlink() or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o022:
        raise OSError("Unsafe runtime directory")
    fd = os.open(runtime / f"bgh-panel-{name}.lock",
                 os.O_CREAT | os.O_RDWR | os.O_CLOEXEC | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "rb") as lock:
        info = os.fstat(lock.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_nlink != 1 or info.st_mode & 0o077:
            raise OSError("Unsafe panel lock")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        open_panel(name, anchor)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", choices=PANELS)
    parser.add_argument("anchor_x", type=int, nargs="?")
    parser.add_argument("bar_bottom", type=int, nargs="?")
    args = parser.parse_args()
    anchor = (args.anchor_x, args.bar_bottom)
    if any(value is None for value in anchor):
        if anchor != (None, None):
            parser.error("Both anchor coordinates are required.")
        anchor = None
    elif any(not -32768 <= value <= 32767 for value in anchor):
        parser.error("Invalid X11 coordinates.")
    os.environ.update(LANG="en_US.UTF-8", LANGUAGE="en_US:en", LC_ALL="en_US.UTF-8")
    try:
        toggle_panel(args.panel, anchor)
    except (KeyError, OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print(f"Could not toggle status panel: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
