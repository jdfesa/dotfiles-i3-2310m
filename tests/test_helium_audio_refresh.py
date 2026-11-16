"""Exact audio utility recovery with synthetic proc files; never signal real processes."""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import os
from pathlib import Path
import signal
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("helium_audio_refresh", ROOT / "scripts/refresh-helium-audio.py")
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)


def process(root, executable, pid=42, started=123, role="utility", subtype="audio.mojom.AudioService", separator=b"\0"):
    path = root / str(pid)
    path.mkdir()
    (path / "exe").symlink_to(executable)
    command = [b"helium", f"--type={role}".encode(), f"--utility-sub-type={subtype}".encode()]
    (path / "cmdline").write_bytes(separator.join(command))
    (path / "stat").write_text(f"{pid} (helium) " + " ".join(["S"] + ["0"] * 18 + [str(started)]))
    return refresh.Process(pid, started)


class AudioRefreshTests(unittest.TestCase):
    def test_only_exact_owned_executable_and_audio_role_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "helium"
            executable.touch()
            wanted = process(root, executable)
            process(root, executable, pid=43, subtype="network.mojom.NetworkService")
            process(root, executable, pid=44, role="renderer")
            other = root / "other"
            other.touch()
            process(root, other, pid=45)
            with patch.object(refresh, "HELIUM", executable):
                self.assertEqual(refresh.select_service(root), wanted)
                with patch.object(refresh.os, "getuid", return_value=os.getuid() + 1):
                    with self.assertRaises(OSError):
                        refresh.select_service(root)

    def test_flattened_process_titles_work_and_duplicate_roles_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "helium"
            executable.touch()
            wanted = process(root, executable, separator=b" ")
            with patch.object(refresh, "HELIUM", executable):
                self.assertEqual(refresh.identify(42, root), wanted)
                with (root / "42/cmdline").open("ab") as output:
                    output.write(b" --type=renderer")
                self.assertIsNone(refresh.identify(42, root))

    def test_absence_ambiguity_and_vanished_processes_stop_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            executable = root / "helium"
            executable.touch()
            with patch.object(refresh, "HELIUM", executable):
                with self.assertRaisesRegex(OSError, "No active"):
                    refresh.select_service(root)
                process(root, executable)
                process(root, executable, pid=43)
                with self.assertRaisesRegex(OSError, "Multiple"):
                    refresh.select_service(root)
                self.assertIsNone(refresh.identify(999, root))

    def test_capture_must_be_closed_and_state_must_be_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            status = root / "card0/pcm0c/sub0/status"
            status.parent.mkdir(parents=True)
            status.write_text("closed\n")
            refresh.ensure_capture_closed(root)
            for value in ("state: RUNNING\n", "state: PREPARED\n", ""):
                status.write_text(value)
                with self.assertRaises(OSError):
                    refresh.ensure_capture_closed(root)
            with self.assertRaises(OSError):
                refresh.ensure_capture_closed(root / "missing")

    def test_pidfd_signal_is_limited_to_verified_generation_and_closed(self):
        wanted = refresh.Process(42, 123)
        with patch.object(refresh, "guard") as guard, \
                patch.object(refresh, "select_service", return_value=wanted), \
                patch.object(refresh.os, "pidfd_open", return_value=71) as opened, \
                patch.object(refresh.signal, "pidfd_send_signal") as send, \
                patch.object(refresh.os, "close") as close:
            refresh.refresh(wanted)
            opened.assert_called_once_with(42)
            guard.assert_called_once_with()
            send.assert_called_once_with(71, signal.SIGTERM)
            close.assert_called_once_with(71)

    def test_changed_pid_generation_or_failed_guard_never_signals(self):
        wanted = refresh.Process(42, 123)
        for fail_guard in (False, True):
            with patch.object(refresh, "guard", side_effect=OSError("USB removed") if fail_guard else None), \
                    patch.object(refresh, "select_service", return_value=refresh.Process(42, 124)), \
                    patch.object(refresh.os, "pidfd_open", return_value=71), \
                    patch.object(refresh.signal, "pidfd_send_signal") as send, \
                    patch.object(refresh.os, "close") as close:
                with self.assertRaises(OSError):
                    refresh.refresh(wanted)
                send.assert_not_called()
                close.assert_called_once_with(71)

    def test_default_only_checks_and_apply_is_explicit(self):
        for args in ([], ["--apply"]):
            with patch.object(refresh.os, "getuid", return_value=1000), \
                    patch.object(refresh, "guard", return_value={"percentage": 47, "muted": False}), \
                    patch.object(refresh, "select_service", return_value=refresh.Process(42, 123)), \
                    patch.object(refresh, "refresh") as action, redirect_stdout(io.StringIO()):
                self.assertEqual(refresh.main(args), 0)
                self.assertEqual(action.call_count, int(bool(args)))

    def test_root_and_unavailable_output_do_not_refresh(self):
        for uid in (0, 1000):
            with patch.object(refresh.os, "getuid", return_value=uid), \
                    patch.object(refresh, "guard", side_effect=OSError("USB absent")), \
                    patch.object(refresh, "refresh") as action, redirect_stderr(io.StringIO()):
                self.assertEqual(refresh.main(["--apply"]), 1)
                action.assert_not_called()


if __name__ == "__main__":
    unittest.main()
