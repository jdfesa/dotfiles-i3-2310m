"""Pure path substitution tests; no account, file or credential operations."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("home_relocation", Path(__file__).resolve().parents[1] / "tools/relocate-user-home.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class HomeRelocationTests(unittest.TestCase):
    def test_moves_only_the_exact_home_prefix(self):
        self.assertEqual(module.relocate('command="/home/joe/.local/bin/engram"'),
                         'command="/home/jd/.local/bin/engram"')
        self.assertEqual(module.relocate('/home/joey/file'), '/home/joey/file')
        self.assertEqual(module.relocate('/home/joe'), '/home/jd')

    def test_is_idempotent_and_does_not_rename_other_data(self):
        text = 'joe@example.test /home/jd/scripts/tool /tmp/joe'
        self.assertEqual(module.relocate(module.relocate(text)), text)


if __name__ == "__main__":
    unittest.main()
