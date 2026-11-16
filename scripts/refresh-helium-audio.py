#!/usr/bin/python3
"""Manually renew only Helium's audio utility after a USB output change."""
import argparse
import importlib.util
import os
from pathlib import Path
import re
import signal
import sys
from typing import NamedTuple

HELIUM = Path("/opt/helium/helium")


class Process(NamedTuple):
    pid: int
    started: int


def audio_module():
    spec = importlib.util.spec_from_file_location("audio_control", Path(__file__).with_name("audio-control.py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def output_ready():
    audio = audio_module()
    profile = audio.load_profile()
    devices = audio.find_devices(profile)
    if len(devices) != 1:
        raise OSError("Connect exactly one configured USB audio output before refreshing Helium.")
    with audio.Mixer(profile, devices[0]) as mixer:
        return mixer.read()


def ensure_capture_closed(root=Path("/proc/asound")):
    if not root.is_dir():
        raise OSError("ALSA capture state is unavailable. No process was restarted.")
    for path in root.glob("card*/pcm*c/sub*/status"):
        if path.read_text().strip() != "closed":
            raise OSError("Audio capture is open. Stop recording or leave the call before refreshing Helium.")


def identify(pid, root=Path("/proc")):
    path = root / str(pid)
    try:
        if path.stat().st_uid != os.getuid() or (path / "exe").resolve(strict=True) != HELIUM:
            return None
        # Chromium may flatten its process title into a single argv field.
        command = (path / "cmdline").read_bytes().replace(bytes([0]), b" ")
        if (re.findall(rb"(?:^|\s)--type=([^\s]+)", command) != [b"utility"] or
                re.findall(rb"(?:^|\s)--utility-sub-type=([^\s]+)", command) != [b"audio.mojom.AudioService"]):
            return None
        started = int((path / "stat").read_text().rsplit(")", 1)[1].split()[19])
        return Process(pid, started)
    except (OSError, ValueError, IndexError):
        return None


def select_service(root=Path("/proc")):
    matches = [process for path in root.iterdir() if path.name.isdigit()
               and (process := identify(int(path.name), root)) is not None]
    if not matches:
        raise OSError("No active Helium AudioService. Start playback and try again.")
    if len(matches) != 1:
        raise OSError("Multiple Helium AudioServices found. No process was restarted.")
    return matches[0]


def guard():
    ensure_capture_closed()
    return output_ready()


def refresh(process):
    # pidfd pins this process; a reused numeric PID must never become a target.
    fd = os.pidfd_open(process.pid)
    try:
        guard()
        if select_service() != process:
            raise OSError("Helium AudioService changed. Run the check again.")
        signal.pidfd_send_signal(fd, signal.SIGTERM)
    finally:
        os.close(fd)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true",
                        help="restart only the verified audio utility; briefly interrupts browser audio")
    args = parser.parse_args(argv)
    try:
        if os.getuid() == 0:
            raise OSError("Run as the desktop user, never root.")
        state = guard()
        process = select_service()
        print(f'USB output ready: {state["percentage"]}%; muted: {str(state["muted"]).lower()}.')
        if args.apply:
            refresh(process)
            print("Helium AudioService refreshed. Resume playback and verify the sound.")
        else:
            print(f"Dry run: would refresh only Helium AudioService PID {process.pid}. Use --apply to proceed.")
        return 0
    except (OSError, ValueError, AttributeError) as error:
        print(f"Audio refresh stopped: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
