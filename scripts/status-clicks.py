#!/usr/bin/python3
"""Event-driven i3status adapter with local traffic and fixed click actions."""
import html
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
WEATHER_ICONS = {"☀": "\ue30d", "☾": "\ue32b", "☁": "\ue312", "≋": "\ue313",
                 "☂": "\ue318", "❄": "\ue31a", "ϟ": "\ue31d"}


def labeled(icon, text, color):
    return f'<span foreground="{color}">{icon}</span> {html.escape(text)}'


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


def adapt_status(blocks, traffic=None):
    if not any(block.get("name") == "volume" for block in blocks):
        index = next((i for i, block in enumerate(blocks) if block.get("name") == "wireless"), len(blocks))
        blocks.insert(index, {"name": "volume", "instance": "default.Master.0", "full_text": "unavailable"})
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
            block["full_text"] = labeled("\uf2db", "CPU " + text, YELLOW)
        elif name == "cpu_temperature":
            block["full_text"] = labeled("\U000f050f", text, "#fab387")
        elif name == "memory":
            block["full_text"] = labeled("\uefc5", "RAM " + text, RED)
        elif name == "disk_info":
            block["full_text"] = labeled("\uf0a0", text.replace(" GB", "G"), "#a6e3a1")
        elif name == "volume":
            volume = re.fullmatch(r"(muted )?(\d+)%", text.strip())
            if volume:
                icon = "\ueee8" if volume[1] else "\uf028" if int(volume[2]) > 50 else "\uf027" if int(volume[2]) else "\uf026"
                block["full_text"] = f'<span foreground="{YELLOW}">{icon}</span>'
            else:
                block["full_text"] = labeled("\ueee8", "No audio", "#7f849c")
            block["min_width"], block["align"] = 28, "center"
        elif name == "read_file" and block.get("instance", "").endswith("/weather.txt"):
            text = re.sub(r"[☀☾☁≋☂❄ϟ]", lambda m: WEATHER_ICONS[m[0]], text)
            block["full_text"] = html.escape(text)
        elif name == "read_file" and block.get("instance", "").endswith("/updates.txt"):
            block["full_text"] = labeled("\U000f03d7", text, "#f5c2e7")
        elif name == "tztime":
            block["color"] = LAVENDER
        block.setdefault("color", TEXT)
        block["markup"] = "pango"
        block["short_text"] = block["full_text"]
        block["separator"] = False
        block["separator_block_width"] = 12
    if traffic is not None:
        blocks.insert(1, {"name": "traffic", "instance": "wlp2s0", "full_text": traffic.sample(),
                          "color": "#7f849c", "separator": False, "separator_block_width": 12})
    return blocks


def handle_click(event):
    if type(event.get("button")) is not int or event["button"] != 1:
        return
    helper = None
    if event.get("name") == "wireless" and event.get("instance") == "wlp2s0":
        helper = "open-networks.sh"
    elif event.get("name") == "volume" and event.get("instance") == "default.Master.0":
        helper = "open-mixer.sh"
    elif event.get("name") == "read_file" and event.get("instance") == str(Path.home() / ".cache/i3/updates.txt"):
        helper = "open-updates.sh"
    if helper:
        # Only allowlisted helper names; never interpret event strings/SSID.
        subprocess.run(["i3-msg", f"exec --no-startup-id ~/scripts/{helper}"],
                       stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=3, check=True)


def main(run_once=False):
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
                            handle_click(value)
                        except (OSError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                            print("Could not open status panel", file=sys.stderr)
                    elif key.data == "status" and isinstance(value, list):
                        print(("" if first else ",") + json.dumps(adapt_status(value, traffic), ensure_ascii=False), flush=True)
                        first = False
    finally:
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
