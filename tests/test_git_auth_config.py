"""Public Git credential-store integration contracts; no real credentials or PAM actions."""
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GitAuthenticationConfigurationTests(unittest.TestCase):
    def test_authentication_sources_have_explicit_system_destinations(self):
        entries = {item["source"]: item for item in json.loads((ROOT / "config/manifest.json").read_text())}
        expected = {
            "config/login-keyring.pam": "/etc/pam.d/login-keyring",
            "config/keyring-secrets-only.conf": "/etc/systemd/user/gnome-keyring-daemon.service.d/10-secrets-only.conf",
            "config/xsession-keyring.sh": "/etc/X11/Xsession.d/95keyring-secrets",
        }
        for source, destination in expected.items():
            self.assertEqual(entries[source]["destination"], destination)
            self.assertEqual(entries[source]["mode"], 0o644)

    def test_keyring_pam_hooks_are_optional_not_authentication_grants(self):
        lines = [line.strip() for line in (ROOT / "config/login-keyring.pam").read_text().splitlines()
                 if line.strip() and not line.lstrip().startswith("#")]
        self.assertEqual(lines, ["auth optional pam_gnome_keyring.so",
                                 "session optional pam_gnome_keyring.so auto_start"])
        self.assertFalse(any("pam_permit" in line or "required" in line for line in lines))

    def test_xsession_initialization_is_nonblocking_and_secrets_only(self):
        path = ROOT / "config/xsession-keyring.sh"
        subprocess.run(["sh", "-n", str(path)], check=True)
        text = path.read_text()
        self.assertIn("--start --components=secrets", text)
        self.assertIn("|| :", text)
        self.assertIn('"${XDG_RUNTIME_DIR:-}"', text)
        for forbidden in ("--unlock", "--replace", "ssh-agent", "eval "):
            self.assertNotIn(forbidden, text)

    def test_user_service_resets_vendor_command_and_excludes_extra_components(self):
        text = (ROOT / "config/keyring-secrets-only.conf").read_text()
        self.assertIn("[Service]\nExecStart=\nExecStart=", text)
        self.assertIn("--foreground --components=secrets --control-directory=%t/keyring", text)
        self.assertNotIn("pkcs11", text)
        self.assertNotIn("components=ssh", text)


if __name__ == "__main__":
    unittest.main()
