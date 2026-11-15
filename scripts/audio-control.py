#!/usr/bin/python3
"""Hardware-scoped USB playback mixer using the existing ALSA library."""
import ctypes as C
import json
import math
import os
from pathlib import Path
import re
from typing import NamedTuple


class Profile(NamedTuple):
    vendor: int
    product: int
    control: str
    index: int


class Device(NamedTuple):
    card: int
    path: Path
    inode: int


def load_profile(path=None):
    if path is None:
        path = Path(__file__).resolve().parents[1] / "config/audio/usb-audio.json"
        if not path.is_file():
            path = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "audio/usb-audio.json"
    data = json.loads(Path(path).read_text())
    if (not isinstance(data, dict) or set(data) != {"vendor", "product", "control", "index"} or
            not all(isinstance(data[k], str) and re.fullmatch(r"[0-9a-fA-F]{4}", data[k])
                    for k in ("vendor", "product")) or
            not isinstance(data["control"], str) or
            not re.fullmatch(r"[A-Za-z][A-Za-z0-9 -]{0,63}", data["control"]) or
            type(data["index"]) is not int or not 0 <= data["index"] <= 31):
        raise ValueError("Invalid USB audio profile.")
    return Profile(int(data["vendor"], 16), int(data["product"], 16), data["control"], data["index"])


def find_devices(profile, root=Path("/sys/class/sound")):
    matches = []
    for card in sorted(root.glob("card*")):
        if not re.fullmatch(r"card[0-9]+", card.name):
            continue
        try:
            interface = (card / "device").resolve(strict=True)
            if (interface / "driver").resolve(strict=True).name != "snd-usb-audio":
                continue
            for usb in (interface, *interface.parents):
                if not (usb / "idVendor").is_file():
                    continue
                identity = tuple(int((usb / key).read_text(), 16) for key in ("idVendor", "idProduct"))
                if identity == (profile.vendor, profile.product):
                    real = card.resolve(strict=True)
                    matches.append(Device(int(card.name[4:]), real, real.stat().st_ino))
                break
        except (OSError, ValueError):
            continue
    return matches


def raw_volume(percentage, minimum, maximum):
    if (isinstance(percentage, bool) or not isinstance(percentage, (int, float)) or
            not math.isfinite(percentage) or not 0 <= percentage <= 100 or maximum <= minimum):
        raise ValueError("Volume must be between 0 and 100 percent.")
    return minimum + round(percentage * (maximum - minimum) / 100)


class ALSA:
    def __init__(self):
        self.lib = C.CDLL("libasound.so.2")
        ptr, integer, long = C.c_void_p, C.c_int, C.c_long
        signatures = {
            "snd_mixer_open": (integer, [C.POINTER(ptr), integer]),
            "snd_mixer_attach": (integer, [ptr, C.c_char_p]),
            "snd_mixer_selem_register": (integer, [ptr, ptr, ptr]),
            "snd_mixer_load": (integer, [ptr]),
            "snd_mixer_handle_events": (integer, [ptr]),
            "snd_mixer_close": (integer, [ptr]),
            "snd_mixer_selem_id_malloc": (integer, [C.POINTER(ptr)]),
            "snd_mixer_selem_id_free": (None, [ptr]),
            "snd_mixer_selem_id_set_name": (None, [ptr, C.c_char_p]),
            "snd_mixer_selem_id_set_index": (None, [ptr, C.c_uint]),
            "snd_mixer_find_selem": (ptr, [ptr, ptr]),
            "snd_mixer_selem_is_active": (integer, [ptr]),
            "snd_mixer_selem_has_playback_volume": (integer, [ptr]),
            "snd_mixer_selem_has_playback_switch": (integer, [ptr]),
            "snd_mixer_selem_has_playback_channel": (integer, [ptr, integer]),
            "snd_mixer_selem_get_playback_volume_range": (integer, [ptr, C.POINTER(long), C.POINTER(long)]),
            "snd_mixer_selem_get_playback_volume": (integer, [ptr, integer, C.POINTER(long)]),
            "snd_mixer_selem_get_playback_switch": (integer, [ptr, integer, C.POINTER(integer)]),
            "snd_mixer_selem_set_playback_volume_all": (integer, [ptr, long]),
            "snd_mixer_selem_set_playback_switch_all": (integer, [ptr, integer]),
        }
        for name, (result, args) in signatures.items():
            function = getattr(self.lib, name)
            function.restype, function.argtypes = result, args


def checked(result):
    if result < 0:
        raise OSError("USB playback control is unavailable.")
    return result


class Mixer:
    def __init__(self, profile, device, alsa=None, finder=find_devices):
        self.profile, self.device, self.finder = profile, device, finder
        self.lib = (alsa or ALSA()).lib
        self.handle, self.identity = C.c_void_p(), C.c_void_p()
        try:
            self.verify()
            checked(self.lib.snd_mixer_open(C.byref(self.handle), 0))
            checked(self.lib.snd_mixer_attach(self.handle, f"hw:{device.card}".encode()))
            checked(self.lib.snd_mixer_selem_register(self.handle, None, None))
            checked(self.lib.snd_mixer_load(self.handle))
            checked(self.lib.snd_mixer_selem_id_malloc(C.byref(self.identity)))
            self.lib.snd_mixer_selem_id_set_name(self.identity, profile.control.encode())
            self.lib.snd_mixer_selem_id_set_index(self.identity, profile.index)
            self.read()
        except Exception:
            self.close()
            raise

    def verify(self):
        if self.finder(self.profile) != [self.device]:
            raise OSError("USB audio changed. Close and reopen the volume panel.")

    def element(self):
        self.verify()
        checked(self.lib.snd_mixer_handle_events(self.handle))
        element = self.lib.snd_mixer_find_selem(self.handle, self.identity)
        if (not element or not self.lib.snd_mixer_selem_is_active(element) or
                not self.lib.snd_mixer_selem_has_playback_volume(element)):
            raise OSError("The USB playback volume control is unavailable.")
        return element

    def read(self):
        element = self.element()
        low, high = C.c_long(), C.c_long()
        checked(self.lib.snd_mixer_selem_get_playback_volume_range(element, C.byref(low), C.byref(high)))
        channels = [c for c in range(32) if self.lib.snd_mixer_selem_has_playback_channel(element, c)]
        if not channels or high.value <= low.value:
            raise OSError("The USB playback volume range is unavailable.")
        volumes, switches = [], []
        can_mute = bool(self.lib.snd_mixer_selem_has_playback_switch(element))
        for channel in channels:
            value, enabled = C.c_long(), C.c_int()
            checked(self.lib.snd_mixer_selem_get_playback_volume(element, channel, C.byref(value)))
            if not low.value <= value.value <= high.value:
                raise OSError("Invalid USB playback volume.")
            volumes.append(value.value)
            if can_mute:
                checked(self.lib.snd_mixer_selem_get_playback_switch(element, channel, C.byref(enabled)))
                switches.append(bool(enabled.value))
        return {"status": "ready", "percentage": round(100 * (max(volumes) - low.value) / (high.value - low.value)),
                "muted": can_mute and not any(switches), "can_mute": can_mute,
                "minimum": low.value, "maximum": high.value, "raw": volumes}

    def set_volume(self, percentage):
        state = self.read()
        value = raw_volume(percentage, state["minimum"], state["maximum"])
        element = self.element()
        checked(self.lib.snd_mixer_selem_set_playback_volume_all(element, value))
        return self.read()

    def set_muted(self, muted):
        if type(muted) is not bool:
            raise ValueError("Mute must be a boolean.")
        element = self.element()
        if not self.lib.snd_mixer_selem_has_playback_switch(element):
            raise OSError("The USB output has no mute switch.")
        checked(self.lib.snd_mixer_selem_set_playback_switch_all(element, not muted))
        return self.read()

    def close(self):
        if self.identity.value:
            self.lib.snd_mixer_selem_id_free(self.identity)
            self.identity = C.c_void_p()
        if self.handle.value:
            self.lib.snd_mixer_close(self.handle)
            self.handle = C.c_void_p()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class AudioStatus:
    def __init__(self, profile=None, finder=find_devices, factory=Mixer):
        self.finder, self.factory, self.alsa = finder, factory, None
        try:
            self.profile = profile or load_profile()
        except (OSError, ValueError, TypeError):
            self.profile = None

    def sample(self):
        if self.profile is None:
            return {"status": "unavailable"}
        try:
            devices = self.finder(self.profile)
            if not devices:
                return {"status": "absent"}
            if len(devices) != 1:
                return {"status": "unavailable"}
            if self.alsa is None:
                self.alsa = ALSA()
            with self.factory(self.profile, devices[0], self.alsa, self.finder) as mixer:
                return mixer.read()
        except (OSError, ValueError, AttributeError):
            return {"status": "unavailable"}


if __name__ == "__main__":
    print(json.dumps(AudioStatus().sample()))
