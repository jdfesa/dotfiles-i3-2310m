#!/usr/bin/python3
"""On-demand controls for the fixed local Apache/PHP and MariaDB stack."""
import argparse
import importlib.util
import os
from pathlib import Path
import subprocess


def load_module(filename):
    path = Path(__file__).resolve().with_name(filename)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--status", action="store_true", help="Read service states without opening a window")
    actions.add_argument("--service-action", nargs=2, metavar=("ACTION", "UNIT"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("Run this program as your desktop account, without sudo")
    try:
        control = load_module("web-stack-control.py")
        if args.service_action:
            return control.run_action(*args.service_action)
        if args.status:
            states = control.service_states()
            for unit, state in states.items():
                print(f"{control.SERVICES[unit]}: {state}")
            return int("Unavailable" in states.values())
        return load_module("web-stack-window.py").run(control)
    except ValueError as error:
        parser.error(str(error))
    except (ImportError, OSError, subprocess.SubprocessError) as error:
        parser.exit(1, f"Local Web Stack: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
