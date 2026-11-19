"""Exercise fixed service actions and read-only state handling without root."""
import importlib.util
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


panel = module("web_stack_control", "scripts/web-stack-control.py")
entry = module("laravel_services", "scripts/laravel-services.py")
installer = module("install_laravel", "tools/install-laravel-stack.py")


class ServiceTests(unittest.TestCase):
    def test_status_cli_is_headless_and_reports_unavailable_as_failure(self):
        for state, expected in (("inactive", 0), ("Unavailable", 1)):
            with self.subTest(state=state), patch.object(sys, "argv", ["panel", "--status"]), \
                    patch.object(entry, "load_module", return_value=panel) as load, \
                    patch.object(panel, "service_states", return_value={unit: state for unit in panel.SERVICES}), \
                    patch.object(sys, "stdout", new_callable=io.StringIO):
                self.assertEqual(entry.main(), expected)
            load.assert_called_once_with("web-stack-control.py")

    def test_actions_cannot_target_other_units_or_interpolate_shell(self):
        for action, unit in (("reload", "mariadb.service"), ("start", "ssh.service"),
                             ("stop; true", "mariadb.service"), ("start", "mariadb.service; true")):
            with self.subTest(action=action, unit=unit), self.assertRaises(ValueError):
                panel.service_command(action, unit)
        self.assertEqual(panel.service_command("stop", "mariadb.service"),
                         ["/usr/bin/systemctl", "--no-ask-password", "stop", "mariadb.service"])

    def test_all_action_has_only_the_reviewed_units(self):
        self.assertEqual(panel.service_command("restart", "all"),
                         ["/usr/bin/systemctl", "--no-ask-password", "restart",
                          "apache2.service", "mariadb.service"])

    def test_state_queries_report_actual_state_and_missing_units(self):
        output = ("Id=mariadb.service\nLoadState=loaded\nActiveState=active\nMainPID=4321\n\n"
                  "Id=apache2.service\nLoadState=not-found\nActiveState=inactive\nMainPID=0\n")
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, output, "")) as run:
            self.assertEqual(panel.service_info(), {
                "mariadb.service": {"state": "active", "pid": "4321"},
                "apache2.service": {"state": "Not installed", "pid": "—"}})
        self.assertNotIn("sudo", " ".join(run.call_args.args[0]))
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_failed_service_query_does_not_report_stopped_or_active(self):
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, "", "no bus")):
            self.assertEqual(set(panel.service_states().values()), {"Unavailable"})

    def test_denied_action_is_not_reported_as_success(self):
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1)):
            self.assertEqual(panel.run_action("start", "mariadb.service"), 1)

    def test_log_tail_bounds_bytes_and_lines(self):
        with tempfile.TemporaryDirectory() as temporary:
            log = Path(temporary) / "error.log"
            log.write_text("discard\n" * 20000 + "recent1\nrecent2\n")
            self.assertEqual(panel.read_tail(log, limit=64, lines=2), "recent1\nrecent2")

    def test_configuration_cannot_read_an_arbitrary_path(self):
        with self.assertRaises(ValueError):
            panel.configuration("/etc/shadow")

    def test_listener_inspection_only_reads_the_stack_ports(self):
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 0, "listeners\n")) as run:
            self.assertEqual(panel.listening_ports(), "listeners\n")
        command = run.call_args.args[0]
        self.assertEqual(command[0], "/usr/bin/ss")
        self.assertIn("sport = :80 or sport = :8080 or sport = :3306", command[-1])
        self.assertFalse(run.call_args.kwargs.get("shell", False))


class InstallerTests(unittest.TestCase):
    def test_local_admin_sql_preserves_socket_authentication(self):
        sql = installer.login_sql("synthetic'\\value")
        self.assertIn("SET SESSION sql_mode='NO_BACKSLASH_ESCAPES'", sql)
        self.assertIn("IDENTIFIED BY 'synthetic''\\value'", sql)
        self.assertIn("'root'@'127.0.0.1'", sql)
        self.assertIn("GRANT ALL PRIVILEGES ON *.*", sql)
        self.assertIn("SET PASSWORD FOR 'root'@'localhost'", sql)
        self.assertNotIn("ALTER USER 'root'@'localhost'", sql)
        self.assertNotIn("'root'@'%'", sql)

    def test_alternate_native_authentication_is_not_lost(self):
        # MariaDB plugin identifiers, not passwords or account records.
        native = {"plugin": "mysql_native_password", "auth_or": [{}, {"plugin": "unix_socket"}]}
        self.assertEqual(installer.authentication_plugins(native), {"mysql_native_password", "unix_socket"})

    def test_password_file_must_be_private_and_external(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "password"
            path.write_text("synthetic-local-password\n")
            path.chmod(0o600)
            self.assertEqual(installer.password_input(path), "synthetic-local-password")
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "private mode600"):
                installer.password_input(path)

    def test_simulation_has_no_mutating_commands(self):
        with patch.object(installer, "run") as run, patch.object(installer, "regular_parents"):
            installer.plan()
        self.assertEqual(run.call_count, 1)
        command = run.call_args.args[0]
        self.assertEqual(command[:2], ["/usr/bin/apt-get", "-s"])
        self.assertIn("--no-remove", command)
        self.assertIn("--no-install-recommends", command)

    def test_symlinked_system_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "real").mkdir()
            (root / "link").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaises(ValueError):
                installer.regular_parents(root / "link/file")

    def test_existing_private_credentials_are_not_overwritten(self):
        from types import SimpleNamespace
        import os
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            directory = home / ".local/state/laravel-development"
            directory.mkdir(parents=True, mode=0o700)
            credentials = directory / "database.env"
            credentials.write_text("synthetic credential fixture\n")
            credentials.chmod(0o600)
            account = SimpleNamespace(pw_dir=str(home), pw_uid=os.getuid(), pw_gid=os.getgid())
            with patch.object(installer, "run") as run:
                installer.create_database(account)
            run.assert_not_called()
            self.assertEqual(credentials.read_text(), "synthetic credential fixture\n")


if __name__ == "__main__":
    unittest.main()
