# dotfiles-i3-2310m

Dotfiles, scripts, and configuration for a **Positivo BGH A470 (2011)** running
Debian 13 with i3 on Xorg.

**Hardware:** Intel Core i3-2310M · Intel HD 3000 · 8 GB RAM · 120 GB SATA SSD.

## Desktop setup

| Component | Configuration |
| --- | --- |
| Session | [i3 on Xorg](docs/i3-setup.md) from a console login, without a display manager or compositor. |
| Bar | [i3bar and i3status](docs/status-bar.md): collapsible metrics, calendar, brightness, audio, and Wi-Fi. |
| Terminal and shell | [Kitty](docs/kitty-setup.md), Bash, and tabs that inherit the current directory. |
| Theme and fonts | Catppuccin Mocha with [JetBrains Mono Nerd Font](docs/apps-setup.md#fonts) and Noto Color Emoji. |
| Wallpaper | [Pixel Car](wallpapers/pixel-car.png), set by [xwallpaper](docs/i3-setup.md#wallpaper). |
| Launcher and power | Rofi application and power menus; [keyboard shortcuts](docs/keybindings.md). |
| Files and editing | [Yazi and Neovim with LazyVim](docs/editor-and-files.md); Thunar and VS Code as graphical alternatives. |
| Web and PDF | [Helium](docs/apps-setup.md#helium) and [Zathura with Poppler](docs/pdf-reader.md). |
| Input and audio | [Magic Trackpad 2](docs/bluetooth-setup.md) with workspace gestures; [USB audio](docs/audio-setup.md) through ALSA. |

## Contents

```text
.
├── config/       # Managed configuration and destination manifest
├── docs/         # Setup, operation, verification, and recovery guides
├── licenses/     # Third-party license texts
├── scripts/      # Session, status bar, and menu scripts
├── tests/        # Automated regression tests
├── tools/        # Installation, verification, and diagnostics
├── wallpapers/   # Desktop wallpaper assets
├── .gitignore
├── AGENTS.md
├── CHANGELOG.md
├── LICENSE
├── README.md
└── TODO.md
```

## Documentation

- **Configuration:** [files and destinations](config/README.md), [scripts](scripts/README.md), and [tools](tools/README.md).
- **Installation:** [dependencies](docs/dependencies.md) and [restoration](docs/restore-guide.md).
- **Network:** [Network setup](docs/wifi-setup.md).
- **Development:** [Git workflow](docs/git-workflow.md),
  [Codex](docs/codex-setup.md), and [RTK/Engram](docs/development-tools.md).
- **Maintenance:** [verification](docs/mirror-status.md),
  [changelog](CHANGELOG.md), and [TODO](TODO.md).

## License

Original code and documentation are licensed under [MIT](LICENSE).
[Third-party licenses and notices](docs/third-party-notices.md).
