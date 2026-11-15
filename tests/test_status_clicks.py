"""Offline checks for signal levels and safe, specific bar click dispatch."""
import importlib.util
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

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


class CollapsibleMetricsTests(unittest.TestCase):
    def setUp(self):
        self.view = status.StatusView()
        self.blocks = [
            {"name": "read_file", "instance": "/fixture/weather.txt", "full_text": "~☾ 15°C"},
            {"name": "memory", "full_text": "37%"},
            {"name": "cpu_usage", "full_text": "2%"},
            {"name": "cpu_temperature", "full_text": "45°C"},
            {"name": "disk_info", "full_text": "40 GB"},
            {"name": "read_file", "instance": "/fixture/updates.txt", "full_text": "?"},
            {"name": "volume", "instance": "default.Master.0", "full_text": "unavailable"},
            {"name": "wireless", "instance": "wlp2s0", "full_text": "down"},
            {"name": "battery", "full_text": "No battery"},
            {"name": "tztime", "full_text": "Sun Nov 15 12:00"},
        ]
        self.traffic = Mock()
        self.traffic.sample.return_value = "↑2K ↓1K/s"
        self.event = {"name": "stats_toggle", "instance": "secondary", "button": 1}

    def test_compact_default_retains_essentials_and_unknown_blocks(self):
        self.blocks.append({"name": "future_block", "full_text": "unknown"})
        frame = self.view.update(self.blocks, self.traffic)
        self.assertEqual([b["name"] for b in frame],
                         ["read_file", "stats_toggle", "read_file", "volume",
                          "wireless", "battery", "tztime", "future_block"])
        self.assertEqual(frame[0]["full_text"], "~\ue32b 15°C")
        self.assertEqual(frame[2]["full_text"].split()[-1], "?")
        self.assertIn("No audio", frame[3]["full_text"])
        self.assertEqual(frame[5]["full_text"], "No battery")
        self.assertEqual(frame[1]["full_text"], "\uf054")

    def test_toggle_redraws_same_sample_without_io_or_mutating_input(self):
        original = deepcopy(self.blocks)
        compact = self.view.update(self.blocks, self.traffic)
        with patch.object(status.subprocess, "run") as run:
            for _ in range(3):
                self.assertTrue(status.handle_click(self.event, self.view))
                expanded = self.view.render()
                self.assertEqual([b["name"] for b in expanded],
                                 ["read_file", "traffic", "memory", "cpu_usage",
                                  "cpu_temperature", "disk_info", "stats_toggle",
                                  "read_file", "volume", "wireless", "battery", "tztime"])
                self.assertEqual(expanded[1]["full_text"], "↑2K ↓1K/s")
                self.assertEqual(expanded[6]["full_text"], "\uf053")
                self.assertTrue(status.handle_click(self.event, self.view))
                self.assertEqual(self.view.render(), compact)
        run.assert_not_called()
        self.traffic.sample.assert_called_once_with()
        self.assertEqual(self.blocks, original)

    def test_ticks_refresh_hidden_metrics_and_keep_expansion_state(self):
        self.view.update(self.blocks, self.traffic)
        self.blocks[1]["full_text"] = "50%"
        self.view.update(self.blocks, self.traffic)
        status.handle_click(self.event, self.view)
        self.assertIn("50%", next(b for b in self.view.render() if b["name"] == "memory")["full_text"])
        self.blocks[1]["full_text"] = "51%"
        frame = self.view.update(self.blocks, self.traffic)
        self.assertIn("51%", next(b for b in frame if b["name"] == "memory")["full_text"])
        self.assertEqual(self.traffic.sample.call_count, 3)

    def test_urgent_metrics_stay_visible_until_producer_clears_flag(self):
        for name in ("memory", "cpu_usage", "cpu_temperature", "disk_info"):
            block = next(b for b in self.blocks if b["name"] == name)
            block["urgent"] = True
            frame = self.view.update(self.blocks)
            self.assertTrue(next(b for b in frame if b["name"] == name)["urgent"])
            block["urgent"] = False
            self.assertNotIn(name, [b["name"] for b in self.view.update(self.blocks)])

    def test_toggle_requires_exact_identity_and_left_button(self):
        with patch.object(status.subprocess, "run") as run:
            for changed in ({"button": True}, {"button": "1"}, {"button": 3},
                            {"button": 4}, {"instance": "other"}, {"name": "other"}):
                self.assertFalse(status.handle_click(dict(self.event, **changed), self.view))
                self.assertFalse(self.view.expanded)
            self.assertFalse(status.handle_click(self.event))
        run.assert_not_called()

    def test_early_click_and_missing_blocks_keep_protocol_valid(self):
        self.assertIsNone(self.view.render())
        self.assertTrue(status.handle_click(self.event, self.view))
        self.assertIsNone(self.view.render())
        self.assertEqual([b["name"] for b in self.view.update([])], ["stats_toggle", "volume"])
        self.assertFalse(status.StatusView().expanded)


if __name__ == "__main__":
    unittest.main()
