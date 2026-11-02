#!/usr/bin/env python3
"""Launch the official standalone CLI, reclaiming only its dangling socket alias.

Codex 0.165.0 can leave an alias in persistent home pointing into volatile /tmp.
Never reads credentials, stops processes, or modifies vendor packages.
"""
import fcntl
import os
from pathlib import Path
import re
import stat
import sys


def owned_directory(path, uid):
    info = path.lstat()
    return (stat.S_ISDIR(info.st_mode) and info.st_uid == uid
            and not info.st_mode & 0o022)


def recover_socket(codex_home, runtime_root=Path("/tmp")):
    """Return whether one verified stale alias was removed; otherwise do nothing.

    Share the vendor startup flock, refuse symlinked directories/locks and only
    accept the observed per-UID runtime target with its exact 64-hex basename.
    A live socket (or any existing target) is always preserved.
    """
    uid = os.getuid()
    control = codex_home / "app-server-control"
    alias = control / "app-server-control.sock"
    lock = control / "app-server-startup.lock"
    try:
        if not all(owned_directory(p, uid) for p in (codex_home, control)):
            return False
        # No creation: a new installation has nothing to recover.
        fd = os.open(lock, os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC)
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_uid != uid or info.st_nlink != 1:
                return False
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            before = alias.lstat()
            if not stat.S_ISLNK(before.st_mode) or before.st_uid != uid:
                return False
            target = Path(os.readlink(alias))
            expected_parent = runtime_root / f"codex-daemon-{uid}"
            if target.parent != expected_parent or not re.fullmatch(r"[0-9a-f]{64}", target.name):
                return False
            try:
                if not owned_directory(expected_parent, uid):
                    return False
            except FileNotFoundError:
                pass  # /tmp itself may have been cleared at boot.
            try:
                target.lstat()
                return False
            except FileNotFoundError:
                pass
            # Recheck identity under the startup lock before the single unlink.
            after = alias.lstat()
            if (before.st_dev, before.st_ino, before.st_ctime_ns) != (
                    after.st_dev, after.st_ino, after.st_ctime_ns):
                return False
            alias.unlink()
            return True
    except OSError:
        # Busy startup, absent files or unexpected permissions: let Codex report
        # its own error rather than broadening cleanup or blocking other commands.
        return False


def main():
    home = Path.home()
    binary = home / ".codex/packages/standalone/current/bin/codex"
    if not binary.is_file() or not os.access(binary, os.X_OK):
        print("Codex standalone binary is missing; see docs/codex-setup.md.", file=sys.stderr)
        return 127
    codex_home = Path(os.environ.get("CODEX_HOME") or home / ".codex")
    if codex_home.is_absolute():
        recover_socket(codex_home)
    os.execv(binary, [str(binary), *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
