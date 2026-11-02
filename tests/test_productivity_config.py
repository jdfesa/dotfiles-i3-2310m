"""Non-destructive deployment and productivity contracts with private fixtures."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import fcntl
import pty
import select
import shutil
import signal
import struct
import subprocess
import tarfile
import tempfile
import termios
import time
import tomllib
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


LINKS = module("link-user-config")
MINI = module("install-mini-files")


class UserLinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="i3-links-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root, self.home = self.base / "repo", self.base / "home"
        (self.root / "config").mkdir(parents=True)
        self.home.mkdir(mode=0o700)
        self.source = self.root / "config/editor.lua"
        self.source.write_text("-- synthetic configuration\n")
        self.source.chmod(0o644)
        self.target = self.home / ".config/nvim/init.lua"
        self.backup = self.base / "backup"
        self.entries = [dict(source="config/editor.lua", destination=str(self.target),
                             mode=0o644, deployment="symlink")]
        self.write_manifest()

    def write_manifest(self):
        (self.root / "config/manifest.json").write_text(json.dumps(self.entries))

    def plan(self):
        return LINKS.plan(self.root, self.home)

    def apply(self):
        return LINKS.apply(self.plan(), self.root, self.home, self.backup)

    def test_dry_run_does_not_create_destinations(self):
        self.assertEqual(self.plan()[0]["action"], "create")
        self.assertFalse(self.target.parent.exists())
        self.assertFalse(self.backup.exists())

    def test_apply_is_idempotent_and_rollback_keeps_unmanaged_files(self):
        journal = self.apply()
        self.assertEqual(self.target.resolve(), self.source)
        self.assertEqual(self.backup.stat().st_mode & 0o777, 0o700)
        self.assertEqual(journal.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.plan()[0]["action"], "unchanged")
        self.assertIsNone(LINKS.apply(self.plan(), self.root, self.home, self.base / "unused"))
        unrelated = self.target.parent / "unmanaged.lua"
        unrelated.write_text("preserve")
        LINKS.rollback(journal)
        self.assertFalse(self.target.is_symlink())
        self.assertFalse(self.target.exists())
        self.assertEqual(unrelated.read_text(), "preserve")
        LINKS.rollback(journal)

    def test_identical_copy_is_backed_up_and_restored_with_its_mode(self):
        self.target.parent.mkdir(parents=True)
        shutil.copyfile(self.source, self.target)
        self.target.chmod(0o600)
        journal = self.apply()
        self.assertTrue(self.target.is_symlink())
        LINKS.rollback(journal)
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_bytes(), self.source.read_bytes())
        self.assertEqual(self.target.stat().st_mode & 0o777, 0o600)

    def test_different_file_is_a_conflict(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("existing preference")
        with self.assertRaisesRegex(ValueError, "Conflict"):
            self.apply()
        self.assertEqual(self.target.read_text(), "existing preference")
        self.assertFalse(self.backup.exists())

    def test_wrong_and_broken_links_are_conflicts(self):
        self.target.parent.mkdir(parents=True)
        self.target.symlink_to(self.base / "absent")
        with self.assertRaisesRegex(ValueError, "Conflict"):
            self.plan()

    def test_symlinked_parent_is_rejected(self):
        (self.home / ".config").symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlinked parent"):
            self.plan()

    def test_changed_source_after_planning_stops_before_writes(self):
        entries = self.plan()
        self.source.write_text("changed")
        with self.assertRaisesRegex(ValueError, "changed after planning"):
            LINKS.apply(entries, self.root, self.home, self.backup)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.backup.exists())

    def test_backup_inside_repo_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside the working tree"):
            LINKS.apply(self.plan(), self.root, self.home, self.root / "backup")

    def test_rollback_stops_if_destination_was_replaced(self):
        journal = self.apply()
        self.target.unlink()
        self.target.write_text("new preference")
        with self.assertRaisesRegex(ValueError, "Changed destination"):
            LINKS.rollback(journal)
        self.assertEqual(self.target.read_text(), "new preference")

    def test_corrupt_backup_stops_rollback_without_unlinking(self):
        self.target.parent.mkdir(parents=True)
        shutil.copyfile(self.source, self.target)
        journal = self.apply()
        (self.backup / "file-0").write_text("corrupt")
        with self.assertRaisesRegex(ValueError, "Invalid backup"):
            LINKS.rollback(journal)
        self.assertTrue(self.target.is_symlink())

    def test_system_destinations_are_never_linked(self):
        self.entries[0]["destination"] = "/etc/synthetic-config"
        self.write_manifest()
        with self.assertRaises(ValueError):
            self.plan()


class MiniInstallerTests(unittest.TestCase):
    def test_archive_hash_failure_has_no_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp).resolve() / "mini.files"
            with self.assertRaisesRegex(ValueError, "checksum"):
                MINI.install(target, b"not the pinned archive")
            self.assertFalse(target.exists())

    def test_minimal_install_idempotence_and_conflict_detection(self):
        contents = {"LICENSE": b"Synthetic license", "lua/mini/files.lua": b"return {}"}
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            for name, body in contents.items():
                member = tarfile.TarInfo(f"mini.files-{MINI.COMMIT}/{name}")
                member.size = len(body)
                archive.addfile(member, io.BytesIO(body))
        body = buffer.getvalue()
        hashes = {k: hashlib.sha256(v).hexdigest() for k, v in contents.items()}
        with tempfile.TemporaryDirectory() as tmp, patch.object(MINI, "FILES", hashes), \
                patch.object(MINI, "ARCHIVE_SHA256", hashlib.sha256(body).hexdigest()):
            target = Path(tmp).resolve() / "pack/start/mini.files"
            self.assertTrue(MINI.install(target, body))
            self.assertFalse(MINI.install(target, body))
            (target / "lua/mini/files.lua").write_text("local modification")
            with self.assertRaisesRegex(ValueError, "differs"):
                MINI.install(target, body)

    def test_symlinked_package_parent_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            (root / "real").mkdir()
            (root / "link").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "Symlinked"):
                MINI.check_path(root / "link/mini.files")


class ProductivityConfigurationTests(unittest.TestCase):
    def test_yazi_apt_sources_are_grouped_and_public_key_is_pinned(self):
        base = ROOT / "config/yazi/apt"
        self.assertEqual(hashlib.sha256((base / "yazi-keyring.gpg").read_bytes()).hexdigest(),
                         "3da842333fc9ec420e404772267a2df4e7fdcee11396820bcf8eae93760d7f26")
        self.assertIn("signed-by=/usr/share/keyrings/yazi-keyring.gpg", (base / "yazi.list").read_text())
        self.assertIn(" stable main", (base / "yazi.list").read_text())
        self.assertIn("Pin-Priority: -1", (base / "yazi.pref").read_text())
        for name in ("yazi.list", "yazi-apt.pref", "yazi-keyring.gpg"):
            self.assertFalse((ROOT / "config" / name).exists())

    def test_yazi_has_only_text_directory_previews_and_no_preloads(self):
        config = tomllib.loads((ROOT / "config/yazi/yazi.toml").read_text())
        self.assertEqual(config["plugin"]["preloaders"], [])
        self.assertEqual({x["run"] for x in config["plugin"]["previewers"]},
                         {"folder", "code", "noop"})
        self.assertEqual(config["opener"]["edit"][0]["run"], "nvim -- %s")
        self.assertTrue(config["opener"]["edit"][0]["block"])

    def test_native_core_has_no_network_bootstrap_or_extra_modules(self):
        text = "\n".join(p.read_text() for p in (ROOT / "config/nvim").rglob("*.lua"))
        for forbidden in ("vim.pack", "git clone", "curl ", "os.execute", "vim.fn.system"):
            self.assertNotIn(forbidden, text)
        self.assertIn("permanent_delete = false", text)
        self.assertIn("preview = false", text)
        self.assertNotIn("require('mini.icons')", text)

    def test_manifest_symlink_scope_is_only_new_productivity_config(self):
        items = json.loads((ROOT / "config/manifest.json").read_text())
        linked = [x for x in items if x.get("deployment") == "symlink"]
        self.assertEqual(len(linked), 6)
        for item in linked:
            self.assertTrue(item["source"].startswith(("config/nvim/", "config/yazi/")))
            self.assertTrue(item["destination"].startswith("/home/jd/.config/"))

    @unittest.skipUnless(shutil.which("nvim"), "Neovim runtime validation needs nvim")
    def test_neovim_startup_with_isolated_state(self):
        with tempfile.TemporaryDirectory(prefix="i3-nvim-test-") as tmp:
            path = Path(tmp).resolve()
            source = path / "fixture-source.lua"
            source.write_text("-- before\n")
            linked = path / "fixture-link.lua"
            linked.symlink_to(source)
            env = dict(os.environ, HOME=str(path))
            for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
                env[key] = str(path / key.lower())
            runtime = str(ROOT / "config/nvim")
            args = ["nvim", "--headless", "-n", "-i", "NONE", "--cmd",
                    f"lua vim.opt.rtp:prepend({json.dumps(runtime)})"]
            plugin = os.environ.get("NVIM_TEST_MINI_FILES")
            if plugin:
                args += ["--cmd", f"lua vim.opt.rtp:append({json.dumps(plugin)})"]
            args += ["-u", str(ROOT / "config/nvim/init.lua"), "+lua assert(vim.o.number); "
                     "assert(vim.o.undofile); assert(vim.g.mapleader == ' '); "
                     "assert(vim.fn.maparg(' e', 'n') ~= '')"]
            if plugin:
                args += ["+lua assert(type(MiniFiles) == 'table'); "
                         "assert(not MiniFiles.config.windows.preview); "
                         "assert(not MiniFiles.config.options.permanent_delete); "
                         "MiniFiles.open(vim.fn.getcwd()); "
                         "assert(MiniFiles.get_explorer_state() ~= nil); MiniFiles.close()"]
            args += ["+lua assert(vim.o.backupcopy == 'yes'); vim.cmd.edit('fixture-link.lua'); "
                     "vim.api.nvim_buf_set_lines(0, 0, -1, false, {'-- after'}); vim.cmd.write()"]
            args += ["+qa!"]
            result = subprocess.run(args, env=env, cwd=path, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("Error detected", result.stderr)
            self.assertTrue(linked.is_symlink())
            self.assertEqual(source.read_text(), "-- after\n")

    @unittest.skipUnless(shutil.which("nvim") and os.environ.get("NVIM_TEST_MINI_FILES"),
                         "Set NVIM_TEST_MINI_FILES to the verified installed module")
    def test_mini_files_create_rename_and_trash_only_in_fixture(self):
        with tempfile.TemporaryDirectory(prefix="i3-mini-operations-") as tmp:
            path = Path(tmp).resolve()
            work = path / "work"
            work.mkdir()
            (work / "seed.txt").write_text("synthetic\n")
            env = dict(os.environ, HOME=str(path))
            for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
                env[key] = str(path / key.lower())
            script = path / "check.lua"
            script.write_text("""
local files = require('mini.files')
files.open(vim.fn.getcwd())
local function buffer()
  local b = vim.api.nvim_get_current_buf()
  assert(vim.bo[b].filetype == 'minifiles', 'Focused explorer buffer missing')
  return b
end
local original_confirm = vim.fn.confirm
vim.fn.confirm = function() return 1 end -- Synthetic fixture only.
local function rendered()
  -- Initial/refresh rendering has its own TextChanged event before user edits.
  vim.api.nvim_exec_autocmds('TextChanged', { buffer = buffer() })
end
local function synchronize()
  -- API buffer edits do not deliver the normal typed TextChanged event here.
  vim.api.nvim_exec_autocmds('TextChanged', { buffer = buffer() })
  files.synchronize()
  rendered()
end
rendered()
local b = buffer()
vim.api.nvim_buf_set_lines(b, -1, -1, false, { 'created.txt' })
synchronize()
assert(vim.fn.filereadable('created.txt') == 1, 'Create failed')
local lines = vim.api.nvim_buf_get_lines(buffer(), 0, -1, false)
for i, line in ipairs(lines) do
  if line:match('created%.txt$') then
    vim.api.nvim_buf_set_lines(buffer(), i - 1, i, false, { (line:gsub('created%.txt$', 'renamed.txt')) })
  end
end
synchronize()
assert(vim.fn.filereadable('renamed.txt') == 1, 'Rename failed')
lines = vim.api.nvim_buf_get_lines(buffer(), 0, -1, false)
for i, line in ipairs(lines) do
  if line:match('renamed%.txt$') then vim.api.nvim_buf_set_lines(buffer(), i - 1, i, false, {}) end
end
synchronize()
assert(vim.fn.filereadable('renamed.txt') == 0, 'Removal failed')
assert(#vim.fn.glob(vim.fn.stdpath('data') .. '/mini.files/trash/*', false, true) > 0, 'Trash missing')
vim.fn.confirm = original_confirm
files.close()
""")
            args = ["nvim", "--headless", "-n", "-i", "NONE", "--cmd",
                    "lua vim.opt.rtp:prepend(" + json.dumps(str(ROOT / "config/nvim")) + ")",
                    "--cmd", "lua vim.opt.rtp:append(" + json.dumps(os.environ["NVIM_TEST_MINI_FILES"]) + ")",
                    "-u", str(ROOT / "config/nvim/init.lua"), "-l", str(script)]
            result = subprocess.run(args, env=env, cwd=work, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((work / "seed.txt").read_text(), "synthetic\n")

    @unittest.skipUnless(shutil.which("yazi"), "Yazi TUI validation needs yazi")
    def test_yazi_starts_renders_fixture_and_quits(self):
        with tempfile.TemporaryDirectory(prefix="i3-yazi-test-") as tmp:
            path = Path(tmp).resolve()
            (path / "sample.txt").write_text("Synthetic text preview\n")
            env = dict(os.environ, HOME=str(path), TERM="xterm-256color",
                       YAZI_CONFIG_HOME=str(ROOT / "config/yazi"))
            for key in ("XDG_CONFIG_HOME", "XDG_DATA_HOME", "XDG_STATE_HOME", "XDG_CACHE_HOME"):
                env[key] = str(path / key.lower())
            pid, master = pty.fork()
            if pid == 0:
                os.chdir(path)
                os.execvpe("yazi", ["yazi", str(path)], env)
            output, status, sent_quit = bytearray(), None, False
            try:
                fcntl.ioctl(master, termios.TIOCSWINSZ, struct.pack("HHHH", 32, 100, 0, 0))
                deadline = time.monotonic() + 12
                while time.monotonic() < deadline:
                    if select.select([master], [], [], 0.1)[0]:
                        try:
                            chunk = os.read(master, 65536)
                        except OSError:
                            break
                        if not chunk:
                            break
                        output.extend(chunk)
                        if b"sample.txt" in output and not sent_quit:
                            os.write(master, b"q")
                            sent_quit = True
                    done, result = os.waitpid(pid, os.WNOHANG)
                    if done:
                        status = result
                        break
            finally:
                if status is None:
                    done, result = os.waitpid(pid, os.WNOHANG)
                    if not done:
                        os.kill(pid, signal.SIGTERM)
                        _, result = os.waitpid(pid, 0)
                    status = result
                os.close(master)
            self.assertTrue(sent_quit, bytes(output).decode(errors="replace"))
            self.assertEqual(os.waitstatus_to_exitcode(status), 0, bytes(output).decode(errors="replace"))


if __name__ == "__main__":
    unittest.main()
