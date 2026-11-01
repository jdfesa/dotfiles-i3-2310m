#!/usr/bin/env python3
"""Print SHA256 for managed files; --remote reads deployed destinations."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
config = root / "config"
remote = "--remote" in sys.argv[1:]
result = {}
for item in json.loads((config / "manifest.json").read_text()):
    path = Path(item["destination"]) if remote else root / item["source"]
    try:
        result[item["source"]] = hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as error:
        result[item["source"]] = "ERROR:" + type(error).__name__
print(json.dumps(result, sort_keys=True))
