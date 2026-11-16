#!/usr/bin/env python3
"""Print managed SHA256 values; --remote --check verifies deployed file contracts."""
import argparse
import hashlib
import json
from pathlib import Path
import os
import stat
import sys

root = Path(__file__).resolve().parents[1]
config = root / "config"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--remote", action="store_true")
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
remote = args.remote
result = {}
errors = []
for item in json.loads((config / "manifest.json").read_text()):
    if remote and item.get("deployment") == "private-overlay":
        result[item["source"]] = "PRIVATE:public-baseline-only"
        continue
    path = Path(item["destination"]) if remote else root / item["source"]
    try:
        result[item["source"]] = hashlib.sha256(path.read_bytes()).hexdigest()
        if args.check:
            source = root / item["source"]
            info = path.stat()
            user_file = item.get("deployment") in ("symlink", "in-place")
            expected_owner = os.getuid() if not remote or user_file else 0
            expected_group = os.getgid() if expected_owner == os.getuid() else 0
            if (info.st_uid != expected_owner or info.st_gid != expected_group or
                    stat.S_IMODE(info.st_mode) != item["mode"]):
                errors.append(f"Incorrect owner/mode: {path}")
            if remote:
                if path.read_bytes() != source.read_bytes():
                    errors.append(f"Different content: {path}")
                if item.get("deployment") == "symlink":
                    if (not path.is_symlink() or path.lstat().st_uid != os.getuid() or
                            os.readlink(path) != str(source)):
                        errors.append(f"Incorrect source link: {path}")
                elif path.is_symlink() or not stat.S_ISREG(info.st_mode):
                    errors.append(f"Expected a regular file: {path}")
                if item.get("deployment") == "in-place" and path != source:
                    errors.append(f"Expected direct checkout execution: {path}")
    except OSError as error:
        result[item["source"]] = "ERROR:" + type(error).__name__
        errors.append(f"{type(error).__name__}: {path}")
if args.check:
    for error in errors:
        print(error, file=sys.stderr)
    if not errors:
        print("Managed public files, links, owners and modes verified; private overlays skipped.")
    sys.exit(bool(errors))
else:
    print(json.dumps(result, sort_keys=True))
