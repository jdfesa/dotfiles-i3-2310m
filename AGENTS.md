# Agent instructions — Debian laptop configuration

## Scope and documentation

- This tree is the source of truth for managed configuration on the BGH A470,
  not a full home or /etc mirror. The target is 2011 i3-2310M/Sandy Bridge,
  Debian 13 amd64, 8 GB RAM and a 120 GB SATA SSD.
- Root README.md is fully English. All documentation titles/subtitles and
  filenames are English; other guide bodies remain Spanish. Adopt English
  progressively for broader accessibility.
- Topic guides and third-party notices belong in docs/. Keep README.md,
  AGENTS.md, CHANGELOG.md, TODO.md and LICENSE in the root; component READMEs
  stay alongside their sources. Guide command examples run from the repository
  root unless stated otherwise.
- Project-owned multi-word filenames and scripts use lowercase kebab-case.
  Preserve conventional tool filenames (README.md, AGENTS.md, CHANGELOG.md,
  TODO.md, LICENSE), vendor assets/notices and Python test_*.py modules for
  standard unittest discovery.
- All visible system, application, menu, bar and help text is English (en_US.UTF-8).
- Documentation must be concise and reproducible: current state, rationale,
  dependencies/origins/verified versions, installation, checks and recovery.
  Use CHANGELOG.md for technical changes and TODO.md for pending work. No chat
  narrative, third-person references to the repository maintainer or exhaustive
  vulnerability diary. Brief kernel/security limits are sufficient.
- README.md is a short entry point: repository contents, specific target machine
  and navigation. Keep working criteria here, pending work in TODO.md and details
  in their topic guides. Link to a single source instead of duplicating status,
  procedures or lists. Do not add generic warnings or defensive caveats to the
  overview; include a constraint only where it affects a concrete operation.
- Low CPU work, stability and productivity are primary selection criteria.
  Prefer the lightest adequate compatible tool; console/TUI only when genuinely
  advantageous. Avoid unnecessary daemons, polling, effects and large local
  compilations. Do not claim performance gains without representative measures.
  RAM/SSD are not unlimited; never weaken security for optimization.
  The browser remains part of the workload; select other tools around those limits.
- Config/desktop sources belong in config/, runtime scripts in scripts/ and
  manual development tools in tools/. Explain scripts and map full source paths,
  real destinations and modes in config/manifest.json.
- /home/jd/setup-guide is a secondary copy, not the only documentation.
  Current account/home is jd /home/jd. General symlink migration is pending.
- No repository creation, folder rename, commit, push or visibility change
  without explicit authorization; publication requires agreement on final state.

## Change workflow

1. Inspect actual destinations and preserve existing changes. If unreachable,
   make only clearly marked local changes; do not claim deployment or equality.
2. Edit local source first; review a non-secret baseline for newly managed files.
3. Back up destinations privately outside this tree before deployment.
4. Deploy user files as jd; system files separately with authorized sudo,
   root ownership and regular installation, never links into a writable home.
5. Validate syntax and behavior in the existing session. Preserve applications,
   tty2+, SSH and the disable-autostart escape hatch; do not start X from SSH/root.
6. Compare contents/hashes, permissions and owners; update guides/CHANGELOG
   with verified results and pending tests. Sync the secondary copy when possible.
7. Future user symlinks need laptop-resident targets, per-file conflict checks,
   dry-run and rollback. Review mimeapps/Codex divergences before migration.

## Runtime contract

- Authenticated tty1 login starts i3; no display manager, autologin, full desktop
  or compositor without explicit approval. Super+Space launcher, Super+Enter
  terminal, top bar; update docs/keybindings.md and visible help for binding
  changes.
- Compact opaque Catppuccin Mocha; JetBrainsMono Nerd Font Mono Regular
  throughout the bar. Bold is installed but not forced. Show existing workspaces.
- i3status tick 10 s; traffic uses counter deltas on that tick. No additional
  high-frequency polling. status-clicks.py is resident and event-driven.
- Weather: public Oran city-centre coordinates, no automatic geolocation;
  icon/temperature only, refresh 30 min via short service/cache, honest stale data.
- APT counter: local simulated metadata every 6 h; no automatic apt update,
  upgrade or installation. Fixed event-driven click helpers; no shell interpolation.
- Wi-Fi block: level icon only, no SSID/numeric quality. Click and Super+N use
  the same English network list; preserve NetworkManager authorization.
- Audio hardware verification is deferred. Show No audio when absent; do not
  install audio servers or continue diagnostics without coordinated adapter test.
- Power menu: Power off first, Yes selected in all confirmations; Escape/No/Cancel
  available. Active local session authorization through logind/standard polkitd,
  no sudo fallback, custom broad policy or NOPASSWD. Require Can*=yes,
  --no-ask-password and check-inhibitors=auto with systemd>=257 guard.
  Suspend locks first. No forced/ignore-inhibitor actions.
- Never test real lock/logout/suspend/reboot/poweroff or disrupt network without
  coordination. Use real dry-run/inhibitor checks from the local session;
  SSH is not an equivalent policy context. Automatic lid/idle locking is pending.
- Keep i3bar SIGSTOP/SIGCONT defaults; signals address the complete process group.
  A reload may retain the old adapter; restart i3 preserving windows if required.
- Helium uses its official signed APT stable repository; preserve sandbox.
  Verify GPU/CPU compatibility, never hide it with permanent software rendering.
- Wi-Fi hard block remains unresolved; final bounded capture is complete.
  No further boot cycles, Fn replay, blacklist or EC/firmware work by default.

## Security, tools and validation

- Verify SSH identity against trusted known_hosts or the physical console.
  DHCP addresses are not permanent; do not publish installation-specific LAN
  endpoints, SSH fingerprints, SSIDs or private administration-host paths.
- Keep sudo password-protected; no password rotation or access-method changes
  without coordination. Never track or publish credentials, private keys,
  nmconnection profiles, Codex auth, keyrings, memories/SQLite, RTK history or logs.
  Necessary local-only material may stay in ignored private/ with restrictive
  permissions; transfer reviewed private files between working copies by SSH,
  never GitHub. Keep destination backups outside the worktree; do not bulk-import
  private authentication directories.
- Before every push, test real ignore matching, check tracked-but-ignored files,
  review an explicit staged allowlist and exact contents, and audit all outgoing
  commits for secrets. Ignore rules do not remove tracked data or history; stop
  publication on any unresolved finding. Never force-add private material.
- Public vendor keys and non-secret repository config may be mirrored with
  verified origins. MIT covers original material; preserve third-party licenses.
- Keep RTK/Engram integration minimal and additive. Recreate the pinned official
  plugin, not whole hidden directories. No cloud/boot service without approval;
  the official loopback-only helper may run with Codex. Preserve active chats;
  tests sending memories to a model need explicit privacy-safe scope.
- Administration-host shell commands must start with rtk; use its supported raw
  passthrough (0.43: proxy). Laptop RTK 1.1.0 uses bypass; do not mix versions.
- Validate i3 with i3 -C, shell files with sh -n and GUI applications with their
  parsers plus bounded real-window checks. Use Mod1 for Alt. Font cache/render
  changes may need i3 restart, never a logout/reboot solely to refresh fonts.
- Tests do not prove clean-system restoration or sustained CPU performance.
  Keep tests non-destructive and store generated material outside the tree.
- Follow the Engram memory protocol; persist durable decisions and session
  summaries outside the published configuration.
