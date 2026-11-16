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
                "sample = json.dumps([{'name': 'memory', 'full_text': '37%'}])\n"
                "def frame(*_):\n"
                " print(',' + sample, flush=True)\n"
                "signal.signal(signal.SIGCONT, frame)\n"
                "print(json.dumps({'version': 1}), flush=True)\n"
                "print('[', flush=True)\n"
                "print(sample, flush=True)\n"
                "while True: signal.pause()\n"
            )
            backend.chmod(0o755)
            adapter = home / "scripts/status-clicks.py"
            adapter.write_bytes((ROOT / "scripts/status-clicks.py").read_bytes())
            adapter.chmod(0o755)
            # Keep process-group regression tests independent of real Bluetooth.
            (home / "scripts/bluetooth-status.py").write_text(
                "class BluetoothStatus:\n"
                " def sample(self):\n"
                "  return dict(adapter='absent', connected=False, percentage=None, charging=False, stale=False)\n"
                " def close(self): pass\n")
            (home / "scripts/audio-control.py").write_text(
                "class AudioStatus:\n"
                " def sample(self): return dict(status='absent')\n")
            (home / "scripts/audio-position.py").write_text(
                "class PositionMemory:\n"
                " def __init__(self): raise OSError('no X11 in fixture')\n")
            (home / "scripts/screen-brightness.py").write_text(
                "def sample(): return 57\n")
            env = dict(os.environ, HOME=str(home))
            process = subprocess.Popen(
                ["/bin/sh", "-c", shlex.quote(str(adapter))],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                start_new_session=True, env=env,
            )
            buffer = b""
            header = None
            frames = 0
            latest = None

            def read_until(wanted_frames):
                nonlocal buffer, header, frames, latest
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
                            latest = value
                self.assertGreaterEqual(frames, wanted_frames)

            try:
                read_until(1)
                self.assertIsNotNone(header)
                self.assertNotIn("memory", [b["name"] for b in latest])
                for _ in range(3):
                    before = frames
                    os.killpg(process.pid, header.get("stop_signal", signal.SIGSTOP))
                    time.sleep(0.05)
                    self.assertIsNone(process.poll(), "hiding killed the launcher")
                    os.killpg(process.pid, header.get("cont_signal", signal.SIGCONT))
                    read_until(before + 1)
                    self.assertIsNone(process.poll(), "showing killed the launcher")
                    # The producer is idle in signal.pause(): clicks must redraw
                    # immediately without waiting for another producer frame.
                    for expanded in (True, False):
                        before = frames
                        event = {"name": "stats_toggle", "instance": "secondary", "button": 1}
                        process.stdin.write((json.dumps(event) + "\n").encode())
                        process.stdin.flush()
                        read_until(before + 1)
                        self.assertEqual("memory" in [b["name"] for b in latest], expanded)
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
