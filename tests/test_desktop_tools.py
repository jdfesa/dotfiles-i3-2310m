"""Check the per-app Thunar launcher."""
import configparser
import json
from pathlib import Path
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DesktopToolsTests(unittest.TestCase):
    def test_thunar_uses_dark_gtk_only_through_its_launcher(self):
        desktop = configparser.ConfigParser(interpolation=None)
        desktop.read(ROOT / "config/thunar/thunar.desktop", encoding="utf-8")
        entry = desktop["Desktop Entry"]
        self.assertEqual(shlex.split(entry["Exec"]),
                         ["env", "GTK_THEME=Adwaita:dark", "/usr/bin/thunar", "%U"])
        self.assertEqual(entry["TryExec"], "/usr/bin/thunar")
        self.assertFalse(entry.getboolean("DBusActivatable"))
        self.assertFalse(entry.getboolean("Terminal"))

    def test_manifest_maps_regular_files_to_the_expected_destinations(self):
        manifest = json.loads((ROOT / "config/manifest.json").read_text())
        entries = {entry["source"]: entry for entry in manifest}
        expected = {
            "config/thunar/thunar.desktop": "/home/jd/.local/share/applications/thunar.desktop",
        }
        for source, destination in expected.items():
            with self.subTest(source=source):
                item = entries[source]
                self.assertEqual(item["destination"], destination)
                self.assertEqual(item["mode"], 0o644)
                self.assertNotEqual(item.get("deployment"), "symlink")
