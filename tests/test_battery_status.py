"""Native i3status battery fixtures; never access or change real power supplies."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("battery_status", ROOT / "scripts/status-clicks.py")
status = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(status)


@unittest.skipUnless(shutil.which("i3status"), "native i3status is required")
class NativeBatteryTests(unittest.TestCase):
    def test_native_battery_states_reach_the_icon_adapter(self):
        native = (ROOT / "config/i3status-config").read_text()
        section = re.search(r"battery all \{\n(.*?)\n\}", native, re.S).group(1)
        with tempfile.TemporaryDirectory(prefix="bgh-battery-fixture-") as tmp:
            root = Path(tmp)
            battery = root / "BAT0"
            battery.mkdir()
            config = root / "i3status.conf"
            config.write_text('general {\n output_format = "i3bar"\n interval = 10\n}\n'
                              'order += "battery all"\nbattery all {\n' + section +
                              '\n path = "' + str(root / 'BAT%d/uevent') + '"\n}\n')
            cases = [(None, 0, "absent", status.BATTERY_ABSENT),
                     ("Charging", 65, "charging 65%", status.BATTERY_CHARGING_LEVELS[6]),
                     ("Discharging", 65, "discharging 65%", status.BATTERY_LEVELS[6]),
                     ("Full", 100, "full 100%", status.BATTERY_FULL),
                     ("Not charging", 65, "idle 65%", status.BATTERY_LEVELS[6]),
                     ("Unknown", 65, "unknown 65%", status.BATTERY_UNKNOWN),
                     ("Discharging", 0, "discharging 0%", status.BATTERY_LEVELS[0])]
            for state, capacity, expected, icon in cases:
                with self.subTest(state=state, capacity=capacity):
                    if state is not None:
                        (battery / "uevent").write_text(
                            "POWER_SUPPLY_NAME=BAT0\nPOWER_SUPPLY_PRESENT=1\n"
                            f"POWER_SUPPLY_STATUS={state}\n"
                            "POWER_SUPPLY_ENERGY_FULL_DESIGN=100000\n"
                            "POWER_SUPPLY_ENERGY_FULL=100000\n"
                            f"POWER_SUPPLY_ENERGY_NOW={capacity * 1000}\n"
                            "POWER_SUPPLY_POWER_NOW=10000\n")
                    result = subprocess.run(["i3status", "-c", str(config), "--run-once"],
                                            capture_output=True, text=True, timeout=3,
                                            env=dict(os.environ, LC_ALL="C"))
                    self.assertEqual(result.returncode, 0, result.stderr)
                    block = json.loads(result.stdout.splitlines()[-1])[0]
                    self.assertEqual(block["full_text"], expected)
                    rendered = status.adapt_status([block])[0]
                    self.assertIn(icon, rendered["full_text"])
                    self.assertNotIn("No battery", rendered["full_text"])


if __name__ == "__main__":
    unittest.main()
