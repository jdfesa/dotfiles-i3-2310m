#!/usr/bin/python3
"""Save and copy an accepted X11 screenshot after preview and optional edits."""

from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from uuid import uuid4


CAPTURE = ("/usr/bin/flameshot", "gui", "--raw")
COPY = ("/usr/bin/xclip", "-selection", "clipboard", "-target", "image/png", "-in", "-silent")
SAVE_DIRECTORY = Path("Pictures/Screenshots")
PNG_HEADER = b"\x89PNG\r\n\x1a\n"
PNG_END = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def save_png(png, directory):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target = directory / f"screenshot-{stamp}-{uuid4().hex[:8]}.png"
    # Publish only a complete file, never overwriting an existing capture.
    with tempfile.NamedTemporaryFile(dir=directory, prefix=".capture-") as pending:
        pending.write(png)
        pending.flush()
        os.link(pending.name, target)
    return target


def main():
    if not os.environ.get("DISPLAY"):
        print("An X11 session is required to take a screenshot.", file=sys.stderr)
        return 1
    try:
        capture = subprocess.run(CAPTURE, stdout=subprocess.PIPE, check=False,
                                 env=dict(os.environ, QT_QPA_PLATFORM="xcb"))
        if capture.returncode or not capture.stdout:
            # Cancellation can produce no bytes even with exit status zero.
            return int(capture.returncode != 0)
        png = capture.stdout
        if not (png.startswith(PNG_HEADER) and png.endswith(PNG_END)):
            print("No complete PNG was captured.", file=sys.stderr)
            return 1
        saved = save_png(png, Path.home() / SAVE_DIRECTORY)
    except OSError as error:
        print(f"Screenshot failed: {error}", file=sys.stderr)
        return 1
    print(saved)
    try:
        if subprocess.run(COPY, input=png, stdout=subprocess.DEVNULL, check=False).returncode == 0:
            return 0
    except OSError as error:
        print(error, file=sys.stderr)
    print("Screenshot saved, but it could not be copied to the clipboard.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
