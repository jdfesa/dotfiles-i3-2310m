"""Exercise the EC write guards using temporary files; never touch real hardware."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wifi_radio", ROOT / "scripts/enable-wifi-radio.py")
WIFI = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(WIFI)


class WifiRadioTests(unittest.TestCase):
    def setUp(self):
        self.folder = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.support = self.folder / "support"
        self.support.write_text("N\n")
        self.enterContext(patch.object(WIFI, "RUNTIME", self.folder))
        self.enterContext(patch.object(WIFI, "WRITE_SUPPORT", self.support))
        original_fstat = os.fstat

        def root_owner(fd):
            info = list(original_fstat(fd))
            info[4] = 0  # Only fixture ownership is simulated; all IO stays in /tmp.
            return os.stat_result(info)

        self.enterContext(patch.object(WIFI.os, "fstat", side_effect=root_owner))

    def test_one_exact_write_and_guard_restoration(self):
        def write(fd, value):
            self.assertEqual((fd, value), (123, 0x80))
            self.assertEqual(self.support.read_text(), "Y\n")
            self.assertEqual((self.folder / "write-guard").read_bytes(), b"N\n")

        with patch.object(WIFI, "read_byte", return_value=0), \
                patch.object(WIFI, "radio_state", return_value=(0, 1)), \
                patch.object(WIFI, "write_byte", side_effect=write) as operation:
            WIFI.enable_byte(123)
        operation.assert_called_once_with(123, 0x80)
        self.assertEqual(self.support.read_text(), "N\n")
        self.assertFalse((self.folder / "write-guard").exists())

    def test_unknown_flags_and_soft_block_never_write(self):
        for value, radio in ((1, (0, 1)), (0x81, (0, 1)), (0, (1, 1)), (0, (0, 0))):
            with self.subTest(value=value, radio=radio), \
                    patch.object(WIFI, "read_byte", return_value=value), \
                    patch.object(WIFI, "radio_state", return_value=radio), \
                    patch.object(WIFI, "write_byte") as operation:
                with self.assertRaises(ValueError):
                    WIFI.enable_byte(123)
                operation.assert_not_called()
                self.assertEqual(self.support.read_text(), "N\n")
                self.assertFalse((self.folder / "write-guard").exists())

    def test_changed_state_aborts_and_restores_guard(self):
        with patch.object(WIFI, "read_byte", side_effect=[0, 0x20]), \
                patch.object(WIFI, "radio_state", return_value=(0, 1)), \
                patch.object(WIFI, "write_byte") as operation:
            with self.assertRaises(ValueError):
                WIFI.enable_byte(123)
        operation.assert_not_called()
        self.assertEqual(self.support.read_text(), "N\n")
        self.assertFalse((self.folder / "write-guard").exists())

    def test_write_failure_or_interruption_restores_guard(self):
        for error in (OSError("fixture IO failure"), RuntimeError("fixture interruption")):
            with self.subTest(error=error), patch.object(WIFI, "read_byte", return_value=0), \
                    patch.object(WIFI, "radio_state", return_value=(0, 1)), \
                    patch.object(WIFI, "write_byte", side_effect=error):
                with self.assertRaises(type(error)):
                    WIFI.enable_byte(123)
                self.assertEqual(self.support.read_text(), "N\n")
                self.assertFalse((self.folder / "write-guard").exists())

    def test_existing_write_permission_is_not_claimed(self):
        self.support.write_text("Y\n")
        with patch.object(WIFI, "write_byte") as operation:
            with self.assertRaises(ValueError):
                WIFI.enable_byte(123)
        operation.assert_not_called()
        self.assertEqual(self.support.read_text(), "Y\n")

    def test_stop_post_recovers_only_with_its_own_marker(self):
        self.support.write_text("Y\n")
        WIFI.restore_guard()
        self.assertEqual(self.support.read_text(), "Y\n")
        marker = self.folder / "write-guard"
        marker.write_bytes(b"N\n")
        marker.chmod(0o600)
        WIFI.restore_guard()
        self.assertEqual(self.support.read_text(), "N\n")
        self.assertFalse(marker.exists())

    def test_recovery_refuses_a_symlink_or_invalid_marker(self):
        marker = self.folder / "write-guard"
        marker.symlink_to(self.support)
        with self.assertRaises(OSError):
            WIFI.restore_guard()
        marker.unlink()
        marker.write_bytes(b"?\n")
        marker.chmod(0o600)
        with self.assertRaises(ValueError):
            WIFI.restore_guard()

    def test_already_enabled_is_idempotent_and_inspection_never_writes(self):
        for apply, initial, value in ((True, (0, 0), 0x80), (False, (0, 1), 0)):
            with self.subTest(apply=apply), patch.object(WIFI, "verify_hardware"), \
                    patch.object(WIFI, "wait_for_radio", return_value=initial), \
                    patch.object(WIFI.os, "open", return_value=123), \
                    patch.object(WIFI.os, "close"), patch.object(WIFI, "read_byte", return_value=value), \
                    patch.object(WIFI, "enable_byte") as operation:
                WIFI.inspect_or_enable(apply, 0)
                operation.assert_not_called()

    def test_firmware_mismatch_prevents_access_to_ec(self):
        def dmi_value(path):
            return WIFI.DMI[path.name]

        with patch.object(Path, "read_text", autospec=True, side_effect=dmi_value), \
                patch.object(Path, "read_bytes", return_value=b"different firmware"), \
                patch.object(WIFI.os, "open") as opened:
            with self.assertRaises(ValueError):
                WIFI.inspect_or_enable(True, 0)
            opened.assert_not_called()

    def test_radio_discovery_has_a_fixed_deadline(self):
        with patch.object(WIFI, "radio_state", side_effect=ValueError("No radio")) as state, \
                patch.object(WIFI.time, "sleep") as sleep:
            with self.assertRaises(ValueError):
                WIFI.wait_for_radio(10)
            self.assertEqual(state.call_count, 11)
            self.assertEqual(sleep.call_count, 10)


if __name__ == "__main__":
    unittest.main()
