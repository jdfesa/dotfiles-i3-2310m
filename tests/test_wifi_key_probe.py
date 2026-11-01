"""Privacy filtering only; these tests never open real input devices."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("wifi_probe", Path(__file__).resolve().parents[1] / "tools/probe-wifi-keys.py")
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


class WifiKeyProbeTests(unittest.TestCase):
    def test_ordinary_keys_and_raw_scancodes_are_not_emitted(self):
        self.assertIsNone(probe.selected_key(1, 30, 1))  # KEY_A
        self.assertIsNone(probe.selected_key(1, 57, 1))  # Space
        self.assertIsNone(probe.selected_key(4, 4, 0x1E))  # MSC_SCAN

    def test_only_explicit_fn_and_radio_keys_are_reported(self):
        self.assertEqual(set(probe.KEYS), {87, 238, 247, 464, 476})
        self.assertEqual(probe.selected_key(1, 87, 1), {
            "kind": "key", "key": "KEY_F11", "code": 87, "value": 1})


if __name__ == "__main__":
    unittest.main()
