"""Backlight fixtures and i3bar click dispatch without real writes."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


brightness = load("screen-brightness")
status = load("status-clicks")


class BacklightTests(unittest.TestCase):
    def setUp(self):
        folder = self.enterContext(tempfile.TemporaryDirectory())
        self.device = Path(folder)
        (self.device / "type").write_text("firmware\n")
        (self.device / "max_brightness").write_text("7\n")
        self.actual = self.device / "actual_brightness"
        self.actual.write_text("4\n")

    def test_native_steps_and_readback(self):
        self.assertEqual(brightness.read_level(self.device), (4, 7))
        self.assertEqual(brightness.percentage(4, 7), 57)
        self.assertEqual(brightness.percentage(1, 7), 14)
        request = Mock(side_effect=lambda target: self.actual.write_text(str(target)))
        self.assertEqual(brightness.write_level(3, 7, request, self.device), 43)
        request.assert_called_once_with(3)

    def test_default_maps_to_three_and_skips_an_already_matching_level(self):
        request = Mock(side_effect=lambda target: self.actual.write_text(str(target)))
        brightness.set_percentage(43, request, self.device)
        brightness.set_percentage(43, request, self.device)
        request.assert_called_once_with(3)

    def test_tiny_percentage_maps_to_nonzero_level_and_invalid_input_is_rejected(self):
        request = Mock(side_effect=lambda target: self.actual.write_text(str(target)))
        for invalid in (0, -1, 101, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                brightness.set_percentage(invalid, request, self.device)
        request.assert_not_called()
        brightness.set_percentage(1, request, self.device)
        request.assert_called_once_with(1)

    def test_never_requests_zero_or_out_of_range_or_changed_device(self):
        request = Mock()
        for level, remembered_max in ((0, 7), (-1, 7), (True, 7), (3.0, 7), (8, 7), (3, 9)):
            with self.subTest(level=level, remembered_max=remembered_max), self.assertRaises(ValueError):
                brightness.write_level(level, remembered_max, request, self.device)
        (self.device / "type").write_text("raw")
        with self.assertRaises(ValueError):
            brightness.write_level(3, 7, request, self.device)
        request.assert_not_called()

    def test_actual_zero_is_valid_but_invalid_reads_are_not(self):
        self.actual.write_text("0")
        self.assertEqual(brightness.percentage(*brightness.read_level(self.device)), 0)
        for invalid in ("8", "-1", "unknown"):
            self.actual.write_text(invalid)
            with self.assertRaises(ValueError):
                brightness.read_level(self.device)
        self.actual.unlink()
        with self.assertRaises(OSError):
            brightness.read_level(self.device)

    def test_post_write_level_must_match(self):
        request = Mock()
        with self.assertRaises(OSError):
            brightness.write_level(3, 7, request, self.device)
        request.assert_called_once_with(3)

    def test_missing_or_bad_telemetry_is_unknown(self):
        for error in (OSError(), ValueError()):
            with patch.object(brightness, "read_level", side_effect=error):
                self.assertIsNone(brightness.sample())


class BrightnessBlockTests(unittest.TestCase):
    def test_i3_sets_default_only_on_initial_startup(self):
        config = (SCRIPTS.parent / "config/i3-config").read_text()
        commands = [line for line in config.splitlines() if "~/dotfiles-i3-2310m/scripts/screen-brightness.py" in line]
        self.assertEqual(commands, ["exec --no-startup-id ~/dotfiles-i3-2310m/scripts/screen-brightness.py --set-percent 43"])

    def test_block_stays_visible_without_resampling_on_toggle(self):
        source = Mock(side_effect=(57, None))
        view = status.StatusView()
        blocks = [{"name": "memory", "full_text": "40%"}]
        frame = view.update(blocks, brightness=source)
        self.assertEqual([b["name"] for b in frame], ["stats_toggle", "screen_brightness", "volume"])
        self.assertTrue(frame[1]["full_text"].endswith("57%"))
        view.expanded = True
        self.assertIn(frame[1], view.render())
        source.assert_called_once()
        frame = view.update(blocks, brightness=source)
        block = next(b for b in frame if b["name"] == "screen_brightness")
        self.assertTrue(block["full_text"].endswith(" ?"))
        self.assertEqual(block["markup"], "pango")

    def test_only_exact_left_click_dispatches_the_anchored_panel(self):
        event = dict(name="screen_brightness", instance="internal-display", button=1,
                     x=100, y=12, relative_x=5, relative_y=12, width=40, height=24)
        with patch.object(status.subprocess, "run") as run:
            for other in (dict(event, button=4), dict(event, button=True),
                          dict(event, instance="keyboard"), dict(event, name="wireless")):
                status.handle_click(other)
            run.assert_not_called()
            status.handle_click(event)
            self.assertEqual(run.call_args.args[0],
                             ["i3-msg", f"exec --no-startup-id {SCRIPTS / 'status-panel.py'} brightness 115 24"])
