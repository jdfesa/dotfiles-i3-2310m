#!/usr/bin/python3
"""Review or install the BGH Wi-Fi oneshot; no package installation or reboot."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {"scripts/enable-wifi-radio.py", "config/wifi-radio/bgh-wifi-radio.service"}
UNIT = "bgh-wifi-radio.service"


def inventory():
    entries = [e for e in json.loads((ROOT / "config/manifest.json").read_text()) if e["source"] in SOURCES]
    if len(entries) != 2 or {e["source"] for e in entries} != SOURCES:
        raise ValueError("Incomplete Wi-Fi deployment inventory")
    return entries


def regular(path):
    for parent in (path, *path.parents):
        if parent.is_symlink():
            raise ValueError(f"Refusing a symlink: {parent}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")


def plan():
    entries = inventory()
    for entry in entries:
        source, target = ROOT / entry["source"], Path(entry["destination"])
        regular(source)
        regular(target)
        if not source.is_file() or stat.S_IMODE(source.stat().st_mode) != entry["mode"]:
            raise ValueError(f"Incorrect source or mode: {source}")
        before = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else "absent"
        after = hashlib.sha256(source.read_bytes()).hexdigest()
        print(f"{entry['source']} -> {target} (root:root {entry['mode']:o})", flush=True)
        print(f"  Previous SHA256: {before}\n  Candidate SHA256: {after}", flush=True)
    print("Apply backs up both destinations, installs regular root-owned files, and enables the oneshot.", flush=True)
    print("It does not start the service, restart NetworkManager, change the radio, or reboot.", flush=True)
    return entries


def apply(entries):
    if os.geteuid() != 0 or os.environ.get("SUDO_USER") != "jd":
        raise ValueError("Run --apply with authenticated sudo from jd")
    os.umask(0o077)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = Path("/var/backups") / ("bgh-wifi-radio-" + stamp)
    backup.mkdir(mode=0o700)
    before = subprocess.run(["systemctl", "is-enabled", UNIT], text=True, capture_output=True).stdout.strip()
    records = []
    for index, entry in enumerate(entries):
        target = Path(entry["destination"])
        regular(target)
        record = {"destination": str(target), "existed": target.exists()}
        if target.exists():
            info = target.stat()
            record.update(mode=stat.S_IMODE(info.st_mode), uid=info.st_uid, gid=info.st_gid, backup=str(index))
            shutil.copyfile(target, backup / str(index))
        records.append(record)
    (backup / "rollback.json").write_text(json.dumps({"unit_state": before, "files": records}, indent=2) + "\n")
    print(f"Private rollback inventory: {backup}", flush=True)
    for entry in entries:
        parent = Path(entry["destination"]).parent
        if not parent.exists():
            parent.mkdir(mode=0o755, parents=True)
            parent.chmod(0o755)
        subprocess.run(["install", "-o", "root", "-g", "root", "-m", f"{entry['mode']:o}",
                        str(ROOT / entry["source"]), entry["destination"]], check=True)
        target = Path(entry["destination"])
        info = target.stat()
        if (info.st_uid, info.st_gid, stat.S_IMODE(info.st_mode)) != (0, 0, entry["mode"]):
            raise ValueError("Installed ownership or mode mismatch")
        if target.read_bytes() != (ROOT / entry["source"]).read_bytes():
            raise ValueError("Installed content differs from reviewed source")
    subprocess.run(["systemd-analyze", "verify", "/etc/systemd/system/" + UNIT], check=True)
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", UNIT], check=True)
    print("Installed and enabled for the next boot; not started.", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Install and enable with authenticated sudo; default is dry-run")
    args = parser.parse_args()
    try:
        entries = plan()
        if args.apply:
            apply(entries)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Installation stopped: {error}\n")


if __name__ == "__main__":
    main()
