"""Configuration scope and ignore rules, with synthetic temporary fixtures."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ConfigurationHygieneTests(unittest.TestCase):
    def test_manifest_only_contains_existing_nonsecret_sources(self):
        entries = json.loads((ROOT / "config/manifest.json").read_text())
        self.assertEqual(len({x["destination"] for x in entries}), len(entries))
        for item in entries:
            source = Path(item["source"])
            self.assertFalse(source.is_absolute())
            self.assertNotIn("..", source.parts)
            self.assertTrue((ROOT / source).is_file())
            self.assertNotEqual(source.name, "auth.json")
            self.assertNotIn(".engram", source.parts)
            self.assertNotIn(".ssh", source.parts)
            self.assertFalse(source.name.endswith((".db", ".nmconnection")))

    def test_minimal_agent_config_is_additive_and_local(self):
        config = tomllib.loads((ROOT / "config/codex-config.toml").read_text())
        self.assertNotIn("model_instructions_file", config)
        self.assertNotIn("experimental_compact_prompt_file", config)
        self.assertEqual(config["marketplaces"]["engram"]["ref"], "v3.6.0")
        self.assertEqual(config["mcp_servers"]["engram"], {
            "command": "/home/jd/.local/bin/engram", "args": ["mcp", "--tools=agent"]})
        telemetry = tomllib.loads((ROOT / "config/rtk-config.toml").read_text())["telemetry"]
        self.assertFalse(telemetry["enabled"])
        self.assertFalse(telemetry["consent_given"])

    @unittest.skipUnless(shutil.which("git"), "git is needed for real ignore matching")
    def test_gitignore_ignores_private_data_but_keeps_config(self):
        prefix = ["rtk", "proxy"] if sys.platform == "darwin" else []
        env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        ignored = ["auth.json", "tmp/auth.json.old", ".codex/auth.json",
                   ".engram/engram.db", "nested/.engram/export.json", "history.jsonl",
                   "downloads/tool.tar.gz", "logs/session.log", ".env", "key.pem",
                   "wifi.nmconnection", "nested/.aws/credentials", ".ssh/authorized_keys",
                   "stats.sqlite-wal", "engram-export.json"]
        retained = ["README.md", "AGENTS.md", ".gitignore", "config/manifest.json",
                    "config/codex-config.toml", "config/codex-hooks.json",
                    "config/rtk-config.toml", "config/helium-signing-key.asc",
                    "tools/install-user-tools.py", "scripts/power-menu", "LICENSE",
                    "docs/third-party-notices.md", "docs/dependencies.md", "licenses/GPL-2.0.txt",
                    "tools/README.md"]
        with tempfile.TemporaryDirectory(prefix="i3-ignore-test-") as tmp:
            # This disposable fixture is not the project and has no commits/remotes.
            subprocess.run(prefix + ["git", "-C", tmp, "init", "-q"], env=env, check=True)
            shutil.copyfile(ROOT / ".gitignore", Path(tmp) / ".gitignore")
            for path in ignored + retained:
                probe = Path(tmp) / path
                if path != ".gitignore":
                    probe.parent.mkdir(parents=True, exist_ok=True)
                    probe.write_text("synthetic fixture\n")
                result = subprocess.run(prefix + ["git", "-C", tmp, "check-ignore",
                    "--no-index", "-q", path], env=env, capture_output=True)
                self.assertEqual(result.returncode, 0 if path in ignored else 1, path)


if __name__ == "__main__":
    unittest.main()
