"""Bluetooth hotplug, bounded battery queries and truthful bar state, offline."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bluetooth = load("bluetooth_status", "scripts/bluetooth-status.py")
status = load("bluetooth_bar", "scripts/status-clicks.py")


class BluetoothTests(unittest.TestCase):
    def test_native_power_property_distinguishes_off_absent_and_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = bluetooth.BlueZ(root)
            self.assertEqual(source.sample(), "absent")
            (root / "hci0").mkdir()
            source.library = Mock()
            source.bus = bluetooth.C.c_void_p(1)

            def respond(*args):
                bluetooth.C.cast(args[-1], bluetooth.C.POINTER(bluetooth.C.c_int))[0] = 1
                return 0

            source.library.sd_bus_get_property_trivial.side_effect = respond
            self.assertEqual(source.sample(), "on")
            source.library.sd_bus_get_property_trivial.side_effect = None
            source.library.sd_bus_get_property_trivial.return_value = 0
            self.assertEqual(source.sample(), "off")
            source.library.sd_bus_get_property_trivial.return_value = -5
            self.assertEqual(source.sample(), "unknown")
            source.library.sd_bus_flush_close_unref.assert_called_once()

    def test_discovery_uses_exact_hardware_and_driver_with_personalized_name(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for index, (driver, identity) in enumerate([
                    ("hid-generic", "0005:0000004C:00000265"),
                    ("magicmouse", "0003:000005AC:00000265"),
                    ("magicmouse", "0005:0000004C:00000269"),
                    ("magicmouse", "0005:0000004C:00000265")]):
                device = root / f"hidraw{index}/device"
                device.mkdir(parents=True)
                (device / "uevent").write_text(
                    f"DRIVER={driver}\nHID_ID={identity}\nHID_NAME=Personal device\n")
            self.assertEqual(bluetooth.find_trackpad(root),
                             ("hidraw3", str(root / "hidraw3/device")))
            (root / "hidraw3/device/uevent").unlink()
            self.assertIsNone(bluetooth.find_trackpad(root))

    def make_monitor(self):
        self.now = 0
        self.query = Mock(return_value="connected")
        self.finder = Mock(return_value=("hidraw2", "/fixture/hid/one"))
        self.worker = Mock()
        self.worker.poll.return_value = None
        self.worker.communicate.return_value = (b"[99, false]\n", None)
        return bluetooth.BluetoothStatus(self.query, self.finder, clock=lambda: self.now)

    def test_reads_once_per_five_minutes_and_reaps_child(self):
        monitor = self.make_monitor()
        with patch.object(bluetooth.subprocess, "Popen", return_value=self.worker) as spawn:
            self.assertIsNone(monitor.sample()["percentage"])
            self.worker.poll.return_value = 0
            self.now = 10
            state = monitor.sample()
            self.assertEqual(state["percentage"], 99)
            self.assertFalse(state["stale"])
            for self.now in (20, 100, 299):
                self.assertEqual(monitor.sample()["percentage"], 99)
            spawn.assert_called_once()
            self.assertEqual(spawn.call_args.args[0][-2:], ["--read-battery", "hidraw2"])
            self.now = 300
            monitor.sample()
            self.assertEqual(spawn.call_count, 2)
            monitor.close()
            self.worker.communicate.assert_called()

    def test_missing_or_powered_off_adapter_does_not_query_hid(self):
        for adapter in ("absent", "off"):
            monitor = self.make_monitor()
            self.query.return_value = adapter
            with patch.object(bluetooth.subprocess, "Popen") as spawn:
                state = monitor.sample()
            self.assertFalse(state["connected"])
            self.assertIsNone(state["percentage"])
            self.finder.assert_not_called()
            spawn.assert_not_called()

    def test_disconnect_kills_owned_reader_and_reconnect_discards_old_charge(self):
        monitor = self.make_monitor()
        with patch.object(bluetooth.subprocess, "Popen", return_value=self.worker):
            monitor.sample()
            self.finder.return_value = None
            self.assertFalse(monitor.sample()["connected"])
            self.worker.kill.assert_called_once()
            self.worker.communicate.assert_called_once()
            self.finder.return_value = ("hidraw2", "/fixture/hid/new")
            self.assertIsNone(monitor.sample()["percentage"])
            monitor.close()

    def test_failed_or_malformed_read_is_unknown_never_false_zero(self):
        for output in (b"null", b"bad JSON", b"[101, false]", b"[false, false]", b"[50, 1]"):
            monitor = self.make_monitor()
            self.worker.communicate.return_value = (output, None)
            with patch.object(bluetooth.subprocess, "Popen", return_value=self.worker):
                monitor.sample()
                self.worker.poll.return_value = 0
                self.now = 10
                self.assertIsNone(monitor.sample()["percentage"])

    def test_read_timeout_reaps_child_without_immediate_retry(self):
        monitor = self.make_monitor()
        with patch.object(bluetooth.subprocess, "Popen", return_value=self.worker) as spawn:
            monitor.sample()
            self.now = 20
            self.assertIsNone(monitor.sample()["percentage"])
            self.worker.kill.assert_called_once()
            self.assertIsNone(monitor.worker)
            spawn.assert_called_once()

    def test_failed_refresh_marks_cached_value_then_expires_it(self):
        monitor = self.make_monitor()
        with patch.object(bluetooth.subprocess, "Popen", return_value=self.worker):
            monitor.sample()
            self.worker.poll.return_value = 0
            self.now = 10
            monitor.sample()
            self.now = 300
            monitor.sample()
            self.worker.communicate.return_value = (b"null", None)
            self.now = 310
            state = monitor.sample()
            self.assertEqual(state["percentage"], 99)
            self.assertTrue(state["stale"])
            self.now = 611
            self.assertIsNone(monitor.sample()["percentage"])
            monitor.close()

    def test_compact_bar_retains_both_icons_and_click_redraw_does_not_sample(self):
        peripherals = Mock()
        peripherals.sample.return_value = dict(adapter="connected", connected=True,
                                               percentage=99, charging=False, stale=False)
        view = status.StatusView()
        frame = view.update([{"name": "tztime", "full_text": "12:00"}], peripherals=peripherals)
        self.assertIn("bluetooth", [block["name"] for block in frame])
        trackpad = next(block for block in frame if block["name"] == "trackpad")
        self.assertIn("99%", trackpad["full_text"])
        self.assertIn("\U000f07f8", trackpad["full_text"])
        self.assertEqual(trackpad["markup"], "pango")
        status.handle_click({"name": "stats_toggle", "instance": "secondary", "button": 1}, view)
        view.render()
        peripherals.sample.assert_called_once()

    def test_low_battery_urgency_requires_fresh_confirmed_reading(self):
        for value, charging, stale, urgent in ((0, False, False, True), (15, False, False, True),
                                              (16, False, False, False), (None, False, False, False),
                                              (10, True, False, False), (10, False, True, False)):
            blocks = status.peripheral_blocks(dict(adapter="on", connected=True,
                                                    percentage=value, charging=charging, stale=stale))
            self.assertEqual(blocks[1]["urgent"], urgent)

    def test_vendor_sources_and_license_match_reviewed_commit(self):
        expected = {"magic-trackpad-battery": "8cae4c35cefdb45439a40ba67a382d251975cd88c6344e802532bac62325714d",
                    "LICENSE": "b93452a9677590d612fec93c243ae5eefb2966e83b20a5911c670fdf9423bbed"}
        for name, digest in expected.items():
            self.assertEqual(hashlib.sha256((ROOT / "config/bluetooth/vendor" / name).read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
