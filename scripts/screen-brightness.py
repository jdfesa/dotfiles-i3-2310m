#!/usr/bin/python3
"""Read the BGH internal backlight and open its on-demand GTK3 control."""
import os
from pathlib import Path
import sys

DEVICE = "acpi_video0"
BACKLIGHT = Path("/sys/class/backlight") / DEVICE
LOGIN1 = "org.freedesktop.login1"
SESSION = "/org/freedesktop/login1/session/auto"


def read_level(device=BACKLIGHT):
    if (device / "type").read_text().strip() != "firmware":
        raise ValueError("Unexpected backlight type.")
    maximum = int((device / "max_brightness").read_text())
    level = int((device / "actual_brightness").read_text())
    if not 1 <= maximum <= 0xFFFFFFFF or not 0 <= level <= maximum:
        raise ValueError("Invalid backlight level.")
    return level, maximum


def percentage(level, maximum):
    return (100 * level + maximum // 2) // maximum


def sample():
    try:
        return percentage(*read_level())
    except (OSError, ValueError):
        return None


def write_level(level, expected_maximum, request, device=BACKLIGHT):
    _, maximum = read_level(device)
    if maximum != expected_maximum or type(level) is not int or not 1 <= level <= maximum:
        raise ValueError("Backlight changed or requested level is invalid.")
    request(level)
    current, maximum = read_level(device)
    if maximum != expected_maximum or current != level:
        raise OSError("Backlight did not report the requested level.")
    return percentage(current, maximum)


def request_brightness(Gio, GLib, level):
    bus = Gio.bus_get_sync(Gio.BusType.SYSTEM)
    bus.call_sync(LOGIN1, SESSION, LOGIN1 + ".Session", "SetBrightness",
                  GLib.Variant("(ssu)", ("backlight", DEVICE, level)),
                  None, Gio.DBusCallFlags.NONE, 1000, None)


def build_window(application, Gdk, Gio, GLib, Gtk):
    window = Gtk.ApplicationWindow(application=application, title="Screen brightness")
    window.set_name("bgh-screen-brightness")
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_default_size(360, -1)
    window.set_border_width(16)
    css = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "calendar/calendar.css"
    provider = Gtk.CssProvider()
    try:
        provider.load_from_path(str(css))
    except GLib.Error:
        print("Brightness panel theme unavailable; using the GTK fallback.", file=sys.stderr)
    else:
        Gtk.StyleContext.add_provider_for_screen(window.get_screen(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    title = Gtk.Label(label="Screen brightness")
    title.set_name("screen-brightness-title")
    content.pack_start(title, False, False, 0)
    hint = Gtk.Label(label="Left / Right: brightness    Esc: close")
    hint.set_name("screen-brightness-hint")
    close = Gtk.Button(label="Close")
    close.connect("clicked", lambda *_: window.destroy())
    try:
        current, maximum = read_level()
    except (OSError, ValueError):
        hint.set_text("Screen brightness is unavailable.")
        window.set_focus(close)
    else:
        row = Gtk.Box(spacing=12)
        adjustment = Gtk.Adjustment(value=current, lower=0, upper=maximum,
                                    step_increment=1, page_increment=1)
        scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adjustment)
        scale.set_draw_value(False)
        scale.set_digits(0)
        scale.set_hexpand(True)
        scale.get_accessible().set_name("Screen brightness")
        label = Gtk.Label(label=f"{percentage(current, maximum)}%")
        label.set_width_chars(4)
        row.pack_start(scale, True, True, 0)
        row.pack_start(label, False, False, 0)
        content.pack_start(row, False, False, 0)

        def change(widget):
            nonlocal current
            target = max(1, round(widget.get_value()))
            if target != widget.get_value():
                widget.handler_block(handler)
                widget.set_value(target)
                widget.handler_unblock(handler)
            if target == current:
                return
            try:
                applied = write_level(target, maximum, lambda level: request_brightness(Gio, GLib, level))
            except (OSError, ValueError, GLib.Error):
                label.set_text("--%")
                hint.set_text("Could not set brightness. Close and reopen.")
                scale.set_sensitive(False)
            else:
                current = target
                label.set_text(f"{applied}%")

        # Initializing and closing the control must not write a new level.
        handler = scale.connect("value-changed", change)
        window.connect("map", lambda *_: scale.grab_focus())

    content.pack_start(close, False, False, 0)
    content.pack_start(hint, False, False, 0)

    def key_press(_, event):
        if event.keyval == Gdk.KEY_Escape:
            window.destroy()
            return True
        return False

    window.connect("key-press-event", key_press)
    window.add(content)
    return window


def main():
    if not os.environ.get("DISPLAY"):
        print("An X11 session is required for the brightness panel.", file=sys.stderr)
        return 1
    os.environ.update(GDK_BACKEND="x11", LANG="en_US.UTF-8", LANGUAGE="en_US:en", LC_ALL="en_US.UTF-8")
    try:
        import gi
        gi.require_version("Gtk", "3.0")
        gi.require_version("Gdk", "3.0")
        from gi.repository import Gdk, Gio, GLib, Gtk
    except (ImportError, ValueError):
        print("Brightness requires python3-gi and gir1.2-gtk-3.0.", file=sys.stderr)
        return 1
    GLib.set_application_name("Screen brightness")
    GLib.set_prgname("bgh-screen-brightness")
    Gdk.set_program_class("BGH-Screen-Brightness")
    application = Gtk.Application(application_id="local.bgh.ScreenBrightness")

    def activate(app):
        window = app.get_active_window()
        if window is None:
            window = build_window(app, Gdk, Gio, GLib, Gtk)
            window.show_all()
        window.present()

    application.connect("activate", activate)
    return application.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
