"""Network panel tests without NetworkManager or a real terminal window."""

import fcntl
import os
from pathlib import Path
import pty
import select
import shutil
import subprocess
import tempfile
import time
import unittest


LAUNCHER = Path(__file__).resolve().parents[1] / "scripts/open-networks.sh"


@unittest.skipUnless(shutil.which("flock"), "util-linux flock is required")
class NetworkPanelTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name)
        self.bin_dir = self.root / "bin"
        self.runtime = self.root / "runtime"
        self.bin_dir.mkdir()
        self.runtime.mkdir()
        self.trace = self.root / "trace"
        self.env = {
            **os.environ,
            "PATH": str(self.bin_dir) + os.pathsep + os.environ["PATH"],
            "XDG_RUNTIME_DIR": str(self.runtime),
            "TRACE": str(self.trace),
        }
        self.lock = self.runtime / "bgh-network-menu.lock"
        self.stub("kitty", """if flock -n "$XDG_RUNTIME_DIR/bgh-network-menu.lock" true; then
    exit 99
fi
printf 'kitty:%s\\n' "$@" >> "$TRACE"
""")
        self.stub("i3-msg", """printf 'i3:%s\\n' "$@" >> "$TRACE"
exit "${I3_STATUS:-0}"
""")
        self.stub("nmtui-connect", 'exit "${CHILD_STATUS:-0}"\n')

    def stub(self, command, program):
        path = self.bin_dir / command
        path.write_text("#!/bin/sh\n" + program)
        path.chmod(0o755)

    def launch(self, *args, **extra_env):
        return subprocess.run(
            [LAUNCHER, *args], input="", capture_output=True, text=True,
            env={**self.env, **extra_env}, timeout=5,
        )

    def test_first_request_starts_dedicated_kitty_under_lock(self):
        result = self.launch()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.trace.read_text().splitlines(), [
            "kitty:--class", "kitty:BGH-Networks", "kitty:--name", "kitty:BGH-Networks",
            "kitty:--title", "kitty:Wi-Fi networks", "kitty:--override=tab_bar_min_tabs=2",
            "kitty:-e", f"kitty:{LAUNCHER}", "kitty:--in-terminal",
        ])
        with self.lock.open("r") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def test_repeat_request_focuses_only_the_existing_instance(self):
        for status in ("0", "2"):
            with self.subTest(i3_status=status), self.lock.open("w") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                result = self.launch(I3_STATUS=status)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(self.trace.read_text().splitlines(), [
                    "i3:-q",
                    'i3:[class="^BGH-Networks$" instance="^BGH-Networks$" title="^Wi-Fi networks$"] focus',
                ])
                self.trace.unlink()

    def test_normal_exit_and_keyboard_interrupt_are_silent(self):
        for status in ("0", "130"):
            with self.subTest(child_status=status):
                result = self.launch("--in-terminal", CHILD_STATUS=status)
                self.assertEqual((result.returncode, result.stderr), (0, ""))

    def test_unexpected_child_failure_keeps_its_status(self):
        result = self.launch("--in-terminal", CHILD_STATUS="37")
        self.assertEqual(result.returncode, 37)
        self.assertIn("Wi-Fi panel exited unexpectedly (status 37).", result.stderr)
        self.assertNotIn("Press Enter", result.stderr)

    def test_unexpected_child_failure_waits_in_a_terminal(self):
        master, slave = pty.openpty()
        self.addCleanup(os.close, master)
        try:
            child = subprocess.Popen(
                [LAUNCHER, "--in-terminal"], stdin=slave, stdout=slave, stderr=slave,
                env={**self.env, "CHILD_STATUS": "37"},
            )
        finally:
            os.close(slave)
        try:
            output = bytearray()
            deadline = time.monotonic() + 5
            while b"Press Enter to close." not in output:
                remaining = deadline - time.monotonic()
                self.assertGreater(remaining, 0, output)
                self.assertTrue(select.select([master], [], [], remaining)[0], output)
                output.extend(os.read(master, 4096))
            self.assertIsNone(child.poll())
            os.write(master, b"\n")
            self.assertEqual(child.wait(timeout=5), 37)
        finally:
            if child.poll() is None:
                child.kill()
                child.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
