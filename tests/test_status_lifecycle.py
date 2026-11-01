"""Exercise the real shell/adapter process group, without a graphical session."""
import json
import os
from pathlib import Path
import select
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StatusLifecycleTests(unittest.TestCase):
    def test_hide_show_keeps_shell_and_adapter_alive_and_resumes_frames(self):
        with tempfile.TemporaryDirectory(prefix="i3-status-lifecycle-") as folder:
            home = Path(folder)
            (home / "scripts").mkdir()
            backend = home / "scripts/status-bar.sh"
            backend.write_text(
                f"#!{sys.executable}\n"
                "import json, signal\n"
                "def frame(*_):\n"
                " print(',[]', flush=True)\n"
                "signal.signal(signal.SIGCONT, frame)\n"
                "print(json.dumps({'version': 1}), flush=True)\n"
                "print('[', flush=True)\n"
                "print('[]', flush=True)\n"
                "while True: signal.pause()\n"
            )
            backend.chmod(0o755)
            env = dict(os.environ, HOME=str(home))
            process = subprocess.Popen(
                ["/bin/sh", "-c", shlex.quote(str(ROOT / "scripts/status-clicks.py"))],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True, env=env,
            )
            buffer = b""
            header = None
            frames = 0

            def read_until(wanted_frames):
                nonlocal buffer, header, frames
                deadline = time.monotonic() + 3
                while frames < wanted_frames and time.monotonic() < deadline:
                    ready, _, _ = select.select([process.stdout], [], [],
                                                max(0, deadline - time.monotonic()))
                    if not ready:
                        break
                    chunk = os.read(process.stdout.fileno(), 65536)
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        line = line.strip().lstrip(b",").strip()
                        if line in (b"", b"[", b"]"):
                            continue
                        value = json.loads(line)
                        if isinstance(value, dict):
                            header = value
                        elif isinstance(value, list):
                            frames += 1
                self.assertGreaterEqual(frames, wanted_frames)

            try:
                read_until(1)
                self.assertIsNotNone(header)
                for _ in range(3):
                    before = frames
                    os.killpg(process.pid, header.get("stop_signal", signal.SIGSTOP))
                    time.sleep(0.05)
                    self.assertIsNone(process.poll(), "hiding killed the launcher")
                    os.killpg(process.pid, header.get("cont_signal", signal.SIGCONT))
                    read_until(before + 1)
                    self.assertIsNone(process.poll(), "showing killed the launcher")
            finally:
                for sig in (signal.SIGCONT, signal.SIGTERM):
                    try:
                        os.killpg(process.pid, sig)
                    except ProcessLookupError:
                        pass
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                for stream in (process.stdin, process.stdout, process.stderr):
                    stream.close()


if __name__ == "__main__":
    unittest.main()
