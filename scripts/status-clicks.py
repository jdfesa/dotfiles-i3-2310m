#!/usr/bin/python3
"""Event-driven i3status adapter with local traffic and fixed click actions."""
import html
import importlib.util
import json
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import sys
import time

TEXT = "#cdd6f4"
RED = "#f38ba8"
YELLOW = "#f9e2af"
LAVENDER = "#b4befe"
ICON_FONT = "JetBrainsMono Nerd Font Propo 12"
WEATHER_ICONS = {"☀": "\uf185", "☾": "\uf186", "☁": "\uf0c2", "≋": "\ue313",
                 "☂": "\ue318", "❄": "\U000f0598", "ϟ": "\U000f0593", "?": "\ue370"}
BATTERY_ABSENT = "\U000f17e9"
BATTERY_UNKNOWN = "\U000f0091"
BATTERY_FULL = "\U000f17e2"
BATTERY_LEVELS = ("\U000f008e", "\U000f007a", "\U000f007b", "\U000f007c",
                  "\U000f007d", "\U000f007e", "\U000f007f", "\U000f0080",
                  "\U000f0081", "\U000f0082", "\U000f0079")
BATTERY_CHARGING_LEVELS = ("\U000f089f", "\U000f089c", "\U000f0086", "\U000f0087",
                           "\U000f0088", "\U000f089d", "\U000f0089", "\U000f089e",
                           "\U000f008a", "\U000f008b", "\U000f0085")
BATTERY_IDLE_MARK = "\uf04c"
SECONDARY_BLOCKS = frozenset(("traffic", "memory", "cpu_usage", "cpu_temperature", "disk_info"))
PANELS = {("tztime", "local"): "calendar", ("cpu_usage", "aggregate"): "resources",
          ("trackpad", "battery"): "trackpad", ("volume", "usb-output"): "audio",
          ("screen_brightness", "internal-display"): "brightness"}


def labeled(icon, text, color):
    return f'<span font_desc="{ICON_FONT}" foreground="{color}">{icon}</span> {html.escape(text)}'


def format_weather(text):
    match = re.fullmatch(r"(~?)([☀☾☁≋☂❄ϟ?])\s+(.+)", text)
    if match:
        return match[1] + labeled(WEATHER_ICONS[match[2]], match[3], TEXT)
    return html.escape(text)


def format_battery(text):
    text = text.strip() if isinstance(text, str) else ""
    if text == "absent":
        return labeled(BATTERY_ABSENT, "", "#7f849c").rstrip()
    match = re.fullmatch(r"(charging|discharging|full|idle|unknown) ([0-9]{1,3})%", text)
    if match is None or int(match[2]) > 100:
        return labeled(BATTERY_UNKNOWN, "", YELLOW).rstrip()
    state, percentage = match[1], int(match[2])
    if state == "charging":
        icon, color = BATTERY_CHARGING_LEVELS[percentage // 10], "#a6e3a1"
    elif state == "full":
        icon, color = BATTERY_FULL, "#a6e3a1"
    elif state == "unknown":
        icon, color = BATTERY_UNKNOWN, YELLOW
    elif state == "idle":
        icon, color = BATTERY_LEVELS[percentage // 10] + " " + BATTERY_IDLE_MARK, YELLOW
    else:
        icon = BATTERY_LEVELS[percentage // 10]
        color = RED if state == "discharging" and percentage < 15 else (
            YELLOW if state == "discharging" and percentage < 30 else TEXT)
    return labeled(icon, f"{percentage}%", color)


class Traffic:
    """Two sysfs reads per existing status tick; no socket/polling daemon."""
    def __init__(self, root=Path("/sys/class/net/wlp2s0/statistics"), clock=time.monotonic):
        self.root, self.clock, self.previous = root, clock, None

    @staticmethod
    def rate(value):
        if value >= 1024 * 1024:
            return f"{value / (1024 * 1024):.1f}M"
        return f"{value / 1024:.0f}K"

    def sample(self):
        try:
            now = self.clock()
            received = int((self.root / "rx_bytes").read_text())
            sent = int((self.root / "tx_bytes").read_text())
            if min(received, sent) < 0:
                raise ValueError("invalid counters")
        except (OSError, ValueError):
            self.previous = None
            return "↑-- ↓--"
        previous, self.previous = self.previous, (now, received, sent)
        if previous is None or now <= previous[0] or received < previous[1] or sent < previous[2]:
            return "↑-- ↓--"
        seconds = now - previous[0]
        return f"↑{self.rate((sent - previous[2]) / seconds)} ↓{self.rate((received - previous[1]) / seconds)}/s"


def peripheral_blocks(state):
    adapter = state["adapter"]
    icon = "\U000f00b1" if adapter == "connected" else "\U000f00af" if adapter == "on" else "\U000f00b2"
    color = "#89b4fa" if adapter in ("on", "connected") else RED if adapter == "absent" else "#7f849c"
    bluetooth = {"name": "bluetooth", "instance": "adapter", "min_width": 24, "align": "center",
                 "full_text": labeled(icon, "?" if adapter == "unknown" else "", color).rstrip()}
    percentage = state["percentage"]
    text = "off" if not state["connected"] else "--%" if percentage is None else f"{percentage}%"
    if state["stale"]:
        text = "~" + text
    if state["charging"]:
        text += "+"
    low = percentage is not None and percentage <= 15 and not state["stale"]
    trackpad = {"name": "trackpad", "instance": "battery", "urgent": low and not state["charging"],
                "full_text": labeled("\U000f07f8", text, RED if low else "#a6e3a1" if state["connected"] else "#7f849c")}
    return [bluetooth, trackpad]


def adapt_status(blocks, traffic=None, peripherals=None, audio=None, brightness=None):
    if peripherals is not None:
        index = next((i for i, block in enumerate(blocks) if block.get("name") in ("battery", "tztime")), len(blocks))
        blocks[index:index] = peripheral_blocks(peripherals.sample())
    if audio is not None:
        state = audio.sample()
        blocks[:] = [block for block in blocks if block.get("name") != "volume"]
    else:
        state = {"status": "absent"}
    if not any(block.get("name") == "volume" for block in blocks):
        index = next((i for i, block in enumerate(blocks) if block.get("name") == "wireless"), len(blocks))
        text = "absent" if state["status"] == "absent" else "unavailable"
        if state["status"] == "ready":
            text = ("muted " if state["muted"] else "") + f'{state["percentage"]}%'
        blocks.insert(index, {"name": "volume", "instance": "usb-output", "full_text": text})
    if brightness is not None:
        level = brightness()
        index = next(i for i, block in enumerate(blocks) if block.get("name") == "volume")
        label = "?" if level is None else f"{level}%"
        blocks.insert(index, {"name": "screen_brightness", "instance": "internal-display",
                              "full_text": labeled("\uf185", label, "#7f849c" if level is None else YELLOW)})
    for block in blocks:
        name, text = block.get("name"), block.get("full_text", "")
        if name == "wireless" and block.get("instance") == "wlp2s0":
            quality = re.fullmatch(r"\s*(\d{1,3})%\s*", text)
            value = min(100, int(quality[1])) if quality else None
            level = max(1, min(4, (value + 24) // 25)) if value is not None else 0
            block["full_text"] = f'<span font_desc="BGH Status Icons 12">{chr(0xE000 + level)}</span>'
            block["min_width"], block["align"] = 28, "center"
            block["color"] = RED if value is None or value <= 25 else YELLOW if value <= 50 else "#f2cdcd"
        elif name == "cpu_usage":
            block["instance"] = "aggregate"
            block["full_text"] = labeled("\uf2db", text, YELLOW)
        elif name == "cpu_temperature":
            block["full_text"] = labeled("\U000f050f", text, "#fab387")
        elif name == "memory":
            block["full_text"] = labeled("\uefc5", text, RED)
        elif name == "disk_info":
            block["full_text"] = labeled("\uf0a0", text.replace(" GB", "G"), "#a6e3a1")
        elif name == "volume":
            volume = re.fullmatch(r"(muted )?(\d+)%", text.strip())
            if volume:
                icon = "\ueee8" if volume[1] else "\uf028" if int(volume[2]) > 50 else "\uf027" if int(volume[2]) else "\uf026"
                block["full_text"] = labeled(icon, volume[2] + "%", YELLOW)
            else:
                block["full_text"] = labeled("\ueee8", "No audio" if text == "absent" else "Audio ?", "#7f849c")
            block["min_width"], block["align"] = 24, "center"
        elif name == "battery":
            block["full_text"] = format_battery(text)
            block["min_width"], block["align"] = 24, "center"
        elif name == "read_file" and block.get("instance", "").endswith("/weather.txt"):
            block["full_text"] = format_weather(text)
        elif name == "read_file" and block.get("instance", "").endswith("/updates.txt"):
            block["full_text"] = labeled("\U000f03d7", text, "#f5c2e7")
        elif name == "tztime":
            block["color"] = LAVENDER
        block.setdefault("color", TEXT)
        block["markup"] = "pango"
        block["short_text"] = block["full_text"]
        block["separator"] = False
        block["separator_block_width"] = 4 if name == "volume" else 12
    if traffic is not None:
        blocks.insert(1, {"name": "traffic", "instance": "wlp2s0", "full_text": traffic.sample(),
                          "color": "#7f849c", "separator": False, "separator_block_width": 12})
    return blocks


class StatusView:
    """Keep a formatted sample so clicks redraw without sampling or processes."""
    def __init__(self):
        self.expanded = False
        self.snapshot = None

    def update(self, blocks, traffic=None, peripherals=None, audio=None, brightness=None):
        self.snapshot = adapt_status([dict(block) for block in blocks], traffic, peripherals, audio, brightness)
        return self.render()

    def render(self):
        if self.snapshot is None:
            return None
        blocks = [block for block in self.snapshot
                  if self.expanded or block.get("name") not in SECONDARY_BLOCKS
                  or block.get("urgent") is True]
        index = next((i for i, block in enumerate(blocks)
                      if (block.get("name") == "read_file" and
                          block.get("instance", "").endswith("/updates.txt")) or
                      block.get("name") in ("screen_brightness", "volume", "wireless", "battery", "tztime")), len(blocks))
        chevron = "\uf053" if self.expanded else "\uf054"
        blocks.insert(index, {"name": "stats_toggle", "instance": "secondary",
                              "full_text": chevron, "short_text": chevron,
                              "color": LAVENDER, "min_width": 28, "align": "center",
                              "markup": "pango", "separator": False,
                              "separator_block_width": 12})
        return blocks


def popup_anchor(event):
    x, y, dx, dy, width, height = (event.get(key) for key in
                                  ("x", "y", "relative_x", "relative_y", "width", "height"))
    if not all(type(n) is int for n in (x, y, dx, dy, width, height)):
        return None
    if not (-32768 <= x <= 32767 and -32768 <= y <= 32767 and
            1 <= width <= 32767 and 1 <= height <= 256 and 0 <= dx < width and 0 <= dy < height):
        return None
    center, bottom = x - dx + width // 2, y - dy + height
    return (center, bottom) if all(-32768 <= n <= 32767 for n in (center, bottom)) else None


def handle_click(event, view=None):
    if type(event.get("button")) is not int or event["button"] != 1:
        return False
    if event.get("name") == "stats_toggle" and event.get("instance") == "secondary":
        if view is not None:
            view.expanded = not view.expanded
            return True
        return False
    helper = None
    if event.get("name") == "wireless" and event.get("instance") == "wlp2s0":
        helper = "open-networks.sh"
    elif event.get("name") == "read_file" and event.get("instance") == str(Path.home() / ".cache/i3/updates.txt"):
        helper = "open-updates.sh"
    else:
        panel = next((panel for identity, panel in PANELS.items()
                      if identity == (event.get("name"), event.get("instance"))), None)
        if panel is not None:
            helper = "status-panel.py " + panel
            anchor = popup_anchor(event)
            if anchor is not None:
                helper += f" {anchor[0]} {anchor[1]}"
    if helper:
        # Only allowlisted helper names; never interpret event strings/SSID.
        subprocess.run(["i3-msg", f"exec --no-startup-id ~/scripts/{helper}"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=3, check=True)
    return False


def main(run_once=False):
    spec = importlib.util.spec_from_file_location("bluetooth_status", Path(__file__).with_name("bluetooth-status.py"))
    bluetooth = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bluetooth)
    peripherals = bluetooth.BluetoothStatus()
    spec = importlib.util.spec_from_file_location("audio_control", Path(__file__).with_name("audio-control.py"))
    audio_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audio_module)
    audio = audio_module.AudioStatus()
    spec = importlib.util.spec_from_file_location("screen_brightness", Path(__file__).with_name("screen-brightness.py"))
    brightness = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(brightness)
    spec = importlib.util.spec_from_file_location("audio_position", Path(__file__).with_name("audio-position.py"))
    position_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(position_module)
    try:
        position = None if run_once else position_module.PositionMemory()
    except OSError:
        position = None
    source = Path.home() / "scripts/status-bar.sh"
    child = subprocess.Popen([str(source)] + (["--run-once"] if run_once else []),
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, bufsize=0)
    def terminate(*_):
        raise SystemExit(0)
    signal.signal(signal.SIGTERM, terminate)
    signal.signal(signal.SIGINT, terminate)
    # i3bar signals the entire status_command process group, including its
    # /bin/sh launcher and i3status. Keep the protocol defaults (SIGSTOP /
    # SIGCONT): custom USR signals kill other group members, not just Python.
    print(json.dumps({"version": 1, "click_events": True}), flush=True)
    print("[", flush=True)
    poller = selectors.DefaultSelector()
    buffers = {}
    poller.register(child.stdout, selectors.EVENT_READ, "status")
    if not run_once:
        poller.register(sys.stdin, selectors.EVENT_READ, "click")
    first = True
    traffic = Traffic()
    view = StatusView()

    def emit(blocks):
        nonlocal first
        if position is not None:
            position.publish(blocks)
        print(("" if first else ",") + json.dumps(blocks, ensure_ascii=False), flush=True)
        first = False

    try:
        while True:
            for key, _ in poller.select():
                fd = key.fd
                chunk = os.read(fd, 65536)
                if not chunk:
                    if key.data == "status":
                        return child.wait()
                    poller.unregister(key.fileobj)
                    continue
                buffers[fd] = buffers.get(fd, b"") + chunk
                while b"\n" in buffers[fd]:
                    line, buffers[fd] = buffers[fd].split(b"\n", 1)
                    line = line.strip().lstrip(b",").strip()
                    if line in (b"", b"[", b"]"):
                        continue
                    try:
                        value = json.loads(line)
                    except (ValueError, UnicodeError):
                        continue
                    if key.data == "click" and isinstance(value, dict):
                        try:
                            if handle_click(value, view):
                                frame = view.render()
                                if frame is not None:
                                    emit(frame)
                        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                            print("Could not open status panel", file=sys.stderr)
                    elif key.data == "status" and isinstance(value, list):
                        emit(view.update(value, traffic, peripherals, audio, brightness.sample))
    finally:
        if position is not None:
            position.close()
        peripherals.close()
        poller.close()
        if child.poll() is None:
            child.send_signal(signal.SIGCONT)
            child.terminate()
            try:
                child.wait(timeout=3)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


if __name__ == "__main__":
    sys.exit(main("--run-once" in sys.argv[1:]))
