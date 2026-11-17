"""Offline regression checks for the on-demand PDF reader configuration."""

from configparser import ConfigParser
import json
from pathlib import Path
import shlex
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = "config/zathura/zathurarc"


class ZathuraConfigTests(unittest.TestCase):
    def test_mocha_pages_and_standard_clipboard_are_enabled_at_startup(self):
        options = {}
        unbound = []
        for number, line in enumerate((ROOT / SOURCE).read_text().splitlines(), 1):
            tokens = shlex.split(line, comments=True)
            if not tokens:
                continue
            if tokens[0] == "unmap":
                unbound.append(tokens[1:])
                continue
            self.assertEqual(len(tokens), 3, f"Invalid directive at line {number}")
            directive, key, value = tokens
            self.assertEqual(directive, "set", f"Unexpected directive at line {number}")
            self.assertNotIn(key, options, f"Duplicate setting: {key}")
            options[key] = value

        self.assertCountEqual(unbound, [["[normal]", "<C-r>"], ["[fullscreen]", "<C-r>"]])
        expected = {
            "recolor": "true",
            "recolor-keephue": "true",
            "recolor-darkcolor": "#cdd6f4",
            "recolor-lightcolor": "#1e1e2e",
            "default-bg": "#1e1e2e",
            "statusbar-bg": "#181825",
            "inputbar-bg": "#181825",
            "selection-clipboard": "clipboard",
        }
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(options.get(key), value)

    def test_pdf_default_does_not_replace_browser_associations(self):
        config = ConfigParser(interpolation=None)
        config.read_string((ROOT / "config/mimeapps.list").read_text())
        expected = config["Default Applications"]
        self.assertEqual(expected["application/pdf"].rstrip(";"), "org.pwmt.zathura-pdf-poppler.desktop")
        for mime in ("text/html", "x-scheme-handler/http", "x-scheme-handler/https"):
            self.assertEqual(expected[mime].rstrip(";"), "helium.desktop")

    def test_configuration_is_managed_as_a_user_link(self):
        manifest = json.loads((ROOT / "config/manifest.json").read_text())
        self.assertEqual(
            [item for item in manifest if item["source"] == SOURCE],
            [{"source": SOURCE, "destination": "/home/jd/.config/zathura/zathurarc", "mode": 0o644,
              "deployment": "symlink"}],
        )


if __name__ == "__main__":
    unittest.main()
