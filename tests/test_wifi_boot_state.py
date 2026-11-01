"""Bound the temporary diagnostic unit; no service or radio actions run."""
import configparser
from pathlib import Path
import unittest

UNIT = Path(__file__).resolve().parents[1] / "config/wifi-boot-state.service"


class WifiBootStateTests(unittest.TestCase):
    def test_runs_once_without_privilege_or_restart(self):
        config = configparser.ConfigParser(strict=False)
        config.read(UNIT)
        self.assertEqual(config["Service"]["Type"], "oneshot")
        self.assertEqual(config["Service"]["User"], "jd")
        self.assertEqual(config["Service"]["Restart"], "no")
        self.assertEqual(config["Service"]["TimeoutStartSec"], "10s")
        self.assertEqual(config["Service"]["NoNewPrivileges"], "yes")

    def test_only_reads_radio_state_not_keys_or_secrets(self):
        commands = [line for line in UNIT.read_text().splitlines() if line.startswith("Exec")]
        self.assertEqual(commands, [
            "ExecStart=/usr/sbin/rfkill --output ID,TYPE,DEVICE,SOFT,HARD list",
            "ExecStart=/usr/bin/nmcli radio",
        ])

    def test_does_not_delay_or_restart_networkmanager(self):
        config = configparser.ConfigParser(strict=False)
        config.read(UNIT)
        self.assertEqual(dict(config["Unit"]), {
            "description": "Record Wi-Fi block state once at boot (temporary diagnostic)",
            "after": "NetworkManager.service",
        })
        self.assertEqual(config["Install"]["WantedBy"], "multi-user.target")


if __name__ == "__main__":
    unittest.main()
