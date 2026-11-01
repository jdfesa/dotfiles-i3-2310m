"""Public documentation contracts; no network or runtime changes."""
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def documents():
    paths = list(ROOT.glob("*.md"))
    for folder in ("config", "scripts", "tools"):
        paths.extend((ROOT / folder).rglob("*.md"))
    # Upstream attribution is preserved verbatim, not edited as project prose.
    return [p for p in paths if p != ROOT / "config/fonts/UPSTREAM.md"]


class DocumentationTests(unittest.TestCase):
    def test_readme_is_a_brief_entrypoint_with_topic_links(self):
        text = (ROOT / "README.md").read_text()
        for term in ("Dotfiles", "scripts", "configuration", "2011", "i3-2310M",
                     "Debian", "config/README.md", "scripts/README.md",
                     "restore-guide.md", "TODO.md", "## Contents", "## Documentation",
                     "## License"):
            self.assertIn(term.casefold(), text.casefold())
        self.assertLessEqual(len(text.split()), 300)
        for duplicate in ("Fn + F11", "No incluir contraseñas", "una CLI no garantiza",
                          "Estado y límites", "--dry-run", "configuraciones",
                          "Documentación", "Licencia", "Directorio"):
            self.assertNotIn(duplicate, text)

    def test_project_filenames_use_kebab_case_with_python_test_exception(self):
        conventional = {"README.md", "AGENTS.md", "CHANGELOG.md", "TODO.md", "LICENSE",
                        ".gitignore"}
        paths = list(ROOT.iterdir())
        for folder in ("config", "scripts", "tools", "tests"):
            paths.extend((ROOT / folder).rglob("*"))
        for path in paths:
            if not path.is_file() or path.name in conventional:
                continue
            if any(part in {"tmp", ".git", "__pycache__"} for part in path.relative_to(ROOT).parts):
                continue
            if path.name == ".DS_Store" or path.is_relative_to(ROOT / "config/fonts"):
                continue
            if path.parent == ROOT / "tests":
                self.assertRegex(path.name, r"^test_[a-z0-9_]+\.py$")
            else:
                self.assertRegex(path.name, r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+)*$")

    def test_project_prose_is_technical_not_conversational(self):
        forbidden = re.compile(
            r"\b(?:el autor|el creador|a su pedido|nuestra conversación|esta sesión)\b"
            r"|\b(?:el usuario|del usuario)\b.{0,60}\b(?:confirm|pid|solicit|aprob|prefer)"
            r"|\b(?:confirm|pid|solicit|aprob)\w*\s+por el usuario\b", re.I)
        for path in documents():
            self.assertIsNone(forbidden.search(path.read_text()), str(path.relative_to(ROOT)))

    def test_no_installation_specific_network_or_host_paths_in_docs(self):
        forbidden = re.compile(
            r"/Users/|\b192\.168\.\d+\.\d+\b"
            r"|\b10\.(?:\d+\.){2}\d+\b"
            r"|\b172\.(?:1[6-9]|2\d|3[01])\.\d+\.\d+\b"
            r"|SHA256:[A-Za-z0-9+/]{40,}")
        for path in documents():
            self.assertIsNone(forbidden.search(path.read_text()), str(path.relative_to(ROOT)))

    def test_local_markdown_links_exist(self):
        for path in documents():
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path:
                    continue
                destination = (path.parent / unquote(parsed.path)).resolve()
                self.assertTrue(destination.is_relative_to(ROOT), (path, target))
                self.assertTrue(destination.exists(), (path, target))

    def test_every_runtime_script_is_documented(self):
        inventory = (ROOT / "scripts/README.md").read_text()
        for path in (ROOT / "scripts").iterdir():
            if path.is_file() and path.name != "README.md":
                self.assertIn("scripts/" + path.name, inventory)

    def test_licenses_preserve_original_and_third_party_scope(self):
        self.assertTrue((ROOT / "LICENSE").read_text().startswith("MIT License\n"))
        notices = (ROOT / "third-party-notices.md").read_text()
        for name in ("config/profile", "GPL-2.0-or-later", "SIL OFL"):
            self.assertIn(name, notices)
        self.assertIn("SIL OPEN FONT LICENSE", (ROOT / "config/fonts/OFL.txt").read_text())
        self.assertIn("Version 2, June 1991", (ROOT / "licenses/GPL-2.0.txt").read_text())


if __name__ == "__main__":
    unittest.main()
