# dotfiles-i3-2310m

Dotfiles, scripts, and configuration for a **Positivo BGH A470 (2011)** running
Debian 13 with i3 on Xorg.

[![Debian 13](https://img.shields.io/badge/Debian-13-A81D33?style=flat&logo=debian&logoColor=white)](docs/dependencies.md)
[![i3 on Xorg](https://img.shields.io/badge/Session-i3%20%2F%20Xorg-89b4fa?style=flat)](docs/i3-setup.md)
[![MIT License](https://img.shields.io/badge/License-MIT-a6e3a1?style=flat)](LICENSE)

## Specs

| Component | Specification |
| --- | --- |
| CPU | Intel Core i3-2310M, 2 cores / 4 threads, 2.10 GHz |
| Memory | 8 GiB: 2 × 4 GiB DDR3 SO-DIMM; 1334 MT/s reported |
| Motherboard | POSITIVO BGH (SMBIOS); Intel HM65 chipset |
| Graphics | Intel HD Graphics 3000, `i915` |
| Display | LVDS, 1366 × 768, 60 Hz |
| Storage | Kingston SA400S37120G, 120 GB SATA SSD |
| Optical drive | Slimtype DVD A DS8A5S |
| Ethernet | Realtek RTL8111/8168-family Gigabit Ethernet |
| Wi-Fi | Realtek RTL8188CE, 802.11b/g/n |
| Card reader | Realtek USB 2.0 multicard reader |
| BIOS | Phoenix 1.04.00.BH |

## Desktop setup

[![Kitty terminal](https://img.shields.io/badge/Terminal-Kitty-cba6f7?style=flat)](docs/kitty-setup.md)
[![Zsh shell](https://img.shields.io/badge/Shell-Zsh-a6e3a1?style=flat)](docs/kitty-setup.md#interactive-shell)
[![Neovim editor](https://img.shields.io/badge/Editor-Neovim-89b4fa?style=flat&logo=neovim&logoColor=white)](docs/editor-and-files.md)
[![Catppuccin Mocha](https://img.shields.io/badge/Theme-Catppuccin%20Mocha-f5c2e7?style=flat)](docs/apps-setup.md)

Rofi launches applications; Yazi manages files, LazyVim edits code, Helium browses, and Zathura reads PDFs.

[Status bar](docs/status-bar.md) ·
[Keyboard shortcuts](docs/keybindings.md) ·
[Editor and file management](docs/editor-and-files.md) ·
[Desktop applications](docs/apps-setup.md) ·
[PDF reader](docs/pdf-reader.md) ·
[Bluetooth and Magic Trackpad 2](docs/bluetooth-setup.md) ·
[USB audio](docs/audio-setup.md)

## Contents

```text
.
├── config/       # Configuration and manifest
├── docs/         # Topic guides
├── licenses/     # Third-party licenses
├── scripts/      # Runtime scripts
├── tests/        # Regression tests
├── tools/        # Development tools
├── wallpapers/   # Desktop backgrounds
├── .gitignore
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── README.md
└── TODO.md
```

## Documentation

- [Managed configuration mirror](config/README.md), [User configuration links](docs/user-config-links.md), [Runtime scripts](scripts/README.md), [Development and diagnostic tools](tools/README.md).
- [Dependencies and versions](docs/dependencies.md), [Restore and recovery](docs/restore-guide.md).
- [Network setup](docs/wifi-setup.md), [Verification status](docs/mirror-status.md).
- [Git workflow](docs/git-workflow.md), [Codex CLI](docs/codex-setup.md), [Development tools](docs/development-tools.md).
- [CHANGELOG.md](CHANGELOG.md), [TODO.md](TODO.md).

## License

Original code and documentation: [MIT](LICENSE).
[Third-party licenses and notices](docs/third-party-notices.md).
