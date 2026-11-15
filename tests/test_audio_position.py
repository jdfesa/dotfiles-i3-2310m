"""Position snapshots and top-bar anchors without live X11 or audio writes."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audio_position", ROOT / "scripts/audio-position.py")
position = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(position)


class PositionTests(unittest.TestCase):
    def test_snapshot_only_contains_audio_and_visible_blocks_to_its_right(self):
        frame = [{"name": "memory", "full_text": "37%"},
                 {"name": "volume", "instance": "usb-output", "full_text": "17%", "separator_block_width": 4},
                 {"name": "tztime", "full_text": "18:00", "markup": "pango"}]
        self.assertEqual(position.suffix(frame), [
            {"full_text": "17%", "separator_block_width": 4},
            {"full_text": "18:00", "markup": "pango"}])
        self.assertEqual(position.suffix([]), [])

    def test_anchor_accounts_for_text_separator_last_gap_and_negative_output(self):
        rect = dict(x=-1366, y=0, width=1366, height=24)
        self.assertEqual(position.anchor_from_widths(rect, [(40, 4), (28, 12), (180, 12)]), (-244, 24))
        self.assertEqual(position.anchor_from_widths(rect, [(40, 4), (28, 12), (180, 12)], 10), (-254, 24))
        for widths in ([], [(0, 4)], [(3000, 4)]):
            with self.assertRaises(ValueError):
                position.anchor_from_widths(rect, widths)

    def test_bar_lookup_stays_on_focused_output(self):
        def bar(xid):
            return dict(window=xid, window_properties={"class": "i3bar", "instance": "bar-0"})
        wanted, other = bar(1), bar(2)
        tree = {"nodes": [{"type": "output", "name": "left", "nodes": [other]},
                          {"type": "output", "name": "right", "nodes": [wanted]}]}
        self.assertIs(position.find_bar(tree, "right"), wanted)
        self.assertIsNone(position.find_bar(tree, "missing"))

    def test_keyboard_uses_current_top_bar_font_and_focused_output(self):
        bar = dict(window=1, window_properties={"class": "i3bar", "instance": "bar-0"},
                   rect=dict(x=0, y=0, width=1366, height=24))
        tree = {"nodes": [{"type": "output", "name": "LVDS-1", "nodes": [bar]}]}
        ipc = Mock()
        ipc.request.side_effect = [[dict(focused=True, output="LVDS-1")],
                                   dict(position="top", font="pango:Mono 10", padding=dict(width=0))]
        with patch.object(position, "PositionMemory") as memory, patch.object(position, "measure_blocks") as measure:
            memory.return_value.dpi.return_value = 96
            memory.return_value.read.return_value = [{"full_text": "17%"}]
            measure.return_value = [(40, 4), (180, 12)]
            self.assertEqual(position.keyboard_anchor(ipc, tree), (1162, 24))
            measure.assert_called_once_with([{"full_text": "17%"}], "Mono 10", 96)
            memory.return_value.close.assert_called_once()

    def test_missing_bar_fails_without_center_fallback(self):
        ipc = Mock()
        ipc.request.return_value = [{"focused": True, "output": "missing"}]
        with self.assertRaises(RuntimeError):
            position.keyboard_anchor(ipc, {"nodes": []})

    def test_unchanged_suffix_does_not_publish_again_on_chevron_redraw(self):
        memory = object.__new__(position.PositionMemory)
        memory.x = Mock()
        memory.display, memory.root, memory.atom, memory.utf8 = 1, 2, 3, 4
        memory.previous = None
        block = dict(name="volume", instance="usb-output", full_text="17%")
        memory.publish([block])
        memory.publish([dict(name="memory", full_text="37%"), block])
        self.assertEqual(memory.x.XChangeProperty.call_count, 1)
        memory.publish([dict(block, full_text="18%")])
        self.assertEqual(memory.x.XChangeProperty.call_count, 2)


if __name__ == "__main__":
    unittest.main()
