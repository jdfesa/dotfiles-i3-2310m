"""Exercise the GRUB drop-in as data; never invoke GRUB or power commands."""
from pathlib import Path
import shlex
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
DROPIN = ROOT / "config/grub-lid.cfg"


class BootConfigTests(unittest.TestCase):
    def evaluate(self, default="", common=""):
        source = shlex.quote(str(DROPIN))
        command = (
            f"GRUB_CMDLINE_LINUX_DEFAULT={shlex.quote(default)}; "
            f"GRUB_CMDLINE_LINUX={shlex.quote(common)}; "
            f". {source}; . {source}; "
            'printf "%s\\n%s\\n" "$GRUB_CMDLINE_LINUX_DEFAULT" "$GRUB_CMDLINE_LINUX"'
        )
        return subprocess.run(["/bin/sh", "-eu", "-c", command],
                              text=True, capture_output=True, check=True).stdout.splitlines()

    def test_preserves_options_and_adds_initial_state_only_once(self):
        self.assertEqual(self.evaluate("quiet loglevel=3", "ro"),
                         ["quiet loglevel=3 button.lid_init_state=open", "ro"])

    def test_respects_explicit_settings_in_either_variable(self):
        for state in ("open", "method", "ignore", "disabled"):
            with self.subTest(state=state):
                option = "button.lid_init_state=" + state
                self.assertEqual(self.evaluate("quiet " + option), ["quiet " + option, ""])
                self.assertEqual(self.evaluate("quiet", option), ["quiet", option])

    def test_handles_empty_options(self):
        self.assertEqual(self.evaluate(), ["button.lid_init_state=open", ""])


if __name__ == "__main__":
    unittest.main()
