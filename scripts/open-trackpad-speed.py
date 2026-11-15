#!/usr/bin/python3
"""GTK panel for the Bluetooth Magic Trackpad 2 in the current Xorg session."""
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import NamedTuple


SPEED = "libinput Accel Speed"
PRESETS = (("Slowest", -1.0), ("Slower", -0.5), ("Slightly slower", -0.25),
           ("Default", None), ("Slightly faster", 0.25), ("Faster", 0.5),
           ("Fastest", 1.0))
MAGIC_TRACKPAD = (0x0005, 0x004c, 0x0265)
TITLE = "Trackpad speed"
APP_ID = "local.bgh.TrackpadSpeed"


class Device(NamedTuple):
    xid: str
    node: str
    sysfs: Path
    speed: float
    default: float


def event_nodes(root):
    devices = {}
    for event in root.glob("event*"):
        if not re.fullmatch(r"event[0-9]+", event.name):
            continue
        try:
            dev = event / "device"
            identity = tuple(int((dev / "id" / key).read_text(), 16)
                             for key in ("bustype", "vendor", "product"))
            if identity == MAGIC_TRACKPAD and (dev / "device/driver").resolve(strict=True).name == "magicmouse":
                devices["/dev/input/" + event.name] = event.resolve(strict=True)
        except (OSError, ValueError):
            continue
    return devices


def property_value(properties, name):
    values = re.findall(r"^\s*" + re.escape(name) + r" \([0-9]+\):[ \t]*(.+)$",
                        properties, flags=re.MULTILINE)
    return values[0].strip() if len(values) == 1 else ""


def xinput(*args):
    return subprocess.run(["xinput", *args], stdin=subprocess.DEVNULL,
                          capture_output=True, text=True, timeout=2,
                          env=dict(os.environ, LC_ALL="C"))


def find_device(root=Path("/sys/class/input"), command=xinput):
    nodes = event_nodes(root)
    if not nodes:
        return None
    ids = command("list", "--id-only")
    if ids.returncode:
        return None
    xids = ids.stdout.split()
    if len(xids) > 64 or any(not re.fullmatch(r"[0-9]+", xid) for xid in xids):
        return None
    matches = []
    for xid in xids:
        data = command("list-props", xid)
        if data.returncode:
            continue
        props = data.stdout
        node = property_value(props, "Device Node").strip('"')
        if node not in nodes:
            continue
        profile = re.sub(r"\s+", "", property_value(props, "libinput Accel Profile Enabled"))
        if profile not in ("1,0,0", "0,1,0", "1,0", "0,1"):
            continue
        try:
            speed = float(property_value(props, SPEED))
            default = float(property_value(props, SPEED + " Default"))
        except ValueError:
            continue
        if -1 <= speed <= 1 and -1 <= default <= 1:
            matches.append(Device(xid, node, nodes[node], speed, default))
    return matches[0] if len(matches) == 1 else None


def speed_rows(device):
    rows = [(label, device.default if value is None else value) for label, value in PRESETS]
    selected = min(range(len(rows)),
                   key=lambda i: (abs(device.speed - rows[i][1]), PRESETS[i][1] is not None))
    return rows, selected


def apply_speed(device, value, find=find_device, command=xinput):
    # Device IDs and nodes can be reused after unplug; re-resolve before any write.
    if not -1 <= value <= 1 or find() != device:
        return False
    if value == device.speed:
        return True
    return command("set-prop", device.xid, SPEED, f"{value:.6f}").returncode == 0


def confirm_speed(window, message, device, value, apply=apply_speed):
    try:
        success = apply(device, value)
    except (OSError, subprocess.SubprocessError):
        success = False
    if success:
        window.destroy()
    else:
        message.set_text("Trackpad changed or speed could not be set. Reopen to try again.")
    return success


def gtk_modules():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gio, GLib, Gtk
    return Gdk, Gio, GLib, Gtk


def build_window(application):
    Gdk, _, GLib, Gtk = gtk_modules()
    window = Gtk.ApplicationWindow(application=application, title=TITLE)
    window.set_name("bgh-trackpad-speed")
    window.set_decorated(False)
    window.set_resizable(False)
    window.set_default_size(360, -1)
    window.set_border_width(16)
    css = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")) / "calendar/calendar.css"
    provider = Gtk.CssProvider()
    try:
        provider.load_from_path(str(css))
    except GLib.Error:
        print("Status panel theme unavailable; using the GTK fallback.", file=sys.stderr)
    else:
        Gtk.StyleContext.add_provider_for_screen(window.get_screen(), provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    title = Gtk.Label(label=TITLE)
    title.set_name("trackpad-speed-title")
    box.pack_start(title, False, False, 0)
    message = Gtk.Label()
    message.set_line_wrap(True)
    message.set_max_width_chars(39)
    message.set_justify(Gtk.Justification.CENTER)
    box.pack_start(message, False, False, 0)
    try:
        device = find_device()
        text = f"Current: {device.speed:+.2f}  •  Until reconnect" if device else (
            "No connected Bluetooth Magic Trackpad 2 with speed control.")
    except FileNotFoundError:
        device, text = None, "Trackpad speed requires xinput."
    except (OSError, subprocess.SubprocessError):
        device, text = None, "Could not read the trackpad speed from Xorg."
    message.set_text(text)

    buttons = Gtk.Box(spacing=8)
    close = Gtk.Button(label="Close")
    close.connect("clicked", lambda _: window.destroy())
    apply = None
    choose = None
    if device is not None:
        rows, selected = speed_rows(device)
        choices = Gtk.ListBox()
        choices.set_activate_on_single_click(False)
        choices.set_selection_mode(Gtk.SelectionMode.SINGLE)
        for label, value in rows:
            row = Gtk.ListBoxRow()
            row.set_activatable(False)
            line = Gtk.Box(spacing=12)
            line.pack_start(Gtk.Label(label=label, xalign=0), True, True, 0)
            line.pack_end(Gtk.Label(label=f"{value:+.2f}", xalign=1), False, False, 0)
            row.add(line)
            choices.add(row)
        initial = choices.get_row_at_index(selected)
        choices.select_row(initial)
        window.connect("map", lambda _: initial.grab_focus())
        box.pack_start(choices, True, True, 0)

        def choose(*_):
            row = choices.get_selected_row()
            if row is not None:
                confirm_speed(window, message, device, rows[row.get_index()][1])

        apply = Gtk.Button(label="Apply")
        apply.connect("clicked", choose)
        buttons.pack_start(apply, True, True, 0)
    buttons.pack_start(close, True, True, 0)
    box.pack_start(buttons, False, False, 0)
    hint = Gtk.Label(label="↑/↓: select   Enter: apply   Esc: close" if device else "Esc: close")
    hint.set_name("trackpad-speed-hint")
    box.pack_start(hint, False, False, 0)

    def key_press(_, event):
        if event.keyval == Gdk.KEY_Escape:
            window.destroy()
            return True
        if (choose is not None and event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter)
                and window.get_focus() not in (apply, close)):
            choose()
            return True
        return False

    window.connect("key-press-event", key_press)
    window.add(box)
    return window


def activate(application):
    window = application.get_active_window()
    if window is not None:
        window.destroy()
        return
    window = build_window(application)
    window.show_all()
    window.present()


def main():
    if not os.environ.get("DISPLAY"):
        print("An X11 session is required to open the trackpad speed panel.", file=sys.stderr)
        return 1
    os.environ.update(GDK_BACKEND="x11", LANG="en_US.UTF-8", LANGUAGE="en_US:en", LC_ALL="en_US.UTF-8")
    try:
        Gdk, Gio, GLib, Gtk = gtk_modules()
    except (ImportError, ValueError):
        print("Trackpad speed requires python3-gi and gir1.2-gtk-3.0.", file=sys.stderr)
        return 1
    GLib.set_application_name(TITLE)
    GLib.set_prgname("bgh-trackpad-speed")
    Gdk.set_program_class("BGH-Trackpad-Speed")
    application = Gtk.Application(application_id=APP_ID, flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
    application.connect("activate", activate)
    return application.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
