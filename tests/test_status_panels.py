"""Offline panel identity, IPC, placement, locking and calendar checks."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


panel = module("status_panel", "status-panel.py")
calendar = module("calendar_popup", "calendar-popup.py")


def window(identity, cid=42):
    return {"id": cid, "window": 100, "rect": {"width": 360, "height": 320},
            "window_properties": {"class": identity[0], "instance": identity[1]}}


class PanelTests(unittest.TestCase):
    def test_only_exact_class_and_instance_match_and_outer_frame_is_retained(self):
        wrong = window(("Kitty", "bgh-resources"))
        wanted = window(panel.PANELS["resources"])
        outer = {"width": 964, "height": 564}
        tree = {"nodes": [wrong], "floating_nodes": [{"type": "floating_con", "rect": outer, "nodes": [wanted]}]}
        self.assertEqual(panel.find_panel(tree, panel.PANELS["resources"]), (wanted, outer))
        self.assertIsNone(panel.find_panel(wrong, panel.PANELS["resources"]))

    def test_placement_uses_global_coordinates_and_clamps_both_edges(self):
        outputs = [{"active": True, "rect": {"x": -1366, "y": 0, "width": 1366, "height": 768}}]
        out = panel.choose_output(outputs, -100, 24)
        self.assertIsNotNone(out)
        size = {"width": 360, "height": 320}
        self.assertEqual(panel.target_position(out, size, -10, 24), (-360, 28))
        self.assertEqual(panel.target_position(out, size, -1360, 700), (-1366, 448))
        self.assertIsNone(panel.choose_output(outputs, 10, 24))
        self.assertEqual(panel.target_position(out, {"width": 2000, "height": 1000}, -100, 24), (-1366, 0))

    def test_invalid_container_never_becomes_an_i3_command(self):
        for value in (True, 0, -1, "42; kill"):
            with self.assertRaises(ValueError):
                panel.container_id({"id": value})

    def test_resource_launch_is_fixed_and_scopes_close_policy_to_monitor(self):
        with patch.object(panel.shutil, "which", side_effect=lambda name: "/usr/bin/" + name):
            command = panel.launch_command("resources")
        self.assertEqual(command[-4:], ["-e", "/usr/bin/btop", "--update", "2000"])
        self.assertIn("--override=confirm_os_window_close=0", command)
        self.assertIn("--class=BGH-Resources", command)
        with patch.object(panel.shutil, "which", return_value=None), self.assertRaises(RuntimeError):
            panel.launch_command("resources")

    def test_trackpad_launch_and_identity_are_independent_of_calendar(self):
        self.assertNotEqual(panel.PANELS["trackpad"], panel.PANELS["calendar"])
        with patch.object(panel.os, "access", return_value=True):
            self.assertEqual(panel.launch_command("trackpad"),
                             [str(Path.home() / "scripts/open-trackpad-speed.py")])
        self.assertIsNone(panel.find_panel(window(panel.PANELS["calendar"]), panel.PANELS["trackpad"]))

    def test_existing_panel_closes_only_its_container_and_does_not_launch(self):
        target = window(panel.PANELS["resources"])
        ipc = Mock()
        ipc.request.side_effect = [{"success": True}, target, [{"success": True}]]
        ipc.next_window.side_effect = [{"change": "close", "container": {"id": 17}},
                                       {"change": "close", "container": {"id": 42}}]
        with patch.dict(os.environ, I3SOCK="/fixture/i3"), patch.object(panel, "IPC", return_value=ipc), \
                patch.object(panel.socket, "socket"), patch.object(panel.subprocess, "Popen") as launch:
            panel.open_panel("resources")
        launch.assert_not_called()
        self.assertEqual(ipc.request.call_args.args, (0, "[con_id=42] kill"))

    def test_subscribe_precedes_launch_and_unrelated_windows_are_ignored(self):
        target = window(panel.PANELS["calendar"])
        ipc = Mock()
        ipc.request.side_effect = [{"success": True}, {},
                                  [{"active": True, "rect": {"x": 0, "y": 0, "width": 1366, "height": 768}}],
                                  target, [{"success": True}]]
        ipc.next_window.side_effect = [{"change": "new", "container": window(("Kitty", "ordinary"))},
                                       {"change": "new", "container": target}]
        with patch.dict(os.environ, I3SOCK="/fixture/i3"), patch.object(panel, "IPC", return_value=ipc), \
                patch.object(panel.socket, "socket"), patch.object(panel, "launch_command", return_value=["fixture"]), \
                patch.object(panel.subprocess, "Popen") as launch:
            launch.side_effect = lambda *a, **k: self.assertEqual(ipc.request.call_count, 3)
            panel.open_panel("calendar", (1320, 24))
        self.assertEqual(ipc.request.call_args.args, (0, "[con_id=42] move absolute position 1006 28"))
        launch.assert_called_once()

    def test_ipc_failure_does_not_launch_a_duplicate_fallback(self):
        with patch.dict(os.environ, I3SOCK="/fixture/i3"), patch.object(panel.socket, "socket") as factory, \
                patch.object(panel.subprocess, "Popen") as launch:
            factory.return_value.__enter__.return_value.connect.side_effect = OSError("offline")
            with self.assertRaises(OSError):
                panel.open_panel("resources")
        launch.assert_not_called()

    def test_busy_lock_drops_simultaneous_activation_and_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, XDG_RUNTIME_DIR=folder), \
                patch.object(panel, "open_panel") as open_panel:
            path = Path(folder) / "bgh-panel-calendar.lock"
            fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                panel.toggle_panel("calendar")
                open_panel.assert_not_called()
            finally:
                os.close(fd)
            panel.toggle_panel("calendar")
            open_panel.assert_called_once_with("calendar", None)
            path.unlink()
            path.symlink_to(Path(folder) / "other")
            with self.assertRaises(OSError):
                panel.toggle_panel("calendar")

    def test_wire_reader_handles_fragmented_packets_and_queues_events(self):
        payload = json.dumps({"change": "focus"}).encode()
        response = json.dumps({"success": True}).encode()
        data = panel.HEADER.pack(b"i3-ipc", len(payload), panel.WINDOW_EVENT) + payload
        data += panel.HEADER.pack(b"i3-ipc", len(response), 2) + response
        stream = Mock()
        chunks = bytearray(data)
        def receive(size):
            result = bytes(chunks[:min(size, 3)])
            del chunks[:len(result)]
            return result
        stream.recv.side_effect = receive
        ipc = panel.IPC(stream)
        self.assertEqual(ipc.request(2, '["window"]'), {"success": True})
        self.assertEqual(ipc.next_window(), {"change": "focus"})
        with self.assertRaises(OSError):
            ipc.receive()


class CalendarTests(unittest.TestCase):
    def test_month_navigation_and_date_bounds(self):
        for values, expected in (((2026, 12, 1), (2027, 1)), ((2026, 1, -1), (2025, 12)),
                                 ((1, 1, -1), (1, 1)), ((9999, 12, 1), (9999, 12))):
            self.assertEqual(calendar.offset_month(*values), expected)
        for values in ((0, 1, 1), (2026, 13, 0), (True, 1, 0), (2026, 1, "1")):
            with self.assertRaises(ValueError):
                calendar.offset_month(*values)

    def test_activation_closes_only_its_existing_window_or_builds_one(self):
        application = Mock()
        with patch.object(calendar, "build_window") as build:
            calendar.activate(application)
            application.get_active_window.return_value.destroy.assert_called_once_with()
            build.assert_not_called()
            application.get_active_window.return_value = None
            calendar.activate(application)
            build.assert_called_once_with(application)
            build.return_value.show_all.assert_called_once_with()

    def test_missing_display_fails_without_loading_gtk(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(calendar, "gtk_modules") as gtk:
            self.assertEqual(calendar.main(), 1)
        gtk.assert_not_called()
