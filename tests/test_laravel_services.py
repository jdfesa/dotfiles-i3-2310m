"""Exercise fixed service actions and read-only state handling without root."""
import importlib.util
from pathlib import Path
import subprocess
import shutil
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


panel = module("laravel_services", "scripts/laravel-services.py")
installer = module("install_laravel", "tools/install-laravel-stack.py")


class ServiceTests(unittest.TestCase):
    def test_actions_cannot_target_other_units_or_interpolate_shell(self):
        for action, unit in (("restart", "mariadb.service"), ("start", "ssh.service"),
                             ("stop; true", "mariadb.service"), ("start", "mariadb.service; true")):
            with self.subTest(action=action, unit=unit), self.assertRaises(ValueError):
                panel.service_command(action, unit)
        self.assertEqual(panel.service_command("stop", "mariadb.service"),
                         ["/usr/bin/sudo", "--", "/usr/bin/systemctl", "stop", "mariadb.service"])

    def test_state_queries_report_actual_state_and_missing_units(self):
        output = ("Id=mariadb.service\nLoadState=loaded\nActiveState=active\n\n"
                  "Id=laravel-phpmyadmin.service\nLoadState=not-found\nActiveState=inactive\n")
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, output, "")) as run:
            self.assertEqual(panel.service_states(), {"mariadb.service": "active",
                                                     "laravel-phpmyadmin.service": "Not installed"})
        self.assertNotIn("sudo", " ".join(run.call_args.args[0]))
        self.assertFalse(run.call_args.kwargs.get("shell", False))

    def test_failed_service_query_does_not_report_stopped_or_active(self):
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1, "", "no bus")):
            self.assertEqual(set(panel.service_states().values()), {"Unavailable"})

    def test_cancelled_sudo_is_not_reported_as_success(self):
        with patch.object(panel.subprocess, "run", return_value=
                          subprocess.CompletedProcess([], 1)), patch.object(panel.sys.stdin, "isatty", return_value=False):
            self.assertEqual(panel.run_action("start", "mariadb.service"), 1)


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


@unittest.skipUnless(shutil.which("php"), "PHP is required for the real router parser")
class RouterTests(unittest.TestCase):
    def route(self, path):
        code = '''
$_SERVER['REQUEST_URI'] = $argv[1];
register_shutdown_function(function() { echo 'STATUS:' . (http_response_code() ?: 200); });
$r = include $argv[2];
if ($r === false) { echo 'FORWARD:'; }
'''
        result = subprocess.run(["php", "-r", code, path,
                                 str(ROOT / "config/laravel/phpmyadmin-router.php")],
                                capture_output=True, text=True, check=True)
        return result.stdout

    def test_required_dynamic_entrypoints_are_forwarded(self):
        for path in ("/", "/index.php?route=/", "/url.php", "/js/messages.php?lang=en"):
            with self.subTest(path=path):
                self.assertEqual(self.route(path), "FORWARD:STATUS:200")

    def test_private_paths_setup_and_traversal_remain_inaccessible(self):
        for path in ("/setup/index.php", "/libraries/classes/Config.php", "/vendor/autoload.php",
                     "/config.inc.php", "/js/unknown.php", "/js/../config.inc.php",
                     "/js/%2e%2e/config.inc.php", "/js/test%00.js", "/js/..%5cconfig.inc.php"):
            with self.subTest(path=path):
                self.assertEqual(self.route(path), "STATUS:404")


if __name__ == "__main__":
    unittest.main()
