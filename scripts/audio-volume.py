#!/usr/bin/python3
"""On-demand GTK3 slider for the selected USB playback output."""
import importlib.util
import os
from pathlib import Path
import sys

APP_ID = "local.bgh.AudioVolume"


def audio_module():
    spec = importlib.util.spec_from_file_location("audio_control", Path(__file__).with_name("audio-control.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gtk_modules():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gio, GLib, Gtk
    return Gdk, Gio, GLib, Gtk


def open_mixer(audio):
    profile = audio.load_profile()
    devices = audio.find_devices(profile)
    if not devices:
        raise OSError("No matching USB audio output is connected.")
    if len(devices) != 1:
        raise OSError("Multiple matching USB outputs. Connect only one to adjust volume.")
    return audio.Mixer(profile, devices[0])


def build_window(application):
    Gdk, _, GLib, Gtk = gtk_modules()
    window = Gtk.ApplicationWindow(application=application, title="USB audio volume")
    window.set_name("bgh-audio-volume")
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_default_size(360, -1)
    window.set_border_width(16)
    css = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "calendar/calendar.css"
    provider = Gtk.CssProvider()
    try:
        provider.load_from_path(str(css))
    except GLib.Error:
        print("Audio panel theme unavailable; using the GTK fallback.", file=sys.stderr)
    else:
        Gtk.StyleContext.add_provider_for_screen(window.get_screen(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    title = Gtk.Label(label="USB audio volume")
    title.set_name("audio-volume-title")
    box.pack_start(title, False, False, 0)
    message = Gtk.Label()
    message.set_line_wrap(True)
    message.set_max_width_chars(38)
    message.set_justify(Gtk.Justification.CENTER)
    box.pack_start(message, False, False, 0)
    mixer = None
    try:
        mixer = open_mixer(audio_module())
        state = mixer.read()
    except (OSError, ValueError, AttributeError) as error:
        if mixer:
            mixer.close()
            mixer = None
        message.set_text(str(error))

    if mixer:
        row = Gtk.Box(spacing=12)
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_draw_value(False)
        scale.set_hexpand(True)
        scale.set_value(state["percentage"])
        percentage = Gtk.Label(label=f'{state["percentage"]}%')
        percentage.set_width_chars(5)
        row.pack_start(scale, True, True, 0)
        row.pack_start(percentage, False, False, 0)
        box.pack_start(row, False, False, 0)
        mute = Gtk.CheckButton(label="Mute")
        mute.set_active(state["muted"])
        mute.set_sensitive(state["can_mute"])
        box.pack_start(mute, False, False, 0)
        message.set_text("Changes apply immediately.")

        def change(action):
            try:
                current = action()
                percentage.set_text(f'{current["percentage"]}%')
            except (OSError, ValueError):
                scale.set_sensitive(False)
                mute.set_sensitive(False)
                message.set_text("USB audio changed or is unavailable. Close and reopen this panel.")

        # Connect after initial values: merely opening never writes or unmutes.
        scale.connect("value-changed", lambda widget: change(lambda: mixer.set_volume(widget.get_value())))
        mute.connect("toggled", lambda widget: change(lambda: mixer.set_muted(widget.get_active())))
        window.connect("destroy", lambda *_: mixer.close())
        window.connect("map", lambda *_: scale.grab_focus())

    close = Gtk.Button(label="Close")
    close.connect("clicked", lambda *_: window.destroy())
    box.pack_start(close, False, False, 0)
    hint = Gtk.Label(label="Left / Right: volume    Esc: close")
    hint.set_name("audio-volume-hint")
    box.pack_start(hint, False, False, 0)

    def key_press(_, event):
        if event.keyval == Gdk.KEY_Escape:
            window.destroy()
            return True
        return False

    window.connect("key-press-event", key_press)
    window.add(box)
    return window


def activate(application):
    window = application.get_active_window()
    if window:
        window.destroy()
    else:
        window = build_window(application)
        window.show_all()
        window.present()


def main():
    if not os.environ.get("DISPLAY"):
        print("An X11 session is required for the audio volume panel.", file=sys.stderr)
        return 1
    os.environ.update(GDK_BACKEND="x11", LANG="en_US.UTF-8", LANGUAGE="en_US:en", LC_ALL="en_US.UTF-8")
    try:
        Gdk, Gio, GLib, Gtk = gtk_modules()
    except (ImportError, ValueError):
        print("Audio volume requires python3-gi and gir1.2-gtk-3.0.", file=sys.stderr)
        return 1
    GLib.set_application_name("USB audio volume")
    GLib.set_prgname("bgh-audio-volume")
    Gdk.set_program_class("BGH-Audio-Volume")
    application = Gtk.Application(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
    application.connect("activate", activate)
    return application.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
