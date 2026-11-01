#!/usr/bin/env python3
"""Install pinned official RTK/Engram binaries on Linux amd64 without compiling.

Run as the target user on the laptop. Never handles credentials or user data.
Existing differing binaries are not overwritten. Integration is a separate,
reviewed step documented in development-tools.md.
"""
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import platform
import tarfile
import tempfile
import time
import urllib.error
import urllib.request


RELEASES = {
    "rtk": (
        "https://github.com/rtk-ai/rtk/releases/download/v1.1.0/"
        "rtk-x86_64-unknown-linux-musl.tar.gz",
        "9454ad1b9489daa57ab0a9f4ebe2faaf4dc82b8a0f26c9e5135151abd7c9378d",
    ),
    "engram": (
        "https://github.com/Gentleman-Programming/engram/releases/download/v3.6.0/"
        "engram_3.6.0_linux_amd64.tar.gz",
        "945fb471188826c251160947f8dda9fe148ba0dd095fa3453174fe7ab5c6479e",
    ),
}


def download(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "i3-2310m-setup"})
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read(32 * 1024 * 1024 + 1)
            if len(body) > 32 * 1024 * 1024:
                raise ValueError("Archive exceeded size limit")
            return body
        except (OSError, urllib.error.URLError):
            if attempt == 2:
                raise
            time.sleep(2)


def main():
    if platform.system() != "Linux" or platform.machine() != "x86_64":
        raise SystemExit("This pinned installer only supports Linux x86_64")
    if os.geteuid() == 0:
        raise SystemExit("Run as the target user, not root")
    destination = Path.home() / ".local/bin"
    if destination.is_symlink():
        raise SystemExit("Refusing a symlinked bin directory")
    destination.mkdir(parents=True, exist_ok=True)
    for name, (url, digest) in RELEASES.items():
        print(f"Downloading pinned {name} release", flush=True)
        archive = download(url)
        if hashlib.sha256(archive).hexdigest() != digest:
            raise SystemExit(f"Checksum mismatch for {name}; not installed")
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            members = [m for m in tar.getmembers()
                       if m.isfile() and PurePosixPath(m.name).name == name]
            if len(members) != 1 or members[0].size > 128 * 1024 * 1024:
                raise SystemExit(f"Unexpected archive layout for {name}")
            binary = tar.extractfile(members[0]).read()
        if not binary.startswith(b"\x7fELF"):
            raise SystemExit(f"Expected a Linux ELF binary for {name}")
        target = destination / name
        if target.is_symlink():
            raise SystemExit(f"Refusing existing symlink {target}")
        if target.exists():
            if target.read_bytes() == binary:
                print(f"Already identical: {target}", flush=True)
                continue
            raise SystemExit(f"Existing differing {target}; review and back up before replacing")
        fd, temporary = tempfile.mkstemp(prefix=f".{name}-", dir=destination)
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(binary)
                os.fchmod(stream.fileno(), 0o755)
                stream.flush()
                os.fsync(stream.fileno())
            # Hard link fails rather than overwriting a concurrently created file.
            os.link(temporary, target)
        finally:
            os.unlink(temporary)
        print(f"Installed {target}; binary SHA256 {hashlib.sha256(binary).hexdigest()}", flush=True)


if __name__ == "__main__":
    main()
