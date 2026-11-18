"""Validate clipboard behavior using only synthetic capture data."""

import importlib.util
import io
import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = "scripts/capture-screenshot.py"
spec = importlib.util.spec_from_file_location("capture_screenshot", ROOT / SCRIPT)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)


class ScreenshotTests(unittest.TestCase):
    def test_both_release_bindings_run_the_same_managed_script(self):
        destination = f"/home/jd/dotfiles-i3-2310m/{SCRIPT}"
        entry = next(e for e in json.loads((ROOT / "config/manifest.json").read_text())
                     if e["source"] == SCRIPT)
        self.assertEqual((entry["destination"], entry["mode"], entry["deployment"]),
                         (destination, 0o755, "in-place"))
        command = f"exec --no-startup-id ~/dotfiles-i3-2310m/{SCRIPT}"
        bindings = [line for line in (ROOT / "config/i3-config").read_text().splitlines()
                    if line.startswith("bindsym ") and line.endswith(command)]
        self.assertEqual(bindings, [f"bindsym --release Print {command}",
                                    f"bindsym --release $mod+Control+Mod1+c {command}"])

    def test_no_display_does_not_launch_anything(self):
        with (patch.dict(capture.os.environ, {}, clear=True),
              patch("sys.stderr", new_callable=io.StringIO),
              patch.object(capture.subprocess, "run") as run):
            self.assertEqual(capture.main(), 1)
        run.assert_not_called()

    def test_cancel_or_incomplete_output_keeps_the_clipboard(self):
        for code, data in ((1, b""), (1, capture.PNG_HEADER + capture.PNG_END),
                           (0, b""), (0, capture.PNG_HEADER)):
            with (self.subTest(code=code, data=data),
                  patch.dict(capture.os.environ, {"DISPLAY": ":99"}),
                  patch("sys.stderr", new_callable=io.StringIO),
                  patch.object(capture.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], code, data)) as run):
                self.assertEqual(capture.main(), 1)
                run.assert_called_once_with(capture.CAPTURE, stdout=subprocess.PIPE, check=False)

    def test_passes_png_as_x11_clipboard_data_and_propagates_copy_failure(self):
        png = capture.PNG_HEADER + b"synthetic data" + capture.PNG_END
        for copy_result in (0, 1):
            with (self.subTest(copy_result=copy_result),
                  patch.dict(capture.os.environ, {"DISPLAY": ":99"}),
                  patch.object(capture.subprocess, "run", side_effect=[
                      subprocess.CompletedProcess([], 0, png),
                      subprocess.CompletedProcess([], copy_result),
                  ]) as run):
                self.assertEqual(capture.main(), copy_result)
                run.assert_called_with(
                    ("/usr/bin/xclip", "-selection", "clipboard", "-target",
                     "image/png", "-in", "-silent"), input=png, check=False)
