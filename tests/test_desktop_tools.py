"""Check the per-app launcher and the scoped VS Code APT source."""
import configparser
import hashlib
import json
from pathlib import Path
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DesktopToolsTests(unittest.TestCase):
    def test_kitty_uses_static_background_alpha_with_basic_x11_compositing(self):
        config = (ROOT / "config/kitty.conf").read_text().splitlines()
        self.assertEqual([line for line in config if line.startswith("background_opacity ")],
                         ["background_opacity 0.85"])
        self.assertIn("background_blur 0", config)
        self.assertIn("dynamic_background_opacity no", config)
        self.assertFalse(any(line.startswith("custom_shaders ") for line in config))
        i3 = (ROOT / "config/i3-config").read_text().splitlines()
        self.assertEqual([line for line in i3 if line.startswith("exec") and "xcompmgr" in line],
                         ["exec --no-startup-id /usr/bin/xcompmgr -n"])

    def test_thunar_launcher_uses_dark_gtk(self):
        desktop = configparser.ConfigParser(interpolation=None)
        desktop.read(ROOT / "config/thunar/thunar.desktop", encoding="utf-8")
        entry = desktop["Desktop Entry"]
        self.assertEqual(shlex.split(entry["Exec"]),
                         ["env", "GTK_THEME=Adwaita:dark", "/usr/bin/thunar", "%U"])
        self.assertEqual(entry["TryExec"], "/usr/bin/thunar")
        self.assertFalse(entry.getboolean("DBusActivatable"))
        self.assertFalse(entry.getboolean("Terminal"))

    def test_microsoft_stable_source_is_limited_to_code(self):
        apt = ROOT / "config/vscode/apt"
        sources = dict(line.split(": ", 1) for line in (apt / "vscode.sources").read_text().splitlines())
        self.assertEqual(sources, {
            "Types": "deb",
            "URIs": "https://packages.microsoft.com/repos/code",
            "Suites": "stable",
            "Components": "main",
            "Architectures": "amd64",
            "Signed-By": "/etc/apt/keyrings/bgh-vscode.asc",
        })
        pin = [dict(line.split(": ", 1) for line in entry.splitlines())
               for entry in (apt / "vscode.pref").read_text().strip().split("\n\n")]
        self.assertEqual(pin, [
            {"Package": "code", "Pin": "release o=code stable", "Pin-Priority": "500"},
            {"Package": "*", "Pin": "release o=code stable", "Pin-Priority": "-1"},
        ])
        self.assertEqual(hashlib.sha256((apt / "microsoft.asc").read_bytes()).hexdigest(),
                         "2fa9c05d591a1582a9aba276272478c262e95ad00acf60eaee1644d93941e3c6")

    def test_manifest_maps_user_links_and_regular_system_files(self):
        manifest = json.loads((ROOT / "config/manifest.json").read_text())
        entries = {entry["source"]: entry for entry in manifest}
        expected = {
            "config/thunar/thunar.desktop": "/home/jd/.local/share/applications/thunar.desktop",
            "config/vscode/apt/microsoft.asc": "/etc/apt/keyrings/bgh-vscode.asc",
            "config/vscode/apt/vscode.sources": "/etc/apt/sources.list.d/vscode.sources",
            "config/vscode/apt/vscode.pref": "/etc/apt/preferences.d/vscode",
        }
        for source, destination in expected.items():
            with self.subTest(source=source):
                item = entries[source]
                self.assertEqual(item["destination"], destination)
                self.assertEqual(item["mode"], 0o644)
                self.assertEqual(item.get("deployment"), "symlink" if destination.startswith("/home/jd/") else None)
