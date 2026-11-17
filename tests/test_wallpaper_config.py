"""Check wallpaper asset and startup manifest without connecting to X11."""
import json
from pathlib import Path
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WallpaperConfigTests(unittest.TestCase):
    def test_png_and_user_destination_match_the_one_shot_i3_command(self):
        source = "wallpapers/pixel-car.png"
        target = "/home/jd/.local/share/wallpapers/pixel-car.png"
        data = (ROOT / source).read_bytes()
        self.assertEqual(data[:16], b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR")
        self.assertEqual(struct.unpack_from(">II", data, 16), (1920, 1080))
        self.assertEqual(data[-12:-4], b"\x00\x00\x00\x00IEND")
        entries = json.loads((ROOT / "config/manifest.json").read_text())
        wallpapers = [entry for entry in entries if entry["source"] == source]
        self.assertEqual(wallpapers, [{"source": source, "destination": target, "mode": 0o644,
                                     "deployment": "symlink"}])
        config = (ROOT / "config/i3-config").read_text()
        commands = [line for line in config.splitlines() if line.startswith("exec") and "xwallpaper" in line]
        self.assertEqual(commands,
                         ["exec --no-startup-id /usr/bin/xwallpaper --zoom ~" + target.removeprefix("/home/jd")])
