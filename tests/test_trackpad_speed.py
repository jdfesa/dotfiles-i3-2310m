"""Offline checks for the Bluetooth trackpad speed menu and XInput writes."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock


spec = importlib.util.spec_from_file_location(
    "trackpad_speed", Path(__file__).resolve().parents[1] / "scripts/open-trackpad-speed.py")
speed = importlib.util.module_from_spec(spec)
spec.loader.exec_module(speed)


def output(text="", code=0):
    return subprocess.CompletedProcess([], code, stdout=text)


def props(node, value="0.000000", profile="1, 0, 0"):
    return (f'\tDevice Node (291):\t"{node}"\n'
            f"\tlibinput Accel Speed (317):\t{value}\n"
            "\tlibinput Accel Speed Default (318):\t-0.125000\n"
            f"\tlibinput Accel Profile Enabled (320):\t{profile}\n")


class TrackpadSpeedTests(unittest.TestCase):
    def make_event(self, root, name, bus, vendor="004c", product="0265", driver="magicmouse"):
        event = root / name
        identity = event / "device/id"
        identity.mkdir(parents=True)
        for key, value in (("bustype", bus), ("vendor", vendor), ("product", product)):
            (identity / key).write_text(value + "\n")
        (event / "device/device" / driver).mkdir(parents=True)
        (event / "device/device/driver").symlink_to(driver, target_is_directory=True)
        return event

    def test_matches_only_native_bluetooth_trackpad_not_an_internal_or_usb_device(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            expected = self.make_event(root, "event7", "0005")
            self.make_event(root, "event5", "0003", vendor="05ac")  # Wired Apple trackpad.
            self.make_event(root, "event1", "0011", vendor="0002", product="0007")
            self.make_event(root, "event8", "0005", driver="hid-generic")
            command = Mock(side_effect=[output("12\n13\n14\n15\n"),
                output(props("/dev/input/event1")), output(props("/dev/input/event5")),
                output(props("/dev/input/event7")), output(props("/dev/input/event8"))])
            self.assertEqual(speed.find_device(root, command),
                             speed.Device("14", "/dev/input/event7", expected.resolve(), 0, -.125))

    def test_no_write_target_on_disconnect_custom_profile_invalid_value_or_ambiguity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            command = Mock()
            self.assertIsNone(speed.find_device(root, command))
            command.assert_not_called()
            self.make_event(root, "event7", "0005")
            for invalid in (props("/dev/input/event7", profile="0, 0, 1"),
                            props("/dev/input/event7", value="nan")):
                with self.subTest(invalid=invalid):
                    command = Mock(side_effect=[output("12\n"), output(invalid)])
                    self.assertIsNone(speed.find_device(root, command))
            command = Mock(side_effect=[output("12\n13\n"), output(props("/dev/input/event7")),
                                        output(props("/dev/input/event7"))])
            self.assertIsNone(speed.find_device(root, command))

    def test_speed_rows_prefer_the_driver_default_and_keep_fixed_presets(self):
        device = speed.Device("14", "/dev/input/event7", Path("/fixture/trackpad"), -.125, -.125)
        rows, selected = speed.speed_rows(device)
        self.assertEqual(rows[selected], ("Default", -.125))
        self.assertEqual([value for _, value in rows], [-1, -.5, -.25, -.125, .25, .5, 1])
        self.assertEqual(speed.speed_rows(device._replace(speed=.51))[1], 5)

    def test_confirm_closes_on_success_and_shows_inline_error_on_failure(self):
        window, message, device = Mock(), Mock(), Mock()
        fail = Mock(return_value=False)
        self.assertFalse(speed.confirm_speed(window, message, device, .25, fail))
        fail.assert_called_once_with(device, .25)
        window.destroy.assert_not_called()
        message.set_text.assert_called_once()
        apply = Mock(return_value=True)
        self.assertTrue(speed.confirm_speed(window, message, device, .25, apply))
        apply.assert_called_once_with(device, .25)
        window.destroy.assert_called_once_with()

    def test_applies_only_speed_and_revalidates_after_the_menu(self):
        device = speed.Device("14", "/dev/input/event7", Path("/fixture/trackpad"), 0, 0)
        command = Mock(return_value=output())
        for found, value in ((None, .5), (device._replace(sysfs=Path("/fixture/new")), .5),
                             (device._replace(speed=-.25), .5), (device, 1.1)):
            self.assertFalse(speed.apply_speed(device, value, Mock(return_value=found), command))
        self.assertTrue(speed.apply_speed(device, 0, Mock(return_value=device), command))
        command.assert_not_called()
        self.assertTrue(speed.apply_speed(device, .5, Mock(return_value=device), command))
        command.assert_called_once_with("set-prop", "14", "libinput Accel Speed", "0.500000")
