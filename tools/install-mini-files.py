#!/usr/bin/env python3
"""Install only pinned mini.files code, help and license; never from Nvim startup.

Dry-run by default. No root, compilation, plugin manager or automatic updates.
Existing differing files are conflicts; --check verifies without using network.
"""
import argparse
import hashlib
import io
import os
from pathlib import Path
import platform
import shutil
import tarfile
import tempfile
import time
import urllib.request


VERSION = "v0.18.0"
COMMIT = "a5689dae6b732955e33eec225b798d6815063179"
URL = f"https://codeload.github.com/nvim-mini/mini.files/tar.gz/{COMMIT}"
ARCHIVE_SHA256 = "b1a68583f6778303873dc5b3571d96720ab9dd97697c4db4ca752872ce15032b"
FILES = {
    "LICENSE": "ad5113c573908b4af4f458b3ed183cd6ce518b24e654c759d4e420f7e4d9faab",
    "doc/mini-files.txt": "6a629f32e420cbebcbf47632e474cac17da946317158481cbcc94f9aef2d7c37",
    "lua/mini/files.lua": "a68bdfe4ea2d158b823f8292ae022add9b2170d30a6eaf65c6d8b57d5bd1a80b",
}
LIMIT = 2 * 1024 * 1024


def destination():
    data = Path(os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    if not data.is_absolute():
        raise ValueError("XDG_DATA_HOME must be absolute")
    return data / "nvim/site/pack/vendor/start/mini.files"


def check_path(path):
    for ancestor in (path, *path.parents):
        if ancestor.is_symlink():
            raise ValueError(f"Symlinked installation path: {ancestor}")
    if path.exists() and path.stat().st_uid != os.getuid():
        raise ValueError("Installation is not owned by this account")


def verify(target):
    check_path(target)
    if not target.is_dir():
        raise ValueError("mini.files is not installed")
    actual = set()
    for path in target.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Unexpected symlink: {path}")
        if path.is_file():
            actual.add(path.relative_to(target).as_posix())
    if actual - set(FILES) - {"doc/tags"}:
        raise ValueError("Unexpected installed files; review before replacing")
    for name, checksum in FILES.items():
        path = target / name
        if hashlib.sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"Installed file differs: {name}")
        if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o777 != 0o644:
            raise ValueError(f"Incorrect installed owner/mode: {name}")


def archive_files(body):
    if len(body) > LIMIT or hashlib.sha256(body).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("Archive checksum/size mismatch; nothing installed")
    result = {}
    prefix = f"mini.files-{COMMIT}/"
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as archive:
        for member in archive.getmembers():
            name = member.name.removeprefix(prefix)
            if not member.name.startswith(prefix) or name not in FILES:
                continue
            if not member.isfile() or member.size > LIMIT or name in result:
                raise ValueError("Unexpected archive member")
            content = archive.extractfile(member).read()
            if hashlib.sha256(content).hexdigest() != FILES[name]:
                raise ValueError(f"Archive file checksum mismatch: {name}")
            result[name] = content
    if set(result) != set(FILES):
        raise ValueError("Missing files in archive")
    return result


def download():
    for attempt in range(3):
        try:
            request = urllib.request.Request(URL, headers={"User-Agent": "i3-2310m-setup"})
            with urllib.request.urlopen(request, timeout=40) as response:
                return response.read(LIMIT + 1)
        except OSError:
            if attempt == 2:
                raise
            time.sleep(2)


def install(target, body):
    check_path(target)
    if target.exists():
        verify(target)
        return False
    files = archive_files(body)
    target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".mini-files-", dir=target.parent))
    try:
        for name, content in files.items():
            path = temporary / name
            path.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o644)
        temporary.chmod(0o755)
        if target.exists() or target.is_symlink():
            raise ValueError("Installation appeared concurrently")
        temporary.rename(target)
        verify(target)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--archive", type=Path, help="Previously downloaded pinned archive")
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("Run as the target account, never root")
    if platform.system() != "Linux":
        parser.error("This deployment targets Linux")
    try:
        target = destination()
        check_path(target)
        print(f"mini.files {VERSION} ({COMMIT})\nDestination: {target}")
        if args.check:
            verify(target)
            print("Installed code, help, license, modes and owners match")
        elif args.apply:
            if target.exists():
                verify(target)
                print("Already identical; no download or changes")
                return
            body = args.archive.read_bytes() if args.archive else download()
            install(target, body)
            print("Installed; Nvim startup never downloads or updates this module")
        else:
            print(f"Source: {URL}\nSHA256: {ARCHIVE_SHA256}\nDry-run only; nothing changed")
    except (OSError, ValueError, tarfile.TarError) as error:
        parser.exit(1, f"Stopped: {error}\n")


if __name__ == "__main__":
    main()
