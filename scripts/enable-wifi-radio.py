#!/usr/bin/python3
"""Enable the verified BGH WLAN radio once; without --apply, only inspect it."""
import argparse
import fcntl
import hashlib
import os
from pathlib import Path
import signal
import stat
import time

# This is a machine-specific firmware operation, not a generic rfkill override.
DMI = {"sys_vendor": "POSITIVO BGH", "product_name": "POSITIVO BGH",
       "bios_version": "1.04.00.BH", "bios_date": "06/09/2011"}
DSDT_SHA256 = "db29f0ce683157aaa5d3391815e82dde8987ac573b2caf2db7011781bedad481"
PCI = Path("/sys/bus/pci/devices/0000:02:00.0")
PCI_IDS = {"vendor": "0x10ec", "device": "0x8176",
           "subsystem_vendor": "0x10ec", "subsystem_device": "0x8181"}
EC = Path("/sys/kernel/debug/ec/ec0/io")
WRITE_SUPPORT = Path("/sys/module/ec_sys/parameters/write_support")
RUNTIME = Path("/run/bgh-wifi-radio")
OFFSET, ENABLED = 0x5B, 0x80


def verify_hardware():
    for key, value in DMI.items():
        if (Path("/sys/class/dmi/id") / key).read_text().strip() != value:
            raise ValueError("Unsupported laptop or BIOS")
    table = Path("/sys/firmware/acpi/tables/DSDT").read_bytes()
    if hashlib.sha256(table).hexdigest() != DSDT_SHA256:
        raise ValueError("ACPI table differs from the reviewed firmware")
    for key, value in PCI_IDS.items():
        if (PCI / key).read_text().strip() != value:
            raise ValueError("Unsupported WLAN PCI identity")


def radio_state():
    if (PCI / "driver").resolve().name != "rtl8192ce":
        raise ValueError("Expected the rtl8192ce driver")
    radios = [d for d in Path("/sys/class/rfkill").glob("rfkill*")
              if (d / "type").read_text().strip() == "wlan"
              and (d / "device").resolve().parent == (PCI / "ieee80211").resolve()]
    if len(radios) != 1:
        raise ValueError("Expected one rfkill device for the verified WLAN card")
    result = tuple(int((radios[0] / key).read_text()) for key in ("soft", "hard"))
    if any(value not in (0, 1) for value in result):
        raise ValueError("Invalid rfkill state")
    return result


def wait_for_radio(seconds):
    # Bounded startup discovery only; no background watcher or driver loading.
    for attempt in range(seconds + 1):
        try:
            return radio_state()
        except (OSError, ValueError):
            if attempt == seconds:
                raise
            time.sleep(1)


def read_byte(fd):
    os.lseek(fd, OFFSET, os.SEEK_SET)
    data = os.read(fd, 1)
    if len(data) != 1:
        raise OSError("Incomplete EC read")
    return data[0]


def write_byte(fd, value):
    os.lseek(fd, OFFSET, os.SEEK_SET)
    if os.write(fd, bytes([value])) != 1:
        raise OSError("Incomplete EC write")


def private_file(path, create=False):
    flags = os.O_RDWR | os.O_NOFOLLOW
    if create:
        flags |= os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o600:
        os.close(fd)
        raise ValueError("Unsafe runtime file")
    return fd


def restore_guard():
    marker = RUNTIME / "write-guard"
    if not os.path.lexists(marker):
        return
    fd = private_file(marker)
    try:
        if os.read(fd, 2) != b"N\n":
            raise ValueError("Invalid EC recovery marker")
        WRITE_SUPPORT.write_text("N\n")
        if WRITE_SUPPORT.read_text().strip() != "N":
            raise OSError("Failed to disable EC writes")
        marker.unlink()
    finally:
        os.close(fd)


def enable_byte(fd):
    if WRITE_SUPPORT.read_text().strip() != "N":
        raise ValueError("EC writes must be disabled initially")
    # Accept only the full byte values measured on this firmware. Unknown flags
    # are not guessed or overwritten. The BIOS restores this field in _WAK.
    if read_byte(fd) != 0 or radio_state() != (0, 1):
        raise ValueError("Expected the verified radio-off state")
    marker = RUNTIME / "write-guard"
    marker_fd = private_file(marker, create=True)
    try:
        if os.write(marker_fd, b"N\n") != 2:
            raise OSError("Incomplete EC recovery marker")
    finally:
        os.close(marker_fd)
    try:
        WRITE_SUPPORT.write_text("Y\n")
        if WRITE_SUPPORT.read_text().strip() != "Y":
            raise OSError("Could not enable the single EC write")
        if read_byte(fd) != 0 or radio_state() != (0, 1):
            raise ValueError("Radio state changed; refusing the write")
        write_byte(fd, ENABLED)
    finally:
        restore_guard()


def inspect_or_enable(apply, wait):
    verify_hardware()
    initial = wait_for_radio(wait)
    if WRITE_SUPPORT.read_text().strip() != "N":
        raise ValueError("EC writes must be disabled initially")
    fd = os.open(EC, os.O_RDWR if apply else os.O_RDONLY)
    try:
        if apply:
            # Check the unit's write access without changing the parameter.
            permission_fd = os.open(WRITE_SUPPORT, os.O_WRONLY | os.O_NOFOLLOW)
            os.close(permission_fd)
        value = read_byte(fd)
        print("Verified BGH WLAN: soft=%d hard=%d EC[0x5b]=0x%02x" % (*initial, value), flush=True)
        if not apply:
            print("Inspection only; no writes performed.")
            return
        if initial == (0, 0) and value == ENABLED:
            print("Already enabled; no write performed.")
            return
        if initial != (0, 1) or value != 0:
            raise ValueError("Unsupported state; software block and other EC flags left unchanged")
        enable_byte(fd)
        for _ in range(10):
            time.sleep(1)
            if radio_state() == (0, 0) and read_byte(fd) == ENABLED:
                print("WLAN hard block cleared; EC writes disabled.", flush=True)
                return
        raise ValueError("Radio did not enable; use integrated Fn+F11. No retry performed")
    finally:
        os.close(fd)


def locked_operation(action):
    RUNTIME.mkdir(mode=0o700, exist_ok=True)
    info = RUNTIME.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or stat.S_IMODE(info.st_mode) != 0o700:
        raise ValueError("Expected a private root-owned runtime directory")
    lock = RUNTIME / "lock"
    try:
        fd = private_file(lock, create=True)
    except FileExistsError:
        fd = private_file(lock)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        restore_guard()
        action()
    finally:
        os.close(fd)


def interrupted(_signum, _frame):
    raise RuntimeError("Operation interrupted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--apply", action="store_true", help="Enable only the verified radio-off state")
    modes.add_argument("--restore-guard", action="store_true", help="Restore disabled EC writes after an interrupted operation")
    parser.add_argument("--wait", type=int, choices=(0, 10), default=0, help="Bounded radio discovery delay in seconds")
    args = parser.parse_args()
    try:
        if os.geteuid() != 0:
            raise ValueError("Use authenticated sudo to inspect protected firmware and EC state")
        signal.signal(signal.SIGTERM, interrupted)
        signal.signal(signal.SIGINT, interrupted)
        if args.apply or args.restore_guard:
            locked_operation((lambda: None) if args.restore_guard else lambda: inspect_or_enable(True, args.wait))
        else:
            inspect_or_enable(False, args.wait)
    except (OSError, ValueError, RuntimeError) as error:
        parser.exit(1, f"Wi-Fi operation stopped: {error}\n")


if __name__ == "__main__":
    main()
