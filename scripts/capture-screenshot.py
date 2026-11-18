#!/usr/bin/python3
"""Copy an explicitly selected X11 screenshot as PNG, without writing a file."""

import os
import subprocess
import sys


CAPTURE = ("/usr/bin/maim", "--select", "--hidecursor", "--noopengl", "--format=png")
COPY = ("/usr/bin/xclip", "-selection", "clipboard", "-target", "image/png", "-in", "-silent")
PNG_HEADER = b"\x89PNG\r\n\x1a\n"
PNG_END = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def main():
    if not os.environ.get("DISPLAY"):
        print("An X11 session is required to take a screenshot.", file=sys.stderr)
        return 1
    try:
        capture = subprocess.run(CAPTURE, stdout=subprocess.PIPE, check=False)
        if capture.returncode:
            # maim reports capture errors itself. Cancellation also exits nonzero.
            return 1
        png = capture.stdout
        if not (png.startswith(PNG_HEADER) and png.endswith(PNG_END)):
            print("No complete PNG was captured.", file=sys.stderr)
            return 1
        return int(subprocess.run(COPY, input=png, check=False).returncode != 0)
    except OSError as error:
        print(f"Screenshot failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
