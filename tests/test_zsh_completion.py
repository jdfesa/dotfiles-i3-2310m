"""Native Zsh completion contracts with isolated private state."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ZSH = shutil.which("zsh")


@unittest.skipUnless(ZSH, "zsh is needed for native completion checks")
class ZshCompletionTests(unittest.TestCase):
    def test_native_completion_keeps_history_prompt_and_private_cache(self):
        with tempfile.TemporaryDirectory(prefix="zsh-completion-") as tmp:
            home = Path(tmp)
            cache = home / "cache"
            env = dict(os.environ, HOME=str(home), XDG_CACHE_HOME=str(cache),
                       STARSHIP_CONFIG=os.devnull, STARSHIP_CACHE=str(cache / "starship"),
                       TERM="xterm-256color")
            command = r'''
source "$1"
[[ $HISTSIZE == 5000 && $SAVEHIST == 5000 && $HISTFILE == "$HOME/.zsh_history" ]] || exit 11
(( $+functions[compdef] && $+_comps[git] && $+_comps[cd] )) || exit 12
zmodload -e zsh/complist || exit 13
zstyle -s ":completion:*" menu reply && [[ $reply == select ]] || exit 14
zstyle -t ":completion:*" special-dirs || exit 15
[[ $_comp_dumpfile == "$XDG_CACHE_HOME/zsh/zcompdump-$ZSH_VERSION" ]] || exit 16
[[ -r $_comp_dumpfile && -z $(compaudit) ]] || exit 17
[[ ! -x /usr/bin/starship || $STARSHIP_SHELL == zsh ]] || exit 18
unset HISTFILE
'''
            for _ in range(2):
                result = subprocess.run([ZSH, "-f", "-i", "-c", command, "zsh-test",
                                         str(ROOT / "config/zsh/zshrc")],
                                        env=env, cwd=home, capture_output=True,
                                        text=True, timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
            self.assertEqual((cache / "zsh").stat().st_mode & 0o777, 0o700)
            self.assertEqual(len(list((cache / "zsh").glob("zcompdump-*"))), 1)
            self.assertFalse((ROOT / "config/zsh/.zcompdump").exists())

    def test_unavailable_cache_does_not_disable_completion(self):
        with tempfile.TemporaryDirectory(prefix="zsh-completion-") as tmp:
            home = Path(tmp)
            cache = home / "blocked-cache"
            cache.write_text("synthetic non-directory")
            env = dict(os.environ, HOME=str(home), XDG_CACHE_HOME=str(cache),
                       STARSHIP_CONFIG=os.devnull, STARSHIP_CACHE=str(home / "starship"),
                       TERM="xterm-256color")
            command = 'source "$1"; unset HISTFILE; (( $+functions[compdef] && $+_comps[git] ))'
            result = subprocess.run([ZSH, "-f", "-i", "-c", command, "zsh-test",
                                     str(ROOT / "config/zsh/zshrc")],
                                    env=env, cwd=home, capture_output=True,
                                    text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(cache.read_text(), "synthetic non-directory")
            self.assertFalse((home / ".zcompdump").exists())


if __name__ == "__main__":
    unittest.main()
