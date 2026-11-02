#!/usr/bin/env python3
"""Regenerate the secondary snapshot from a clean, committed Git checkout.

GitHub/pull synchronizes working copies; this tool never transports their sources.
Default is a dry-run. It excludes all untracked/ignored data via git archive and
retires only recognized legacy guides, renamed tools and generated metadata.
Unknown extra files or symlinks stop the entire plan before any writes.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def checksum(body):
    return hashlib.sha256(body).hexdigest()


def export(root):
    if subprocess.check_output(["git", "-C", str(root), "status", "--porcelain"]):
        raise ValueError("Source checkout must be committed and clean; pull from GitHub first")
    if subprocess.check_output(["git", "-C", str(root), "ls-files", "-ci", "--exclude-standard"]):
        raise ValueError("Tracked ignored files require a privacy review before export")
    commit = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    body = subprocess.check_output(["git", "-C", str(root), "archive", "--format=tar", "HEAD"])
    files = {}
    with tarfile.open(fileobj=io.BytesIO(body)) as archive:
        for member in archive.getmembers():
            if member.isdir():
                continue
            name = PurePosixPath(member.name)
            if name.is_absolute() or ".." in name.parts or not member.isfile():
                raise ValueError("Only regular, relative tracked files are supported")
            mode = 0o755 if member.mode & 0o111 else 0o644
            files[str(name)] = (archive.extractfile(member).read(), mode)
    return commit, files


def retired(name, files):
    path = Path(name)
    if path.name.startswith("._") or path.name == ".DS_Store":
        return True
    if "__pycache__" in path.parts and path.suffix == ".pyc":
        return True
    if path.parent == Path(".") and "docs/" + name in files:
        return True
    return name == "tools/build_status_icons.py" and "tools/build-status-icons.py" in files


def plan(target, files):
    if target.is_symlink() or not target.is_dir() or target.stat().st_uid != os.getuid():
        raise ValueError("Destination must be an existing account-owned regular directory")
    actions = []
    for path in target.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Review symlink before synchronization: {path}")
        if path.stat().st_uid != os.getuid():
            raise ValueError(f"Unexpected owner: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"Unexpected file type: {path}")
        name = str(path.relative_to(target))
        if name not in files:
            if not retired(name, files):
                raise ValueError(f"Unknown extra file; review privately first: {name}")
            actions.append(dict(path=name, action="retire", before=checksum(path.read_bytes()),
                                mode=stat.S_IMODE(path.stat().st_mode)))
    for name, (body, mode) in files.items():
        path = target / name
        for parent in path.parents:
            if parent == target:
                break
            if parent.exists() and not parent.is_dir():
                raise ValueError(f"Destination parent is not a directory: {parent}")
        if path.exists() and not path.is_file():
            raise ValueError(f"Destination is not a regular file: {path}")
        if path.exists() and path.read_bytes() == body and stat.S_IMODE(path.stat().st_mode) == mode:
            continue
        actions.append(dict(path=name, action="write", before=checksum(path.read_bytes()) if path.exists() else None,
                            mode=stat.S_IMODE(path.stat().st_mode) if path.exists() else None))
    return sorted(actions, key=lambda item: item["path"])


def apply(root, target, files, actions, backup, commit):
    root, target, backup = root.resolve(), target.resolve(), backup.absolute()
    if not actions:
        return
    for boundary in (root, target):
        if backup == boundary or boundary in backup.parents:
            raise ValueError("Recovery baseline must be outside source and destination")
    if backup.exists() or any(p.is_symlink() for p in (backup, *backup.parents)):
        raise ValueError("Recovery directory must be new and not symlinked")
    if plan(target, files) != actions:
        raise ValueError("Destination changed after review")
    backup.mkdir(mode=0o700, parents=True)
    backup.chmod(0o700)
    for item in actions:
        path = target / item["path"]
        if item["before"] is not None:
            copy = backup / "files" / item["path"]
            copy.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            copy.write_bytes(path.read_bytes())
            copy.chmod(0o600)
            if checksum(copy.read_bytes()) != item["before"]:
                raise ValueError("Destination changed while backing up")
    journal = backup / "journal.json"
    journal.write_text(json.dumps(dict(commit=commit, entries=actions), indent=2) + "\n")
    journal.chmod(0o600)
    for item in actions:
        path = target / item["path"]
        current = checksum(path.read_bytes()) if path.is_file() and not path.is_symlink() else None
        if path.is_symlink() or current != item["before"]:
            raise ValueError("Destination changed before installation; inspect the recovery baseline")
        if item["action"] == "retire":
            path.unlink()
            continue
        body, mode = files[item["path"]]
        path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".secondary-", dir=path.parent)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(body)
                os.fchmod(stream.fileno(), mode)
            os.replace(temporary, path)
        finally:
            if os.path.lexists(temporary):
                os.unlink(temporary)
    for path in sorted(target.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            try:
                path.rmdir()
            except OSError:
                pass  # Nonempty current directories must remain.
    if plan(target, files):
        raise ValueError("Post-deployment comparison failed; inspect the recovery baseline")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("Run as jd, never root")
    try:
        commit, files = export(ROOT)
        target = Path.home() / "setup-guide"
        if ROOT == target.resolve() or ROOT in target.resolve().parents or target.resolve() in ROOT.parents:
            raise ValueError("Source and secondary snapshot must be separate trees")
        actions = plan(target, files)
        print(f"Committed files: {len(files)}; planned changes: {len(actions)}; source: {commit[:12]}")
        for item in actions:
            print(f"{item['action']}: {item['path']}")
        if args.check:
            if args.apply or args.backup_dir:
                parser.error("--check cannot be combined with deployment")
            if actions:
                raise ValueError("Secondary snapshot is not current")
            print("Secondary contents, modes and file set match the committed source")
        elif args.apply:
            if not args.backup_dir:
                parser.error("--apply requires --backup-dir outside both trees")
            apply(ROOT, target, files, actions, args.backup_dir, commit)
            print("Current snapshot verified; no obsolete active copies retained")
        else:
            if args.backup_dir:
                parser.error("--backup-dir requires --apply")
            print("Dry-run only; nothing changed")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Stopped: {error}\n")


if __name__ == "__main__":
    main()
