"""Offline checks for the Bluetooth trackpad speed menu and XInput writes."""
import importlib.util
import fnmatch
import json
import re
import shlex
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


class NativeInitialSpeedTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]
    tag = "bgh-magic-trackpad-2-bluetooth"

    def test_input_class_uses_only_the_next_preset_for_the_tagged_libinput_touchpad(self):
        text = (self.root / "config/bluetooth/90-bgh-magic-trackpad-speed.conf").read_text()
        directives = [parts for line in text.splitlines()
                      if (parts := shlex.split(line, comments=True))]
        default = next(i for i, (_, value) in enumerate(speed.PRESETS) if value is None)
        label, value = speed.PRESETS[default + 1]
        self.assertEqual((label, value), ("Slightly faster", .25))
        self.assertEqual(directives, [
            ["Section", "InputClass"],
            ["Identifier", "BGH Bluetooth Magic Trackpad 2 speed"],
            ["MatchTag", self.tag], ["MatchDriver", "libinput"],
            ["MatchIsTouchpad", "on"], ["Option", "AccelSpeed", str(value)],
            ["EndSection"]])

    def tagged(self, changes=None, tags=""):
        properties = {"SUBSYSTEM": "input", "KERNEL": "event7",
                      "KERNELS": "0005:004C:0265.0001", "DRIVERS": "magicmouse",
                      "ENV{ID_INPUT_TOUCHPAD}": "1", "ENV{ID_INPUT.tags}": tags}
        properties.update(changes or {})
        rules = (self.root / "config/bluetooth/72-bgh-magic-trackpad.rules").read_text()
        lines = [line for line in rules.splitlines()
                 if line.startswith("SUBSYSTEM") and "ENV{ID_INPUT.tags}" in line]
        self.assertEqual(len(lines), 2)
        for line in lines:
            clauses = re.findall(r'(ENV\{[^}]+\}|[A-Z_]+)(==|!=|=)"([^"]*)"', line)
            required = {"SUBSYSTEM": "input", "KERNEL": "event[0-9]*",
                        "KERNELS": "0005:004C:0265.*", "DRIVERS": "magicmouse",
                        "ENV{ID_INPUT_TOUCHPAD}": "1"}
            for key, value in required.items():
                self.assertIn((key, "==", value), clauses)
            actions = [(key, value) for key, op, value in clauses if op == "="]
            self.assertEqual([key for key, _ in actions], ["ENV{ID_INPUT.tags}"])
            matches = all(fnmatch.fnmatchcase(properties.get(key, ""), value) == (op == "==")
                          for key, op, value in clauses if op != "=")
            if matches:
                for key, value in actions:
                    properties[key] = value.replace("$env{ID_INPUT.tags}", properties[key])
        return properties["ENV{ID_INPUT.tags}"]

    def test_tag_requires_exact_bluetooth_hid_driver_and_touchpad_and_keeps_other_tags(self):
        self.assertEqual(self.tagged(), self.tag)
        self.assertEqual(self.tagged(tags="existing"), "existing," + self.tag)
        self.assertEqual(self.tagged(tags="existing," + self.tag), "existing," + self.tag)
        for changes in ({"SUBSYSTEM": "hidraw"}, {"KERNEL": "mouse0"},
                        {"KERNELS": "0003:05AC:0265.0001"},
                        {"KERNELS": "0005:004C:030D.0001"},
                        {"DRIVERS": "hid-generic"}, {"ENV{ID_INPUT_TOUCHPAD}": "0"}):
            with self.subTest(changes=changes):
                self.assertEqual(self.tagged(changes, tags="existing"), "existing")
        rules = (self.root / "config/bluetooth/72-bgh-magic-trackpad.rules").read_text()
        self.assertEqual(rules.count('TAG+="uaccess"'), 1)
        self.assertNotIn("RUN+=", rules)

    def test_manifest_declares_the_native_system_copy(self):
        entries = json.loads((self.root / "config/manifest.json").read_text())
        source = "config/bluetooth/90-bgh-magic-trackpad-speed.conf"
        entry = next(item for item in entries if item["source"] == source)
        self.assertEqual(entry, {"source": source,
                                "destination": "/etc/X11/xorg.conf.d/90-bgh-magic-trackpad-speed.conf",
                                "mode": 0o644})
