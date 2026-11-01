#!/usr/bin/env python3
"""Repair reviewed managed paths after joe->jd; default is inspection only.

Development maintenance tool, not a boot service. Does not rename accounts,
read credentials/memories, rewrite application history, or run shell commands.
"""
import argparse
import json
import os
from pathlib import Path
import pwd
import re
import shutil
import stat
import tempfile

OLD = "/home/joe"
NEW = "/home/jd"
LINKS = (
    ".local/bin/codex", ".codex/packages/standalone/current",
    ".codex/packages/app-server-daemon/current",
    ".config/systemd/user/timers.target.wants/weather-refresh.timer",
    ".config/systemd/user/timers.target.wants/packages-refresh.timer",
)


def relocate(value):
    return re.sub(re.escape(OLD) + r"(?=/|$|[\s\"':,;)\]])", NEW, value)


def atomic_text(path, content, info):
    fd, temporary = tempfile.mkstemp(prefix=".home-migration-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, stat.S_IMODE(info.st_mode))
        os.chown(temporary, info.st_uid, info.st_gid)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--backup", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    home = Path(NEW if args.apply else OLD)
    if args.apply:
        account = pwd.getpwnam("jd")
        if os.geteuid() != 0 or account.pw_uid != 1000 or account.pw_dir != NEW:
            parser.error("apply requires root and the renamed UID1000 jd account")
        if args.backup is None or not args.backup.is_relative_to("/root/bgh-a470-backups"):
            parser.error("a private root backup directory is required")
        args.backup.mkdir(parents=True, exist_ok=True, mode=0o700)
    changed = []
    for relative in LINKS:
        path = home / relative
        if not path.is_symlink():
            continue
        previous = os.readlink(path)
        following = relocate(previous)
        if following == previous:
            continue
        if args.apply:
            info = path.lstat()
            target = args.backup / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            target.symlink_to(previous)
            path.unlink()
            path.symlink_to(following)
            os.lchown(path, info.st_uid, info.st_gid)
        changed.append({"kind": "symlink", "path": relative})
    for item in json.loads(args.manifest.read_text()):
        destination = Path(item["destination"])
        if not destination.is_relative_to(NEW):
            continue  # System files are not part of this operation.
        relative = destination.relative_to(NEW)
        path = home / relative
        if path.is_symlink():
            raise RuntimeError("unexpected managed symlink: " + str(relative))
        info = path.stat()
        if info.st_uid != 1000:
            raise RuntimeError("unexpected managed owner: " + str(relative))
        try:
            original = path.read_text()
        except UnicodeDecodeError:
            continue  # Fonts are binary and are never rewritten.
        updated = relocate(original)
        if updated == original:
            continue
        if args.apply:
            target = args.backup / relative
            target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            shutil.copy2(path, target)
            atomic_text(path, updated, info)
        changed.append({"kind": "managed_text", "path": str(relative)})
    print(json.dumps({"apply": args.apply, "changes": changed}, indent=2))


if __name__ == "__main__":
    main()
