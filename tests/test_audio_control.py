"""USB identity, playback-only writes and honest audio states; no real writes."""
import ctypes as C
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("audio_control", ROOT / "scripts/audio-control.py")
audio = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audio)


def put(pointer, kind, value):
    C.cast(pointer, C.POINTER(kind))[0] = value
    return 0


def fixture_mixer():
    mixer = object.__new__(audio.Mixer)
    mixer.profile = audio.Profile(0x8086, 0x0808, "Speaker", 0)
    mixer.device = audio.Device(0, Path("/synthetic/card0"), 123)
    mixer.finder = Mock(return_value=[mixer.device])
    mixer.handle, mixer.identity = C.c_void_p(1), C.c_void_p(2)
    lib = mixer.lib = Mock()
    for name in ("snd_mixer_handle_events", "snd_mixer_close"):
        getattr(lib, name).return_value = 0
    lib.snd_mixer_find_selem.return_value = 3
    lib.snd_mixer_selem_is_active.return_value = 1
    lib.snd_mixer_selem_has_playback_volume.return_value = 1
    lib.snd_mixer_selem_has_playback_switch.return_value = 1
    lib.snd_mixer_selem_has_playback_channel.side_effect = lambda _, channel: channel in (0, 1)
    values, switches = [25, 25], [1, 1]

    def limits(_, low, high):
        put(low, C.c_long, 0)
        return put(high, C.c_long, 151)

    def volume(_, value):
        values[:] = [value, value]
        return 0

    def mute(_, value):
        switches[:] = [int(value), int(value)]
        return 0

    lib.snd_mixer_selem_get_playback_volume_range.side_effect = limits
    lib.snd_mixer_selem_get_playback_volume.side_effect = lambda _, channel, out: put(out, C.c_long, values[channel])
    lib.snd_mixer_selem_get_playback_switch.side_effect = lambda _, channel, out: put(out, C.c_int, switches[channel])
    lib.snd_mixer_selem_set_playback_volume_all.side_effect = volume
    lib.snd_mixer_selem_set_playback_switch_all.side_effect = mute
    return mixer, values, switches


class AudioTests(unittest.TestCase):
    def test_profile_rejects_bad_types_identity_and_control(self):
        valid = dict(vendor="8086", product="0808", control="Speaker", index=0)
        with tempfile.TemporaryDirectory() as tmp:
            profile = Path(tmp) / "profile.json"
            for value in (None, [], dict(valid, vendor="8086;"), dict(valid, index=True),
                          dict(valid, control="Speaker\0Mic"), dict(valid, secret="excluded")):
                profile.write_text(json.dumps(value))
                with self.assertRaises(ValueError):
                    audio.load_profile(profile)
            profile.write_text(json.dumps(valid))
            self.assertEqual(audio.load_profile(profile), audio.Profile(0x8086, 0x0808, "Speaker", 0))

    def test_only_profile_usb_hardware_with_native_driver_is_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            usb = root / "usb"
            interface = usb / "interface"
            interface.mkdir(parents=True)
            (usb / "idVendor").write_text("8086\n")
            (usb / "idProduct").write_text("0808\n")
            driver = root / "drivers/snd-usb-audio"
            driver.mkdir(parents=True)
            (interface / "driver").symlink_to(driver)
            (root / "card0").mkdir()
            (root / "card0/device").symlink_to(interface)
            profile = audio.Profile(0x8086, 0x0808, "Speaker", 0)
            found = audio.find_devices(profile, root)
            self.assertEqual(len(found), 1)
            self.assertEqual(found[0].card, 0)
            (usb / "idProduct").write_text("1234\n")
            self.assertEqual(audio.find_devices(profile, root), [])
            (usb / "idProduct").write_text("0808\n")
            (interface / "driver").unlink()
            self.assertEqual(audio.find_devices(profile, root), [])

    def test_volume_conversion_is_bounded_and_never_amplifies(self):
        for percent, raw in ((0, 0), (17, 26), (50, 76), (100, 151)):
            self.assertEqual(audio.raw_volume(percent, 0, 151), raw)
        for value in (-1, 101, True, "50", float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                audio.raw_volume(value, 0, 151)
        with self.assertRaises(ValueError):
            audio.raw_volume(50, 2, 2)

    def test_read_preserves_raw_values_switches_and_performs_no_writes(self):
        mixer, values, switches = fixture_mixer()
        state = mixer.read()
        self.assertEqual(state["percentage"], 17)
        self.assertFalse(state["muted"])
        self.assertEqual(values, [25, 25])
        self.assertEqual(switches, [1, 1])
        mixer.lib.snd_mixer_selem_set_playback_volume_all.assert_not_called()
        mixer.lib.snd_mixer_selem_set_playback_switch_all.assert_not_called()

    def test_volume_only_changes_playback_and_never_unmutes(self):
        mixer, values, switches = fixture_mixer()
        switches[:] = [0, 0]
        state = mixer.set_volume(50)
        self.assertEqual(values, [76, 76])
        self.assertTrue(state["muted"])
        self.assertEqual(switches, [0, 0])
        mixer.lib.snd_mixer_selem_set_playback_switch_all.assert_not_called()
        self.assertFalse(any("capture" in str(call) for call in mixer.lib.mock_calls))

    def test_explicit_mute_changes_no_volume(self):
        mixer, values, switches = fixture_mixer()
        self.assertTrue(mixer.set_muted(True)["muted"])
        self.assertEqual(switches, [0, 0])
        self.assertEqual(values, [25, 25])
        self.assertFalse(mixer.set_muted(False)["muted"])
        mixer.lib.snd_mixer_selem_set_playback_volume_all.assert_not_called()

    def test_disconnect_or_reused_card_blocks_writes(self):
        for devices in ([], [audio.Device(0, Path("/synthetic/card0"), 124)]):
            mixer, _, _ = fixture_mixer()
            mixer.finder.return_value = devices
            with self.assertRaises(OSError):
                mixer.set_volume(50)
            with self.assertRaises(OSError):
                mixer.set_muted(False)
            mixer.lib.snd_mixer_selem_set_playback_volume_all.assert_not_called()
            mixer.lib.snd_mixer_selem_set_playback_switch_all.assert_not_called()

    def test_missing_removed_control_and_read_errors_do_not_write(self):
        for change in ("snd_mixer_find_selem", "snd_mixer_selem_has_playback_volume",
                       "snd_mixer_selem_get_playback_volume"):
            mixer, _, _ = fixture_mixer()
            method = getattr(mixer.lib, change)
            method.side_effect = None
            method.return_value = -19 if change.endswith("get_playback_volume") else 0
            with self.assertRaises(OSError):
                mixer.set_volume(50)
            mixer.lib.snd_mixer_selem_set_playback_volume_all.assert_not_called()

    def test_closing_twice_releases_native_resources_only_once(self):
        mixer, _, _ = fixture_mixer()
        mixer.close()
        mixer.close()
        mixer.lib.snd_mixer_close.assert_called_once()
        mixer.lib.snd_mixer_selem_id_free.assert_called_once()

    def test_absence_and_ambiguity_do_not_open_an_alsa_mixer(self):
        profile = audio.Profile(0x8086, 0x0808, "Speaker", 0)
        finder, factory = Mock(), Mock()
        sample = audio.AudioStatus(profile=profile, finder=finder, factory=factory)
        with patch.object(audio, "ALSA") as native:
            finder.return_value = []
            self.assertEqual(sample.sample(), {"status": "absent"})
            finder.return_value = [Mock(), Mock()]
            self.assertEqual(sample.sample(), {"status": "unavailable"})
            native.assert_not_called()
        factory.assert_not_called()

    def test_alsa_failure_is_unknown_instead_of_absent_or_zero(self):
        sample = audio.AudioStatus(profile=audio.Profile(0x8086, 0x0808, "Speaker", 0),
                                   finder=Mock(return_value=[Mock()]))
        with patch.object(audio, "ALSA", side_effect=OSError("test failure")):
            self.assertEqual(sample.sample(), {"status": "unavailable"})


if __name__ == "__main__":
    unittest.main()
