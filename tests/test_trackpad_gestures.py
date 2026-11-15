"""Gesture sequences and hardware scope; no input injection or desktop actions."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gestures", ROOT / "scripts/trackpad-gestures.py")
g = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(g)


class GestureTests(unittest.TestCase):
    def swipe(self, dx, dy=0, fingers=3, cancelled=False):
        reader = g.Recognizer()
        self.assertIsNone(reader.feed(g.BEGIN, 17, fingers))
        self.assertIsNone(reader.feed(g.UPDATE, 17, fingers, dx, dy))
        result = reader.feed(g.END, 17, fingers, cancelled=cancelled)
        self.assertIsNone(reader.feed(g.END, 17, fingers))
        return result

    def test_one_action_at_end_in_reference_direction(self):
        self.assertEqual(self.swipe(-150, 5), "left")
        self.assertEqual(self.swipe(150, -5), "right")
        self.assertEqual(g.COMMANDS["left"], "workspace next_on_output")
        self.assertEqual(g.COMMANDS["right"], "workspace prev_on_output")

    def test_ignore_other_fingers_vertical_diagonal_and_short(self):
        for fingers in (2, 4, 5):
            self.assertIsNone(self.swipe(200, fingers=fingers))
        for dx, dy in ((0, 200), (100, 100), (200, 100), (99, 0), (-99, 0)):
            self.assertIsNone(self.swipe(dx, dy))

    def test_cancelled_and_nonfinite_gestures_never_act(self):
        self.assertIsNone(self.swipe(-200, cancelled=True))
        for bad in (float("nan"), float("inf"), -float("inf")):
            self.assertIsNone(self.swipe(bad))

    def test_reversal_uses_final_displacement(self):
        reader = g.Recognizer()
        reader.feed(g.BEGIN, 17, 3)
        reader.feed(g.UPDATE, 17, 3, -200)
        reader.feed(g.UPDATE, 17, 3, 210)
        self.assertIsNone(reader.feed(g.END, 17, 3))

    def test_lost_begin_reset_and_changed_fingers_do_not_act(self):
        reader = g.Recognizer()
        self.assertIsNone(reader.feed(g.END, 17, 3, -200))
        reader.feed(g.BEGIN, 17, 3)
        reader.feed(g.UPDATE, 17, 3, -200)
        reader.reset()  # hierarchy change, including disconnect/reused X ID
        self.assertIsNone(reader.feed(g.END, 17, 3))
        reader.feed(g.BEGIN, 17, 3)
        reader.feed(g.UPDATE, 17, 4, -200)
        self.assertIsNone(reader.feed(g.END, 17, 3))

    def test_other_device_cannot_finish_or_extend_sequence(self):
        reader = g.Recognizer()
        reader.feed(g.BEGIN, 17, 3)
        reader.feed(g.UPDATE, 18, 3, -200)
        self.assertIsNone(reader.feed(g.END, 18, 3, -200))
        self.assertIsNone(reader.feed(g.END, 17, 3))

    def test_event_mask_includes_end_above_32_bits(self):
        mask = g.event_mask(17, (g.BEGIN, g.UPDATE, g.END))
        self.assertEqual(bytes(mask.mask[:mask.mask_len]), b"\0\0\0\xc0\x01")

    def test_hardware_requires_bus_vendor_product_driver_and_valid_node(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            device = root / "event6/device"
            (device / "id").mkdir(parents=True)
            (device / "device").mkdir()
            driver = root / "drivers/magicmouse"
            driver.mkdir(parents=True)
            (device / "device/driver").symlink_to(driver)
            for identity in g.IDENTITIES:
                for key, value in zip(("bustype", "vendor", "product"), identity):
                    (device / "id" / key).write_text(f"{value:04x}\n")
                self.assertTrue(g.is_trackpad("/dev/input/event6", root))
            (device / "id/product").write_text("1234\n")
            self.assertFalse(g.is_trackpad("/dev/input/event6", root))
            (device / "id/product").write_text("0265\n")
            (device / "device/driver").unlink()
            self.assertFalse(g.is_trackpad("/dev/input/event6", root))
            for node in ("event6", "/dev/input/event99", "/dev/input/../event6", "/dev/input/mouse1"):
                self.assertFalse(g.is_trackpad(node, root))

    def test_command_is_fixed_bounded_and_has_no_shell(self):
        with patch.object(g.subprocess, "run") as run:
            run.return_value.returncode = 0
            g.switch_workspace("left")
            args, kwargs = run.call_args
            self.assertEqual(args[0], ["i3-msg", "-q", "workspace next_on_output"])
            self.assertEqual(kwargs["timeout"], 2)
            self.assertNotIn("shell", kwargs)
            run.return_value.returncode = 1
            with self.assertRaises(RuntimeError):
                g.switch_workspace("right")
            run.side_effect = subprocess.TimeoutExpired("i3-msg", 2)
            with self.assertRaises(subprocess.TimeoutExpired):
                g.switch_workspace("left")

    def test_refresh_rebuilds_grabs_even_when_xid_is_reused(self):
        connection = object.__new__(g.XInput)
        connection.display, connection.root = 1, 2
        connection.targets = {17}
        connection.devices = Mock(return_value=({17}, {17}))
        connection.sync = Mock(return_value=True)
        connection.xi = Mock()
        connection.xi.XIGrabSwipeGestureBegin.return_value = 0
        connection.refresh()
        self.assertEqual(connection.targets, {17})
        self.assertEqual(connection.xi.XIUngrabSwipeGestureBegin.call_args.args[1], 17)
        self.assertEqual(connection.xi.XIGrabSwipeGestureBegin.call_args.args[1], 17)
        connection.devices.return_value = (set(), set())
        connection.xi.reset_mock()
        connection.refresh()
        self.assertEqual(connection.targets, set())
        connection.xi.XIUngrabSwipeGestureBegin.assert_not_called()
        connection.xi.XIGrabSwipeGestureBegin.assert_not_called()

    def test_hotplug_bad_device_is_recoverable_other_x_errors_stop(self):
        connection = object.__new__(g.XInput)
        connection.display, connection.bad_device = 1, 129
        connection.x = Mock()
        connection.errors = [129]
        self.assertFalse(connection.sync())
        self.assertEqual(connection.errors, [])
        connection.errors = [8]
        self.assertFalse(connection.sync(ignored=(8,)))
        connection.errors = [2]
        with self.assertRaises(RuntimeError):
            connection.sync()


if __name__ == "__main__":
    unittest.main()
