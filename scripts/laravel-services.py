#!/usr/bin/python3
"""On-demand GTK controls for the fixed local Apache/PHP and MariaDB stack."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SERVICES = {"apache2.service": "Apache / PHP", "mariadb.service": "MariaDB"}
PORTS = {"apache2.service": "80, 8080", "mariadb.service": "3306"}
LOGS = {"apache2.service": Path("/var/log/apache2/error.log"),
        "mariadb.service": Path("/var/log/mysql/error.log")}
CONFIGS = {
    "apache2.service": [Path("/etc/apache2/ports.conf"),
                        Path("/etc/apache2/conf-available/bgh-web-stack.conf"),
                        Path("/etc/phpmyadmin/conf.d/90-laravel-local.php")],
    "mariadb.service": [Path("/etc/mysql/mariadb.conf.d/90-laravel-local.cnf")],
}
URL = "http://127.0.0.1/phpmyadmin/"
WEB_ROOT = "/var/www/html"


def service_command(action, unit):
    if action not in ("start", "stop", "restart") or unit not in (*SERVICES, "all"):
        raise ValueError("Unsupported service action")
    targets = list(SERVICES) if unit == "all" else [unit]
    return ["/usr/bin/systemctl", "--no-ask-password", action, *targets]


def service_info():
    result = subprocess.run(
        ["/usr/bin/systemctl", "show", "--no-pager",
         "--property=Id,LoadState,ActiveState,MainPID", *SERVICES],
        capture_output=True, text=True, timeout=5, check=False)
    info = {unit: {"state": "Unavailable", "pid": "—"} for unit in SERVICES}
    for block in result.stdout.strip().split("\n\n"):
        fields = dict(line.split("=", 1) for line in block.splitlines() if "=" in line)
        unit = fields.get("Id")
        if unit in info:
            state = ("Not installed" if fields.get("LoadState") == "not-found"
                     else fields.get("ActiveState", "Unavailable"))
            info[unit] = {"state": state, "pid": fields.get("MainPID", "0") if state == "active" else "—"}
    return info


def service_states():
    return {unit: details["state"] for unit, details in service_info().items()}


def run_action(action, unit):
    return subprocess.run(service_command(action, unit), check=False).returncode


def read_tail(path, limit=65536, lines=120):
    with path.open("rb") as stream:
        stream.seek(0, 2)
        stream.seek(max(0, stream.tell() - limit))
        data = stream.read(limit)
    return "\n".join(data.decode("utf-8", errors="replace").splitlines()[-lines:])


def configuration(unit):
    if unit not in CONFIGS:
        raise ValueError("Unsupported service")
    return "\n\n".join("# " + str(path) + "\n" + path.read_text() for path in CONFIGS[unit])


def gui():
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, GLib, Gtk

    Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
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
        box.pack_start(Gtk.Label(label="Apache + PHP 8.4 · MariaDB · phpMyAdmin"), False, False, 0)
        labels, pids, ports, controls = {}, {}, {}, []
        busy = [False]
        hint = Gtk.Label(label="Services start only when requested.")
        hint.set_name("laravel-hint")
        hint.set_line_wrap(True)
        open_admin = Gtk.Button(label="Open phpMyAdmin")
        open_site = Gtk.Button(label="Open localhost")

        def details(title_text, loader):
            dialog = Gtk.Dialog(title=title_text, transient_for=window)
            dialog.set_name("bgh-laravel-services")
            dialog.set_default_size(760, 420)
            dialog.add_button("Refresh", 1)
            dialog.add_button("Close", Gtk.ResponseType.CLOSE)
            text = Gtk.TextView(editable=False, cursor_visible=False, monospace=True)
            scroll = Gtk.ScrolledWindow()
            scroll.add(text)
            dialog.get_content_area().pack_start(scroll, True, True, 8)
            def load():
                try:
                    content = loader()
                except (OSError, ValueError) as error:
                    content = str(error)
                text.get_buffer().set_text(content or "No messages.")
            load()
            dialog.show_all()
            while dialog.run() == 1:
                load()
            dialog.destroy()

        def refresh(*_):
            try:
                info = service_info()
            except (OSError, subprocess.TimeoutExpired):
                info = {unit: {"state": "Unavailable", "pid": "—"} for unit in SERVICES}
            for unit, label in labels.items():
                label.set_text(info[unit]["state"])
                pids[unit].set_text(info[unit]["pid"])
                ports[unit].set_text(PORTS[unit] if info[unit]["state"] == "active" else "—")
            enabled = info["apache2.service"]["state"] == "active" and not busy[0]
            open_admin.set_sensitive(enabled)
            open_site.set_sensitive(enabled)

        def action(_, verb, unit):
            if busy[0]:
                return
            busy[0] = True
            for control in controls:
                control.set_sensitive(False)
            hint.set_text(verb.title() + " in progress…")
            try:
                process = subprocess.Popen(service_command(verb, unit),
                                           stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            except OSError as error:
                busy[0] = False
                hint.set_text(str(error))
                for control in controls:
                    control.set_sensitive(True)
                return

            def finished(_pid, status):
                process.returncode = os.waitstatus_to_exitcode(status)
                error = process.stderr.read(4096).strip()
                process.stderr.close()
                busy[0] = False
                for control in controls:
                    control.set_sensitive(True)
                refresh()
                hint.set_text("Status refreshed." if process.returncode == 0 else
                              (error or "Service action failed."))
            GLib.child_watch_add(process.pid, finished)

        grid = Gtk.Grid(column_spacing=10, row_spacing=12)
        for column, label in enumerate(("Service", "Status", "PID", "Ports")):
            grid.attach(Gtk.Label(label=label, xalign=0), column, 0, 1, 1)
        for row, (unit, name) in enumerate(SERVICES.items(), start=1):
            labels[unit] = Gtk.Label(label="Checking…", xalign=0)
            pids[unit] = Gtk.Label(label="—", xalign=0)
            ports[unit] = Gtk.Label(label="—", xalign=0)
            for column, label in enumerate((Gtk.Label(label=name, xalign=0), labels[unit], pids[unit], ports[unit])):
                grid.attach(label, column, row, 1, 1)
            for column, verb in enumerate(("start", "stop", "restart"), start=4):
                button = Gtk.Button(label=verb.title())
                button.connect("clicked", action, verb, unit)
                controls.append(button)
                grid.attach(button, column, row, 1, 1)
            logs = Gtk.Button(label="Logs")
            logs.connect("clicked", lambda _, u=unit: details(SERVICES[u] + " — Logs", lambda: read_tail(LOGS[u])))
            config = Gtk.Button(label="Config")
            config.connect("clicked", lambda _, u=unit: details(SERVICES[u] + " — Configuration (read-only)", lambda: configuration(u)))
            grid.attach(logs, 7, row, 1, 1)
            grid.attach(config, 8, row, 1, 1)
        box.pack_start(grid, False, False, 0)
        all_buttons = Gtk.Box(spacing=10)
        for verb in ("start", "stop", "restart"):
            button = Gtk.Button(label=verb.title() + " all")
            button.connect("clicked", action, verb, "all")
            controls.append(button)
            all_buttons.pack_start(button, True, True, 0)
        box.pack_start(all_buttons, False, False, 0)
        links = Gtk.Box(spacing=10)
        open_admin.connect("clicked", lambda _: subprocess.Popen(["/usr/bin/xdg-open", URL]))
        open_site.connect("clicked", lambda _: subprocess.Popen(["/usr/bin/xdg-open", "http://127.0.0.1/"]))
        links.pack_start(open_site, True, True, 0)
        links.pack_start(open_admin, True, True, 0)
        box.pack_start(links, False, False, 0)
        box.pack_start(hint, False, False, 0)
        buttons = Gtk.Box(spacing=10)
        folder = Gtk.Button(label="Web root")
        folder.connect("clicked", lambda _: subprocess.Popen(["/usr/bin/xdg-open", WEB_ROOT]))
        terminal = Gtk.Button(label="Terminal")
        terminal.connect("clicked", lambda _: subprocess.Popen(["/usr/bin/kitty", "--directory", WEB_ROOT]))
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", refresh)
        controls.append(refresh_button)
        close = Gtk.Button(label="Close")
        close.connect("clicked", lambda _: window.close())
        for button in (folder, terminal, refresh_button, close):
            buttons.pack_start(button, True, True, 0)
        box.pack_start(buttons, False, False, 0)
        window.add(box)
        window.connect("delete-event", lambda *_: busy[0])
        window.connect("key-press-event", lambda _, event:
                       window.close() if event.keyval == Gdk.KEY_Escape else False)
        refresh()
        window.show_all()
        def center():
            monitor = window.get_display().get_monitor_at_window(window.get_window())
            area = monitor.get_workarea()
            width, height = window.get_size()
            window.move(area.x + max(0, (area.width - width) // 2),
                        area.y + max(0, (area.height - height) // 2))
            return False
        GLib.idle_add(center)

    app.connect("activate", activate)
    return app.run([])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status", action="store_true", help="Read service states without opening a window")
    parser.add_argument("--service-action", nargs=2, metavar=("ACTION", "UNIT"), help=argparse.SUPPRESS)
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
