"""Offline checks for signal levels and safe, specific bar click dispatch."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("status_clicks", Path(__file__).resolve().parents[1] / "scripts/status-clicks.py")
status = importlib.util.module_from_spec(spec)
spec.loader.exec_module(status)


class StatusTests(unittest.TestCase):
    def test_quality_to_signal_levels(self):
        for quality, level in (("down", 0), ("0%", 1), ("25%", 1), ("26%", 2),
                               ("50%", 2), ("60%", 3), ("75%", 3), ("76%", 4), ("100%", 4)):
            with self.subTest(quality=quality):
                blocks = status.adapt_status([{"name": "wireless", "instance": "wlp2s0", "full_text": quality}])
                wifi = next(block for block in blocks if block["name"] == "wireless")
                self.assertIn(chr(0xE000 + level), wifi["full_text"])
                self.assertNotIn(quality, wifi["full_text"])
                self.assertEqual(wifi["markup"], "pango")

    def test_absent_battery_stays_english(self):
        blocks = [{"name": "battery", "full_text": "No battery"}]
        self.assertEqual(status.adapt_status(blocks)[0]["full_text"], "No battery")

    def test_weather_icon_replaced_without_location(self):
        block = {"name": "read_file", "instance": "/home/jd/.cache/i3/weather.txt", "full_text": "~☾ 15°C"}
        self.assertEqual(status.adapt_status([block])[0]["full_text"], "~\ue32b 15°C")

    def test_volume_and_missing_hardware(self):
        for text, expected in (("80%", "\uf028"), ("30%", "\uf027"), ("0%", "\uf026"),
                               ("muted 20%", "\ueee8"), ("no mixer", "No audio")):
            with self.subTest(text=text):
                block = {"name": "volume", "full_text": text}
                self.assertIn(expected, status.adapt_status([block])[0]["full_text"])

    def test_traffic_averages_and_counter_reset(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "rx_bytes").write_text("100")
            (root / "tx_bytes").write_text("200")
            traffic = status.Traffic(root, clock=lambda: 10)
            self.assertEqual(traffic.sample(), "↑-- ↓--")
            (root / "rx_bytes").write_text(str(100 + 10240))
            (root / "tx_bytes").write_text(str(200 + 20480))
            traffic.clock = lambda: 20
            self.assertEqual(traffic.sample(), "↑2K ↓1K/s")
            (root / "rx_bytes").write_text("0")
            traffic.clock = lambda: 30
            self.assertEqual(traffic.sample(), "↑-- ↓--")

    def test_missing_traffic_is_unknown_not_zero(self):
        traffic = status.Traffic(Path("/not/an/interface"))
        self.assertEqual(traffic.sample(), "↑-- ↓--")

    def test_dynamic_label_is_escaped(self):
        result = status.adapt_status([{"name": "memory", "full_text": "<unsafe>"}])
        self.assertIn("&lt;unsafe&gt;", result[0]["full_text"])

    def test_wifi_click_launches_fixed_helper(self):
        with patch.object(status.subprocess, "run") as run:
            status.handle_click({"name": "wireless", "instance": "wlp2s0", "button": 1,
                                 "irrelevant": "'; touch /tmp/unsafe"})
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["i3-msg", "exec --no-startup-id ~/scripts/open-networks.sh"])
        self.assertTrue(run.call_args.kwargs["check"])
        self.assertNotIn("shell", run.call_args.kwargs)

    def test_native_volume_instance_click(self):
        with patch.object(status.subprocess, "run") as run:
            status.handle_click({"name": "volume", "instance": "default.Master.0", "button": 1})
        self.assertEqual(run.call_args.args[0], ["i3-msg", "exec --no-startup-id ~/scripts/open-mixer.sh"])

    def test_missing_volume_block_is_honest(self):
        blocks = status.adapt_status([{"name": "wireless", "instance": "wlp2s0", "full_text": "60%"}])
        self.assertEqual(blocks[0]["name"], "volume")
        self.assertIn("No audio", blocks[0]["full_text"])

    def test_unrelated_or_invalid_click_ignored(self):
        with patch.object(status.subprocess, "run") as run:
            for event in ({"name": "battery", "button": 1},
                          {"name": "wireless", "instance": "wlp2s0", "button": 3},
                          {"name": "wireless", "instance": "wrong", "button": 1},
                          {"name": "wireless", "instance": "wlp2s0", "button": True}):
                status.handle_click(event)
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
