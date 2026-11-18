"""Validate clipboard behavior using only synthetic capture data."""

import importlib.util
import io
import json
from pathlib import Path
import stat
import subprocess
import tempfile
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

    def test_cancel_or_incomplete_output_never_saves_or_copies(self):
        cases = ((1, b"", 1), (1, capture.PNG_HEADER + capture.PNG_END, 1),
                 (0, b"", 0), (0, capture.PNG_HEADER, 1))
        for code, data, status in cases:
            with (self.subTest(code=code, data=data),
                  patch.dict(capture.os.environ, {"DISPLAY": ":99"}, clear=True),
                  patch("sys.stderr", new_callable=io.StringIO),
                  patch.object(capture, "save_png") as save,
                  patch.object(capture.subprocess, "run",
                               return_value=subprocess.CompletedProcess([], code, data)) as run):
                self.assertEqual(capture.main(), status)
                run.assert_called_once_with(("/usr/bin/flameshot", "gui", "--raw"),
                                            stdout=subprocess.PIPE, check=False,
                                            env={"DISPLAY": ":99", "QT_QPA_PLATFORM": "xcb"})
                save.assert_not_called()

    def test_accept_saves_the_final_png_and_copies_it(self):
        png = capture.PNG_HEADER + b"synthetic data" + capture.PNG_END
        for copy_result in (0, 1):
            with (self.subTest(copy_result=copy_result), tempfile.TemporaryDirectory() as home,
                  patch.object(capture.Path, "home", return_value=Path(home)),
                  patch("sys.stdout", new_callable=io.StringIO),
                  patch("sys.stderr", new_callable=io.StringIO),
                  patch.dict(capture.os.environ, {"DISPLAY": ":99"}),
                  patch.object(capture.subprocess, "run", side_effect=[
                      subprocess.CompletedProcess([], 0, png),
                      subprocess.CompletedProcess([], copy_result),
                  ]) as run):
                self.assertEqual(capture.main(), copy_result)
                run.assert_called_with(
                    ("/usr/bin/xclip", "-selection", "clipboard", "-target",
                     "image/png", "-in", "-silent"), input=png,
                    stdout=subprocess.DEVNULL, check=False)
                folder = Path(home) / "Pictures/Screenshots"
                files = list(folder.iterdir())
                self.assertEqual(len(files), 1)
                self.assertRegex(files[0].name, r"^screenshot-.*\.png$")
                self.assertEqual(files[0].read_bytes(), png)
                self.assertEqual(stat.S_IMODE(files[0].stat().st_mode), 0o600)

    def test_save_failure_keeps_the_clipboard(self):
        png = capture.PNG_HEADER + b"synthetic data" + capture.PNG_END
        with (patch.dict(capture.os.environ, {"DISPLAY": ":99"}),
              patch("sys.stderr", new_callable=io.StringIO),
              patch.object(capture, "save_png", side_effect=PermissionError),
              patch.object(capture.subprocess, "run",
                           return_value=subprocess.CompletedProcess([], 0, png)) as run):
            self.assertEqual(capture.main(), 1)
        self.assertEqual(run.call_count, 1)
