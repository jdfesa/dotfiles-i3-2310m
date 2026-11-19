"""Event-driven GTK3 window for Local Web Stack; loaded only for the GUI."""
from collections import deque
import subprocess
import time

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk

HELP = """Local Web Stack

Apache serves PHP projects from /var/www/html on http://127.0.0.1/.
MariaDB provides the local database. Its Admin button opens phpMyAdmin;
both services must be running to use the database administration page.

Start, Stop and Restart affect only the selected service. The all buttons
affect both. Actions use your active local desktop session authorization.
Closing this window leaves services running. Services do not start at boot.

Status is read when opening, after actions and with Refresh; there is no
periodic polling. The activity list holds only the latest 120 lines in
memory. Logs reads recent server errors; Config is read-only. Ports reads
the actual listening sockets for ports 80, 8080 and 3306 on request.

Web root opens the project folder. Terminal opens Kitty there on request.
Installation, dependencies and recovery: docs/laravel-setup.md in the checkout.
"""


class StackWindow(Gtk.ApplicationWindow):
    def __init__(self, application, control):
        super().__init__(application=application, title="Local Web Stack")
        self.control = control
        self.process = None
        self.controls = []
        self.states, self.pids, self.ports, self.admins = {}, {}, {}, {}
        self.messages = deque(maxlen=120)
        self.set_name("bgh-laravel-services")
        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        self.set_border_width(18)
        self.connect("delete-event", lambda *_: self.process is not None)
        self.connect("key-press-event", self.key_pressed)
        css = Gtk.CssProvider()
        css.load_from_path(str(control.ROOT / "config/laravel/services.css"))
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.pack_start(Gtk.Label(label="Local Web Stack", name="laravel-title"), False, False, 0)
        box.pack_start(Gtk.Label(label="Apache + PHP 8.4 · MariaDB · phpMyAdmin"), False, False, 0)
        box.pack_start(self.service_grid(), False, False, 0)
        box.pack_start(self.global_actions(), False, False, 0)
        self.activity = Gtk.TextView(editable=False, cursor_visible=False, monospace=True)
        self.activity.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(-1, 140)
        scroll.add(self.activity)
        box.pack_start(scroll, True, True, 0)
        box.pack_start(self.utilities(), False, False, 0)
        self.add(box)
        self.refresh()
        self.record("Services start only when requested. Closing the panel keeps them running.")
        self.show_all()
        GLib.idle_add(self.center)

    @staticmethod
    def button(label, callback, *args):
        button = Gtk.Button(label=label)
        button.connect("clicked", callback, *args)
        return button

    def service_grid(self):
        grid = Gtk.Grid(column_spacing=10, row_spacing=12)
        for column, label in enumerate(("Service", "Status", "PID", "Ports")):
            grid.attach(Gtk.Label(label=label, xalign=0), column, 0, 1, 1)
        for row, (unit, name) in enumerate(self.control.SERVICES.items(), start=1):
            self.states[unit] = Gtk.Label(label="Checking…", xalign=0)
            self.pids[unit] = Gtk.Label(label="—", xalign=0)
            self.ports[unit] = Gtk.Label(label="—", xalign=0)
            self.ports[unit].set_tooltip_text("Configured ports; use Ports to inspect actual listeners.")
            for column, label in enumerate((Gtk.Label(label=name, xalign=0), self.states[unit],
                                            self.pids[unit], self.ports[unit])):
                grid.attach(label, column, row, 1, 1)
            for column, verb in enumerate(("start", "stop", "restart"), start=4):
                button = self.button(verb.title(), self.action, verb, unit)
                self.controls.append(button)
                grid.attach(button, column, row, 1, 1)
            self.admins[unit] = self.button("Admin", self.open_admin, unit)
            grid.attach(self.admins[unit], 7, row, 1, 1)
            grid.attach(self.button("Config", self.show_config, unit), 8, row, 1, 1)
            grid.attach(self.button("Logs", self.show_logs, unit), 9, row, 1, 1)
        return grid

    def global_actions(self):
        box = Gtk.Box(spacing=10)
        for verb in ("start", "stop", "restart"):
            button = self.button(verb.title() + " all", self.action, verb, "all")
            self.controls.append(button)
            box.pack_start(button, True, True, 0)
        return box

    def utilities(self):
        box = Gtk.Box(spacing=10)
        buttons = (
            self.button("Web root", self.launch, ["/usr/bin/xdg-open", self.control.WEB_ROOT]),
            self.button("Terminal", self.launch, ["/usr/bin/kitty", "--directory", self.control.WEB_ROOT]),
            self.button("Ports", self.show_ports),
            self.button("Help", self.show_help),
            self.button("Refresh", self.refresh),
            self.button("Close", lambda _: self.close()),
        )
        self.controls.append(buttons[-2])
        for button in buttons:
            box.pack_start(button, True, True, 0)
        return box

    def details(self, title, loader):
        dialog = Gtk.Dialog(title=title, transient_for=self, modal=True)
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
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                content = str(error)
            text.get_buffer().set_text(content or "No messages.")

        def response(widget, result):
            if result == 1:
                load()
            else:
                widget.destroy()

        dialog.connect("response", response)
        dialog.connect("key-press-event", lambda widget, event:
                       widget.destroy() if event.keyval == Gdk.KEY_Escape else False)
        load()
        dialog.show_all()

    def show_config(self, _, unit):
        self.details(self.control.SERVICES[unit] + " — Configuration (read-only)",
                     lambda: self.control.configuration(unit))

    def show_logs(self, _, unit):
        self.details(self.control.SERVICES[unit] + " — Logs",
                     lambda: self.control.read_tail(self.control.LOGS[unit]))

    def show_ports(self, _):
        self.details("Local Web Stack — Listening ports", self.control.listening_ports)

    def show_help(self, _):
        self.details("Local Web Stack — Help", lambda: HELP)

    def launch(self, _, command):
        try:
            subprocess.Popen(command)
        except OSError as error:
            self.record(str(error))

    def open_admin(self, button, unit):
        url = self.control.SITE_URL if unit == "apache2.service" else self.control.URL
        self.launch(button, ["/usr/bin/xdg-open", url])

    def record(self, message):
        # Errors can contain multiple lines; bound both line count and message length.
        for line in message[:4096].splitlines():
            self.messages.append(time.strftime("%H:%M:%S") + "  " + line)
        buffer = self.activity.get_buffer()
        buffer.set_text("\n".join(self.messages))
        self.activity.scroll_to_iter(buffer.get_end_iter(), 0.0, False, 0.0, 1.0)

    def refresh(self, *_):
        try:
            info = self.control.service_info()
        except (OSError, subprocess.TimeoutExpired):
            info = {unit: {"state": "Unavailable", "pid": "—"} for unit in self.control.SERVICES}
        busy = self.process is not None
        apache_active = info["apache2.service"]["state"] == "active"
        for unit, label in self.states.items():
            state = info[unit]["state"]
            label.set_text(state)
            style = label.get_style_context()
            for name in ("service-active", "service-error"):
                style.remove_class(name)
            if state == "active":
                style.add_class("service-active")
            elif state in ("failed", "Unavailable", "Not installed"):
                style.add_class("service-error")
            self.pids[unit].set_text(info[unit]["pid"])
            self.ports[unit].set_text(self.control.PORTS[unit] if state == "active" else "—")
            self.admins[unit].set_sensitive(apache_active and not busy and
                                           (unit == "apache2.service" or state == "active"))
        return info

    def set_busy(self, busy):
        for button in self.controls:
            button.set_sensitive(not busy)
        if busy:
            for button in self.admins.values():
                button.set_sensitive(False)

    def action(self, _, verb, unit):
        if self.process is not None:
            return
        name = "all services" if unit == "all" else self.control.SERVICES[unit]
        try:
            self.process = Gio.Subprocess.new(
                self.control.service_command(verb, unit),
                Gio.SubprocessFlags.STDOUT_SILENCE | Gio.SubprocessFlags.STDERR_PIPE)
        except (GLib.Error, ValueError) as error:
            self.record(str(error))
            return
        self.set_busy(True)
        self.record(f"{verb.title()}: {name}…")
        self.process.communicate_utf8_async(None, None, self.finished)

    def finished(self, process, result):
        try:
            _, _, error = process.communicate_utf8_finish(result)
            message = "Action completed." if process.get_successful() else (error.strip() or "Service action failed.")
        except GLib.Error as error:
            message = str(error)
        self.process = None
        self.set_busy(False)
        info = self.refresh()
        self.record(message)
        self.record(" · ".join(self.control.SERVICES[unit] + ": " + details["state"]
                               for unit, details in info.items()))

    def center(self):
        monitor = self.get_display().get_monitor_at_window(self.get_window())
        area = monitor.get_workarea()
        width, height = self.get_size()
        self.move(area.x + max(0, (area.width - width) // 2),
                  area.y + max(0, (area.height - height) // 2))
        return False

    def key_pressed(self, _, event):
        if event.keyval == Gdk.KEY_Escape:
            self.close()
            return True
        return False


def run(control):
    Gtk.Settings.get_default().set_property("gtk-application-prefer-dark-theme", True)
    app = Gtk.Application(application_id="local.bgh.LaravelServices")

    def activate(application):
        windows = application.get_windows()
        if windows:
            windows[0].present()
        else:
            StackWindow(application, control)

    app.connect("activate", activate)
    return app.run([])
