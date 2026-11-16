"""Verify link identity, runtime paths and private exclusions in isolated trees."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DeploymentVerificationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (self.root / "tools").mkdir()
        (self.root / "config").mkdir()
        self.tool = self.root / "tools/verify-mirror.py"
        shutil.copyfile(ROOT / "tools/verify-mirror.py", self.tool)
        self.source = self.root / "config/sample.conf"
        self.source.write_text("public=true\n")
        self.source.chmod(0o644)
        self.target = self.root / "installed.conf"

    def check(self, entries):
        (self.root / "config/manifest.json").write_text(json.dumps(entries))
        return subprocess.run([sys.executable, self.tool, "--remote", "--check"],
                              capture_output=True, text=True)

    def linked_entry(self):
        return dict(source="config/sample.conf", destination=str(self.target),
                    mode=0o644, deployment="symlink")

    def test_identical_content_requires_the_exact_source_link(self):
        self.target.write_bytes(self.source.read_bytes())
        result = self.check([self.linked_entry()])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Incorrect source link", result.stderr)
        self.target.unlink()
        other = self.root / "other.conf"
        other.write_bytes(self.source.read_bytes())
        self.target.symlink_to(other)
        self.assertNotEqual(self.check([self.linked_entry()]).returncode, 0)
        self.target.unlink()
        self.target.symlink_to(self.source)
        self.assertEqual(self.check([self.linked_entry()]).returncode, 0)

    def test_in_place_script_rejects_an_identical_duplicate(self):
        self.source.chmod(0o755)
        entry = dict(source="config/sample.conf", destination=str(self.source),
                     mode=0o755, deployment="in-place")
        self.assertEqual(self.check([entry]).returncode, 0)
        self.target.write_bytes(self.source.read_bytes())
        self.target.chmod(0o755)
        entry["destination"] = str(self.target)
        result = self.check([entry])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("direct checkout execution", result.stderr)

    def test_private_overlay_is_not_read_or_compared(self):
        entry = dict(source="config/sample.conf", destination=str(self.target),
                     mode=0o600, deployment="private-overlay")
        self.target.write_text("synthetic-private-state\n")
        self.target.chmod(0)
        try:
            result = self.check([entry])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("synthetic-private-state", result.stdout + result.stderr)
        finally:
            self.target.chmod(0o600)
