"""Isolated socket recovery fixtures; no real Codex state, auth or processes."""
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/codex-launch.py"
spec = importlib.util.spec_from_file_location("codex_launcher", SOURCE)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class CodexLauncherTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cx-", dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.home.mkdir(mode=0o700)
        self.control = self.home / "app-server-control"
        self.control.mkdir(mode=0o700)
        self.lock = self.control / "app-server-startup.lock"
        self.lock.touch(mode=0o600)
        self.runtime = self.root / "t"
        self.parent = self.runtime / f"codex-daemon-{os.getuid()}"
        self.parent.mkdir(mode=0o700, parents=True)
        self.target = self.parent / ("a" * 64)
        self.alias = self.control / "app-server-control.sock"
        self.alias.symlink_to(self.target)

    def recover(self):
        return launcher.recover_socket(self.home, self.runtime)

    def test_reclaims_only_stale_alias_and_is_idempotent(self):
        private = self.home / "auth.json"
        private.write_text("synthetic credential sentinel")
        self.assertTrue(self.recover())
        self.assertFalse(self.alias.is_symlink())
        self.assertFalse(self.recover())
        self.assertEqual(private.read_text(), "synthetic credential sentinel")

    def test_handles_runtime_parent_missing_after_boot(self):
        self.parent.rmdir()
        self.assertTrue(self.recover())

    def test_preserves_live_socket(self):
        with socket.socket(socket.AF_UNIX) as server:
            server.bind(str(self.target))
            server.listen(1)
            self.assertFalse(self.recover())
            self.assertTrue(self.alias.is_symlink())
            with socket.socket(socket.AF_UNIX) as client:
                client.connect(str(self.alias))

    def test_preserves_any_existing_target(self):
        self.target.write_text("not a socket")
        self.assertFalse(self.recover())
        self.assertTrue(self.alias.is_symlink())

    def test_refuses_unexpected_target(self):
        for target in (self.root / "missing", self.parent / "short",
                       self.parent.parent / "codex-daemon-other" / ("a" * 64)):
            self.alias.unlink()
            self.alias.symlink_to(target)
            self.assertFalse(self.recover())
            self.assertTrue(self.alias.is_symlink())

    def test_preserves_regular_control_entry(self):
        self.alias.unlink()
        self.alias.write_text("preserve")
        self.assertFalse(self.recover())
        self.assertEqual(self.alias.read_text(), "preserve")

    def test_busy_startup_lock_prevents_cleanup(self):
        with self.lock.open("rb") as stream:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertFalse(self.recover())
            self.assertTrue(self.alias.is_symlink())

    def test_refuses_symlinked_lock_and_directories(self):
        self.lock.unlink()
        other = self.root / "lock"
        other.touch()
        self.lock.symlink_to(other)
        self.assertFalse(self.recover())
        self.lock.unlink()
        self.lock.touch()
        moved = self.home / "moved"
        self.control.rename(moved)
        self.control.symlink_to(moved)
        self.assertFalse(self.recover())
        self.assertTrue(self.alias.is_symlink())

    def test_refuses_writable_state_or_runtime_directories(self):
        for path in (self.home, self.control, self.parent):
            path.chmod(0o777)
            self.assertFalse(self.recover())
            self.assertTrue(self.alias.is_symlink())
            path.chmod(0o700)

    def test_new_installation_creates_nothing(self):
        missing = self.root / "missing"
        self.assertFalse(launcher.recover_socket(missing, self.runtime))
        self.assertFalse(missing.exists())

    def test_launcher_exec_preserves_arguments_and_exit_status(self):
        user = self.root / "user"
        binary = user / ".codex/packages/standalone/current/bin/codex"
        binary.parent.mkdir(parents=True)
        binary.write_text(f"#!{sys.executable}\nimport json,sys\n"
                          "print(json.dumps(sys.argv[1:]))\nsys.exit(23)\n")
        binary.chmod(0o755)
        result = subprocess.run([sys.executable, str(SOURCE), "exec", "a b", "--no-daemon"],
                                env=dict(os.environ, HOME=str(user), CODEX_HOME=str(self.home)),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 23, result.stderr)
        self.assertEqual(json.loads(result.stdout), ["exec", "a b", "--no-daemon"])

    def test_manifest_and_durable_contract(self):
        entries = json.loads((ROOT / "config/manifest.json").read_text())
        self.assertIn({"source": "scripts/codex-launch.py",
                       "destination": "/home/jd/.local/bin/codex", "mode": 493}, entries)
        self.assertIn("on-demand Codex launcher", (ROOT / "AGENTS.md").read_text())
        self.assertIn("intended source account", (ROOT / "AGENTS.md").read_text())
        self.assertIn("cuenta esperada", (ROOT / "docs/codex-setup.md").read_text())


if __name__ == "__main__":
    unittest.main()
