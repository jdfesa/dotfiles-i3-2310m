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

    def test_absent_battery_is_an_icon_without_a_fake_percentage(self):
        blocks = [{"name": "battery", "full_text": "absent"}]
        block = status.adapt_status(blocks)[0]
        self.assertIn(status.BATTERY_ABSENT, block["full_text"])
        self.assertNotIn("%", block["full_text"])
        self.assertNotIn("No battery", block["full_text"])
        self.assertEqual((block["min_width"], block["align"]), (24, "center"))

    def test_battery_states_keep_native_status_separate_from_percentage(self):
        for text, icon in (("charging 65%", status.BATTERY_CHARGING_LEVELS[6]),
                           ("charging 100%", status.BATTERY_CHARGING_LEVELS[10]),
                           ("full 100%", status.BATTERY_FULL),
                           ("discharging 100%", status.BATTERY_LEVELS[10]),
                           ("discharging 65%", status.BATTERY_LEVELS[6]),
                           ("idle 65%", status.BATTERY_LEVELS[6] + " " + status.BATTERY_IDLE_MARK),
                           ("discharging 0%", status.BATTERY_LEVELS[0]),
                           ("unknown 65%", status.BATTERY_UNKNOWN)):
            with self.subTest(text=text):
                formatted = status.format_battery(text)
                self.assertIn(icon, formatted)
                self.assertTrue(formatted.endswith(text.split()[-1]))

    def test_invalid_battery_telemetry_never_invents_level_or_state(self):
        for text in ("", None, "charging", "charging -1%", "full 101%", "idle nan%", "charging <bad>"):
            with self.subTest(text=text):
                formatted = status.format_battery(text)
                self.assertIn(status.BATTERY_UNKNOWN, formatted)
                self.assertNotIn("%", formatted)
                self.assertNotIn("<bad>", formatted)

    def test_low_battery_keeps_native_urgency_and_survives_compact_view(self):
        block = dict(name="battery", full_text="discharging 14%", color=status.RED, urgent=True)
        frame = status.StatusView().update([block])
        result = next(item for item in frame if item["name"] == "battery")
        self.assertTrue(result["urgent"])
        self.assertEqual(result["color"], status.RED)
        self.assertIn(status.RED, result["full_text"])
        self.assertIn("14%", result["full_text"])
        self.assertNotIn(status.RED, status.format_battery("charging 14%"))

    def test_weather_icon_replaced_without_location(self):
        block = {"name": "read_file", "instance": "/home/jd/.cache/i3/weather.txt", "full_text": "~☾ 15°C"}
        self.assertEqual(status.adapt_status([block])[0]["full_text"],
                         '~<span font_desc="JetBrainsMono Nerd Font Propo 12" foreground="#cdd6f4">\uf186</span> 15°C')

    def test_volume_and_missing_hardware(self):
        for text, expected in (("80%", "\uf028"), ("30%", "\uf027"), ("0%", "\uf026"),
                               ("muted 20%", "\ueee8"), ("absent", "No audio"),
                               ("unavailable", "Audio ?")):
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

    def test_cpu_and_memory_keep_values_without_text_labels(self):
        blocks = status.adapt_status([{"name": "cpu_usage", "full_text": "12%"},
                                      {"name": "memory", "full_text": "1.4G"}])
        cpu, memory = blocks[:2]
        self.assertEqual(cpu["full_text"], status.labeled("\uf2db", "12%", status.YELLOW))
        self.assertEqual(memory["full_text"], status.labeled("\uefc5", "1.4G", status.RED))
        self.assertEqual(cpu["instance"], "aggregate")

    def test_wifi_click_launches_fixed_helper(self):
        with patch.object(status.subprocess, "run") as run:
            status.handle_click({"name": "wireless", "instance": "wlp2s0", "button": 1,
                                 "irrelevant": "'; touch /tmp/unsafe"})
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["i3-msg", f"exec --no-startup-id {Path(status.__file__).resolve().parent}/open-networks.sh"])
        self.assertTrue(run.call_args.kwargs["check"])
        self.assertNotIn("shell", run.call_args.kwargs)

    def test_usb_volume_instance_click(self):
        with patch.object(status.subprocess, "run") as run:
            status.handle_click({"name": "volume", "instance": "usb-output", "button": 1})
        self.assertEqual(run.call_args.args[0], ["i3-msg", f"exec --no-startup-id {Path(status.__file__).resolve().parent}/status-panel.py audio"])

    def test_trackpad_click_launches_only_the_fixed_speed_menu(self):
        event = {"name": "trackpad", "instance": "battery", "button": 1}
        with patch.object(status.subprocess, "run") as run:
            for other in (dict(event, button=4), dict(event, button=True), dict(event, instance="other"),
                          dict(event, name="bluetooth")):
                self.assertFalse(status.handle_click(other))
            run.assert_not_called()
            self.assertFalse(status.handle_click(dict(event, x="unsafe")))
            self.assertEqual(run.call_args.args[0],
                             ["i3-msg", f"exec --no-startup-id {Path(status.__file__).resolve().parent}/status-panel.py trackpad"])

    def test_clock_and_cpu_clicks_only_launch_allowlisted_panels(self):
        for name, instance, panel in (("tztime", "local", "calendar"), ("cpu_usage", "aggregate", "resources"),
                                      ("trackpad", "battery", "trackpad"), ("volume", "usb-output", "audio")):
            with self.subTest(panel=panel), patch.object(status.subprocess, "run") as run:
                status.handle_click({"name": name, "instance": instance, "button": 1,
                                     "x": 1310, "y": 12, "relative_x": 30, "relative_y": 12,
                                     "width": 80, "height": 24})
                self.assertEqual(run.call_args.args[0],
                                 ["i3-msg", f"exec --no-startup-id {Path(status.__file__).resolve().parent}/status-panel.py {panel} 1320 24"])

    def test_panel_clicks_reject_wrong_identity_and_do_not_interpret_coordinates(self):
        with patch.object(status.subprocess, "run") as run:
            for name, instance, button in (("tztime", "other", 1), ("cpu_usage", "other", 1),
                                           ("tztime", "local", 3), ("cpu_usage", "aggregate", True)):
                status.handle_click({"name": name, "instance": instance, "button": button})
            run.assert_not_called()
            status.handle_click({"name": "tztime", "instance": "local", "button": 1,
                                 "x": "$(touch /tmp/not-a-command)", "y": 0})
            self.assertEqual(run.call_args.args[0],
                             ["i3-msg", f"exec --no-startup-id {Path(status.__file__).resolve().parent}/status-panel.py calendar"])

    def test_anchor_handles_negative_monitor_coordinates_and_invalid_dimensions(self):
        event = {"x": -100, "y": 12, "relative_x": 20, "relative_y": 12, "width": 80, "height": 24}
        self.assertEqual(status.popup_anchor(event), (-80, 24))
        for changes in ({"width": 0}, {"height": 257}, {"relative_x": 80}, {"x": True}, {"y": 32767}):
            self.assertIsNone(status.popup_anchor(dict(event, **changes)))

    def test_missing_volume_block_is_honest(self):
        blocks = status.adapt_status([{"name": "wireless", "instance": "wlp2s0", "full_text": "60%"}])
        self.assertEqual(blocks[0]["name"], "volume")
        self.assertIn("No audio", blocks[0]["full_text"])

    def test_audio_tracks_hotplug_on_ticks_and_chevron_does_not_resample(self):
        audio = Mock()
        audio.sample.side_effect = [{"status": "absent"},
                                    {"status": "ready", "percentage": 17, "muted": False},
                                    {"status": "ready", "percentage": 17, "muted": True},
                                    {"status": "absent"}]
        view = status.StatusView()
        with patch.object(status.subprocess, "run") as run:
            for expected in ("No audio", "17%", "17%", "No audio"):
                frame = view.update([], audio=audio)
                block = next(b for b in frame if b["name"] == "volume")
                self.assertEqual(block["instance"], "usb-output")
                self.assertIn(expected, block["full_text"])
                before = audio.sample.call_count
                status.handle_click({"name": "stats_toggle", "instance": "secondary", "button": 1}, view)
                view.render()
                self.assertEqual(audio.sample.call_count, before)
        self.assertEqual(audio.sample.call_count, 4)
        run.assert_not_called()

    def test_unrelated_or_invalid_click_ignored(self):
        with patch.object(status.subprocess, "run") as run:
            for event in ({"name": "battery", "button": 1},
                          {"name": "wireless", "instance": "wlp2s0", "button": 3},
                          {"name": "wireless", "instance": "wrong", "button": 1},
                          {"name": "wireless", "instance": "wlp2s0", "button": True},
                          {"name": "volume", "instance": "default.Master.0", "button": 1}):
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
            {"name": "volume", "instance": "usb-output", "full_text": "absent"},
            {"name": "wireless", "instance": "wlp2s0", "full_text": "down"},
            {"name": "battery", "full_text": "absent"},
            {"name": "tztime", "full_text": "Sun Nov 15 12:00"},
        ]
        self.traffic = Mock()
        self.traffic.sample.return_value = "↑2K ↓1K/s"
        self.event = {"name": "stats_toggle", "instance": "secondary", "button": 1}

    def test_compact_gaps_keep_the_centered_icons_visually_balanced(self):
        peripherals = Mock()
        peripherals.sample.return_value = dict(adapter="connected", connected=True, percentage=80,
                                               stale=False, charging=False)
        for expanded in (False, True):
            self.view.expanded = expanded
            with self.subTest(expanded=expanded):
                frame = self.view.update(self.blocks, self.traffic, peripherals=peripherals)
                wifi = next(i for i, block in enumerate(frame) if block["name"] == "wireless")
                neighbors = frame[wifi - 1:wifi + 3]
                self.assertEqual([b["name"] for b in neighbors], ["volume", "wireless", "bluetooth", "trackpad"])
                self.assertEqual([b["separator_block_width"] for b in neighbors], [4, 1, 10, 10])
                self.assertEqual([(b["min_width"], b["align"]) for b in neighbors[1:3]],
                                 [(28, "center"), (24, "center")])
                self.assertTrue(all(b["separator_block_width"] == 10 for b in frame if b not in neighbors))
        frame = self.view.update(self.blocks)
        wifi = next(b for b in frame if b["name"] == "wireless")
        self.assertEqual(wifi["separator_block_width"], 10)

    def test_compact_default_retains_essentials_and_unknown_blocks(self):
        self.blocks.append({"name": "future_block", "full_text": "unknown"})
        frame = self.view.update(self.blocks, self.traffic)
        self.assertEqual([b["name"] for b in frame],
                         ["read_file", "stats_toggle", "read_file", "volume",
                          "wireless", "battery", "tztime", "future_block"])
        self.assertTrue(frame[0]["full_text"].startswith("~"))
        self.assertIn("\uf186", frame[0]["full_text"])
        self.assertIn("15°C", frame[0]["full_text"])
        self.assertEqual(frame[2]["full_text"].split()[-1], "?")
        self.assertIn("No audio", frame[3]["full_text"])
        self.assertIn(status.BATTERY_ABSENT, frame[5]["full_text"])
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
