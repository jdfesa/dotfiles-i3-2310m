"""Current-only secondary snapshot behavior, without network or real repositories."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("secondary", ROOT / "tools/sync-secondary.py")
SECONDARY = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SECONDARY)


class SecondarySnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="i3-secondary-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.source, self.target = self.base / "source", self.base / "secondary"
        self.source.mkdir()
        self.target.mkdir()
        self.files = {"README.md": (b"Current entry\n", 0o644),
                      "docs/example.md": (b"Current guide\n", 0o644)}

    def test_apply_replaces_old_content_and_retires_only_recognized_extras(self):
        (self.target / "README.md").write_text("Obsolete entry\n")
        (self.target / "example.md").write_text("Obsolete guide\n")
        (self.target / "._README.md").write_bytes(b"metadata")
        actions = SECONDARY.plan(self.target, self.files)
        backup = self.base / "recovery"
        SECONDARY.apply(self.source, self.target, self.files, actions, backup, "synthetic")
        self.assertFalse(SECONDARY.plan(self.target, self.files))
        self.assertFalse((self.target / "example.md").exists())
        self.assertFalse((self.target / "._README.md").exists())
        self.assertEqual((backup / "files/README.md").read_text(), "Obsolete entry\n")
        self.assertEqual(backup.stat().st_mode & 0o777, 0o700)
        self.assertEqual((backup / "journal.json").stat().st_mode & 0o777, 0o600)

    def test_unknown_extra_is_reviewed_not_published_or_deleted(self):
        private = self.target / "personal-notes.txt"
        private.write_text("synthetic private note")
        with self.assertRaisesRegex(ValueError, "Unknown extra"):
            SECONDARY.plan(self.target, self.files)
        self.assertEqual(private.read_text(), "synthetic private note")
        self.assertFalse((self.target / "README.md").exists())

    def test_symlinks_stop_before_writes(self):
        (self.target / "docs").symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            SECONDARY.plan(self.target, self.files)

    def test_backup_inside_active_tree_is_rejected(self):
        actions = SECONDARY.plan(self.target, self.files)
        with self.assertRaisesRegex(ValueError, "outside source and destination"):
            SECONDARY.apply(self.source, self.target, self.files, actions, self.target / "backups", "synthetic")
        self.assertFalse((self.target / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
