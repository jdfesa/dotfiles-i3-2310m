#!/usr/bin/python3
"""On-demand GTK controls for two fixed local development services; no polling."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {"mariadb.service": "MariaDB",
            "laravel-phpmyadmin.service": "phpMyAdmin"}
URL = "http://127.0.0.1:8080/"


def service_command(action, unit):
    if action not in ("start", "stop") or unit not in SERVICES:
        raise ValueError("Unsupported service action")
    return ["/usr/bin/sudo", "--", "/usr/bin/systemctl", action, unit]


def service_states():
    result = subprocess.run(
        ["/usr/bin/systemctl", "show", "--no-pager",
         "--property=Id,LoadState,ActiveState", *SERVICES],
        capture_output=True, text=True, timeout=5, check=False)
    states = {unit: "Unavailable" for unit in SERVICES}
    for block in result.stdout.strip().split("\n\n"):
        fields = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
        unit = fields.get("Id")
        if unit in states:
            states[unit] = ("Not installed" if fields.get("LoadState") == "not-found"
                            else fields.get("ActiveState", "Unavailable"))
    return states


def run_action(action, unit):
    result = subprocess.run(service_command(action, unit), check=False)
    if result.returncode and sys.stdin.isatty():
        input("Service action failed or was cancelled. Press Enter to close.")
    return result.returncode


def gui():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk

    app = Gtk.Application(application_id="local.bgh.LaravelServices")

    def activate(application):
        windows = application.get_windows()
        if windows:
            windows[0].present()
            return
        window = Gtk.ApplicationWindow(application=application, title="Local Web Stack")
        window.set_name("bgh-laravel-services")
        window.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        window.set_position(Gtk.WindowPosition.CENTER)
        window.set_resizable(False)
        window.set_border_width(18)
        css = Gtk.CssProvider()
        css.load_from_path(str(ROOT / "config/laravel/services.css"))
        Gtk.StyleContext.add_provider_for_screen(
            window.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        title = Gtk.Label(label="Local Web Stack")
        title.set_name("laravel-title")
        box.pack_start(title, False, False, 0)
        labels, controls = {}, []
        busy = [False]
        hint = Gtk.Label(label="Services start only when requested.")
        hint.set_name("laravel-hint")
        open_button = Gtk.Button(label="Open phpMyAdmin")

        def refresh(*_):
            try:
                states = service_states()
            except (OSError, subprocess.TimeoutExpired):
                states = {unit: "Unavailable" for unit in SERVICES}
            for unit, label in labels.items():
                label.set_text(states[unit])
            open_button.set_sensitive(states["laravel-phpmyadmin.service"] == "active")

        def action(_, verb, unit):
            if busy[0]:
                return
            busy[0] = True
            for control in controls:
                control.set_sensitive(False)
            hint.set_text("Complete authorization in the terminal.")
            try:
                process = subprocess.Popen(
                    ["/usr/bin/kitty", "--class", "bgh-laravel-action",
                     "--title", "Local Web Stack", sys.executable, str(Path(__file__).resolve()),
                     "--service-action", verb, unit])
            except OSError as error:
                busy[0] = False
                hint.set_text(str(error))
                for control in controls:
                    control.set_sensitive(True)
                return

            def finished(_pid, status):
                process.returncode = os.waitstatus_to_exitcode(status)
                busy[0] = False
                for control in controls:
                    control.set_sensitive(True)
                # Kitty's exit status does not prove the child action succeeded.
                refresh()
                hint.set_text("Status refreshed. Stop MariaDB also stops phpMyAdmin.")
            GLib.child_watch_add(process.pid, finished)

        grid = Gtk.Grid(column_spacing=14, row_spacing=12)
        for row, (unit, name) in enumerate(SERVICES.items()):
            label = Gtk.Label(label=name, xalign=0)
            labels[unit] = Gtk.Label(label="Checking...", xalign=0)
            grid.attach(label, 0, row, 1, 1)
            grid.attach(labels[unit], 1, row, 1, 1)
            for column, verb in enumerate(("start", "stop"), start=2):
                button = Gtk.Button(label=verb.title())
                button.connect("clicked", action, verb, unit)
                controls.append(button)
                grid.attach(button, column, row, 1, 1)
        box.pack_start(grid, False, False, 0)
        open_button.connect("clicked", lambda _: subprocess.Popen(["/usr/bin/xdg-open", URL]))
        box.pack_start(open_button, False, False, 0)
        box.pack_start(hint, False, False, 0)
        buttons = Gtk.Box(spacing=10)
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", refresh)
        controls.append(refresh_button)
        close = Gtk.Button(label="Close")
        close.connect("clicked", lambda _: window.close())
        buttons.pack_start(refresh_button, True, True, 0)
        buttons.pack_start(close, True, True, 0)
        box.pack_start(buttons, False, False, 0)
        window.add(box)
        window.connect("delete-event", lambda *_: busy[0])
        window.connect("key-press-event", lambda _, event:
                       window.close() if event.keyval == Gdk.KEY_Escape else False)
        refresh()
        window.show_all()

    app.connect("activate", activate)
    return app.run([])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true", help="Read service states without opening a window")
    parser.add_argument("--service-action", nargs=2, metavar=("ACTION", "UNIT"),
                        help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error("Run this program as your desktop account, without sudo")
    if args.service_action:
        try:
            return run_action(*args.service_action)
        except ValueError as error:
            parser.error(str(error))
    if args.status:
        for unit, state in service_states().items():
            print(f"{SERVICES[unit]}: {state}")
        return 0
    return gui()


if __name__ == "__main__":
    raise SystemExit(main())
