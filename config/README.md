# Managed configuration mirror

Fuentes de los archivos administrados, versionadas mediante **GitHub**. Cada
máquina mantiene un único checkout, sin una copia secundaria. Editar fuente,
revisar destino, respaldar, desplegar y validar principalmente en la portátil.
No contiene secretos Wi-Fi ni claves privadas.

Mapa legible; la misma lista para verificaciones está en `manifest.json`, con fuentes relativas a la raíz del proyecto. Los scripts se explican en `../scripts/README.md` y se ejecutan desde `/home/jd/dotfiles-i3-2310m/scripts/`. Estado de coincidencia comprobada en [Verification status](../docs/mirror-status.md).

| Fuente desde la raíz | Destino real | Modo | Deployment |
|---|---|---|---|
| `scripts/codex-launch.py` | `/home/jd/.local/bin/codex` | `755` | `symlink` |
| `scripts/laravel-services.py` | `/home/jd/dotfiles-i3-2310m/scripts/laravel-services.py` | `755` | `in-place` |
| `config/laravel/services.css` | `/home/jd/dotfiles-i3-2310m/config/laravel/services.css` | `644` | `in-place` |
| `config/laravel/packages-debian.txt` | `/home/jd/dotfiles-i3-2310m/config/laravel/packages-debian.txt` | `644` | `in-place` |
| `config/laravel/bgh-laravel-services.desktop` | `/home/jd/.local/share/applications/bgh-laravel-services.desktop` | `644` | `symlink` |
| `config/laravel/mariadb.cnf` | `/etc/mysql/mariadb.conf.d/90-laravel-local.cnf` | `644` | `system-copy` |
| `config/laravel/phpmyadmin.inc.php` | `/etc/phpmyadmin/conf.d/90-laravel-local.php` | `644` | `system-copy` |
| `config/laravel/phpmyadmin.service` | `/etc/systemd/system/laravel-phpmyadmin.service` | `644` | `system-copy` |
| `config/laravel/phpmyadmin-router.php` | `/usr/local/share/bgh-laravel/phpmyadmin-router.php` | `644` | `system-copy` |
| `config/grub-lid.cfg` | `/etc/default/grub.d/60-bgh-lid.cfg` | `644` | `system-copy` |
| `config/i3-config` | `/home/jd/.config/i3/config` | `644` | `symlink` |
| `wallpapers/pixel-car.png` | `/home/jd/.local/share/wallpapers/pixel-car.png` | `644` | `symlink` |
| `config/i3status-config` | `/home/jd/.config/i3status/config` | `644` | `symlink` |
| `config/xinitrc` | `/home/jd/.xinitrc` | `644` | `symlink` |
| `config/profile` | `/home/jd/.profile` | `644` | `symlink` |
| `config/network-interfaces` | `/etc/network/interfaces` | `644` | `system-copy` |
| `config/networkmanager.conf` | `/etc/NetworkManager/conf.d/20-network-ownership.conf` | `644` | `system-copy` |
| `config/locale` | `/etc/locale.conf` | `644` | `system-copy` |
| `config/helium.list` | `/etc/apt/sources.list.d/helium.list` | `644` | `system-copy` |
| `config/kitty.conf` | `/home/jd/.config/kitty/kitty.conf` | `644` | `symlink` |
| `config/zsh/zshrc` | `/home/jd/.zshrc` | `644` | `symlink` |
| `config/starship/starship.toml` | `/home/jd/.config/starship.toml` | `644` | `symlink` |
| `config/rofi-config.rasi` | `/home/jd/.config/rofi/config.rasi` | `644` | `symlink` |
| `config/keybindings-help.txt` | `/home/jd/.config/i3/keybindings-help.txt` | `644` | `symlink` |
| `config/mimeapps.list` | `/home/jd/.config/mimeapps.list` | `644` | `symlink` |
| `scripts/capture-screenshot.py` | `/home/jd/dotfiles-i3-2310m/scripts/capture-screenshot.py` | `755` | `in-place` |
| `scripts/status-bar.sh` | `/home/jd/dotfiles-i3-2310m/scripts/status-bar.sh` | `755` | `in-place` |
| `scripts/status-clicks.py` | `/home/jd/dotfiles-i3-2310m/scripts/status-clicks.py` | `755` | `in-place` |
| `scripts/bluetooth-status.py` | `/home/jd/dotfiles-i3-2310m/scripts/bluetooth-status.py` | `755` | `in-place` |
| `scripts/open-trackpad-speed.py` | `/home/jd/dotfiles-i3-2310m/scripts/open-trackpad-speed.py` | `755` | `in-place` |
| `scripts/trackpad-gestures.py` | `/home/jd/dotfiles-i3-2310m/scripts/trackpad-gestures.py` | `755` | `in-place` |
| `config/bluetooth/vendor/magic-trackpad-battery` | `/home/jd/.local/lib/bgh-bluetooth/magic-trackpad-battery` | `644` | `symlink` |
| `config/bluetooth/vendor/LICENSE` | `/home/jd/.local/lib/bgh-bluetooth/LICENSE` | `644` | `symlink` |
| `config/bluetooth/72-bgh-magic-trackpad.rules` | `/etc/udev/rules.d/72-bgh-magic-trackpad.rules` | `644` | `system-copy` |
| `config/bluetooth/90-bgh-magic-trackpad-speed.conf` | `/etc/X11/xorg.conf.d/90-bgh-magic-trackpad-speed.conf` | `644` | `system-copy` |
| `scripts/status-panel.py` | `/home/jd/dotfiles-i3-2310m/scripts/status-panel.py` | `755` | `in-place` |
| `scripts/screen-brightness.py` | `/home/jd/dotfiles-i3-2310m/scripts/screen-brightness.py` | `755` | `in-place` |
| `scripts/calendar-popup.py` | `/home/jd/dotfiles-i3-2310m/scripts/calendar-popup.py` | `755` | `in-place` |
| `config/calendar/calendar.css` | `/home/jd/.config/calendar/calendar.css` | `644` | `symlink` |
| `scripts/open-networks.sh` | `/home/jd/dotfiles-i3-2310m/scripts/open-networks.sh` | `755` | `in-place` |
| `config/network-panel/bgh-network-panel.desktop` | `/home/jd/.local/share/applications/bgh-network-panel.desktop` | `644` | `symlink` |
| `scripts/open-mixer.sh` | `/home/jd/dotfiles-i3-2310m/scripts/open-mixer.sh` | `755` | `in-place` |
| `scripts/audio-control.py` | `/home/jd/dotfiles-i3-2310m/scripts/audio-control.py` | `755` | `in-place` |
| `scripts/audio-volume.py` | `/home/jd/dotfiles-i3-2310m/scripts/audio-volume.py` | `755` | `in-place` |
| `scripts/audio-position.py` | `/home/jd/dotfiles-i3-2310m/scripts/audio-position.py` | `755` | `in-place` |
| `scripts/refresh-helium-audio.py` | `/home/jd/dotfiles-i3-2310m/scripts/refresh-helium-audio.py` | `755` | `in-place` |
| `config/audio/usb-audio.json` | `/home/jd/.config/audio/usb-audio.json` | `644` | `symlink` |
| `scripts/open-updates.sh` | `/home/jd/dotfiles-i3-2310m/scripts/open-updates.sh` | `755` | `in-place` |
| `config/bgh-status-icons.ttf` | `/home/jd/.local/share/fonts/bgh-status-icons.ttf` | `644` | `symlink` |
| `config/weather.json` | `/home/jd/.config/i3/weather.json` | `644` | `symlink` |
| `scripts/update-weather.py` | `/home/jd/dotfiles-i3-2310m/scripts/update-weather.py` | `755` | `in-place` |
| `config/weather-refresh.service` | `/home/jd/.config/systemd/user/weather-refresh.service` | `644` | `symlink` |
| `config/weather-refresh.timer` | `/home/jd/.config/systemd/user/weather-refresh.timer` | `644` | `symlink` |
| `scripts/update-packages.py` | `/home/jd/dotfiles-i3-2310m/scripts/update-packages.py` | `755` | `in-place` |
| `config/packages-refresh.service` | `/home/jd/.config/systemd/user/packages-refresh.service` | `644` | `symlink` |
| `config/packages-refresh.timer` | `/home/jd/.config/systemd/user/packages-refresh.timer` | `644` | `symlink` |
| `config/fonts/JetBrainsMonoNerdFontMono-Regular.ttf` | `/home/jd/.local/share/fonts/JetBrainsMonoNerdFontMono-Regular.ttf` | `644` | `symlink` |
| `config/fonts/JetBrainsMonoNerdFontMono-Bold.ttf` | `/home/jd/.local/share/fonts/JetBrainsMonoNerdFontMono-Bold.ttf` | `644` | `symlink` |
| `config/fonts/jetbrains-mono-nerd-font-propo-regular.ttf` | `/home/jd/.local/share/fonts/jetbrains-mono-nerd-font-propo-regular.ttf` | `644` | `symlink` |
| `config/fonts/OFL.txt` | `/home/jd/.local/share/fonts/bgh-font-licenses/OFL.txt` | `644` | `symlink` |
| `config/fonts/UPSTREAM.md` | `/home/jd/.local/share/fonts/bgh-font-licenses/UPSTREAM.md` | `644` | `symlink` |
| `scripts/power-menu` | `/home/jd/dotfiles-i3-2310m/scripts/power-menu` | `755` | `in-place` |
| `scripts/power-action.sh` | `/home/jd/dotfiles-i3-2310m/scripts/power-action.sh` | `755` | `in-place` |
| `config/bgh-power-menu.desktop` | `/home/jd/.local/share/applications/bgh-power-menu.desktop` | `644` | `symlink` |
| `config/zathura/zathurarc` | `/home/jd/.config/zathura/zathurarc` | `644` | `symlink` |
| `config/thunar/thunar.desktop` | `/home/jd/.local/share/applications/thunar.desktop` | `644` | `symlink` |
| `config/thunar/10-dark-theme.conf` | `/home/jd/.config/systemd/user/thunar.service.d/10-dark-theme.conf` | `644` | `symlink` |
| `config/vscode/apt/microsoft.asc` | `/etc/apt/keyrings/bgh-vscode.asc` | `644` | `system-copy` |
| `config/vscode/apt/vscode.sources` | `/etc/apt/sources.list.d/vscode.sources` | `644` | `system-copy` |
| `config/vscode/apt/vscode.pref` | `/etc/apt/preferences.d/vscode` | `644` | `system-copy` |
| `scripts/README.md` | `/home/jd/dotfiles-i3-2310m/scripts/README.md` | `644` | `in-place` |
| `config/codex-config.toml` | `/home/jd/.codex/config.toml` | `600` | `private-overlay` |
| `config/codex-agents.md` | `/home/jd/.codex/AGENTS.md` | `600` | `symlink` |
| `config/codex-rtk.md` | `/home/jd/.codex/RTK.md` | `600` | `symlink` |
| `config/codex-hooks.json` | `/home/jd/.codex/hooks.json` | `600` | `symlink` |
| `config/rtk-config.toml` | `/home/jd/.config/rtk/config.toml` | `600` | `symlink` |
| `config/login-keyring.pam` | `/etc/pam.d/login-keyring` | `644` | `system-copy` |
| `config/keyring-secrets-only.conf` | `/etc/systemd/user/gnome-keyring-daemon.service.d/10-secrets-only.conf` | `644` | `system-copy` |
| `config/xsession-keyring.sh` | `/etc/X11/Xsession.d/95keyring-secrets` | `644` | `system-copy` |
| `config/lazyvim/init.lua` | `/home/jd/.config/nvim/init.lua` | `644` | `symlink` |
| `config/lazyvim/lazy-lock.json` | `/home/jd/.config/nvim/lazy-lock.json` | `644` | `symlink` |
| `config/yazi/yazi.toml` | `/home/jd/.config/yazi/yazi.toml` | `644` | `symlink` |
| `config/yazi/apt/yazi.list` | `/etc/apt/sources.list.d/yazi.list` | `644` | `system-copy` |
| `config/yazi/apt/yazi.pref` | `/etc/apt/preferences.d/yazi` | `644` | `system-copy` |
| `config/yazi/apt/yazi-keyring.gpg` | `/usr/share/keyrings/yazi-keyring.gpg` | `644` | `system-copy` |

## Special cases

- Keyring: fragmento PAM opcional incluido desde login, inicialización Xsession
  y servicio sólo secrets; instalación/rollback en [Git workflow](../docs/git-workflow.md).
  No copiar contraseñas, tokens o depósitos privados al manifiesto.

- `wifi-boot-state.service` es referencia diagnóstica inactiva, fuera del
  manifiesto: no instalar/habilitar al restaurar.
- `grub-lid.cfg` requiere instalación root y regenerar/validar GRUB; no copiar
  un grub.cfg generado. [Diagnóstico](../docs/boot-troubleshooting.md).
- `helium-signing-key.asc` es clave pública: convertir a keyring binario y
  comparar fingerprint oficial, no hash entre formatos.
- `config/locale` corresponde al archivo root `/etc/locale.conf`; conservar
  el alias Debian `/etc/default/locale`, sin reemplazarlo con un enlace al home.
- `login-autostart.sh` es el fragmento ya incluido en `profile`, no otro
  ejecutable de inicio.
- `manifest.json` y este README documentan/verifican; no los consume i3.
- Codex/RTK/Engram se reinstalan desde su origen; no se espejan binarios,
  credenciales, plugins completos, memorias, bases de datos o caches.
- La configuración mínima Codex y mimeapps no contiene todas las preferencias
  actuales. Revisar diferencias antes de restaurar.
- `~/.cache/i3/` contiene datos generados, no configuración administrada.

Archivos de sesión propiedad de jd; archivos de sistema root:root. El manifiesto
expresa permisos en decimal: 420=644, 493=755, 384=600.
Los destinos públicos de usuario usan `deployment=symlink`; los scripts se
marcan `in-place` y se ejecutan desde el repositorio. `private-overlay` conserva
sólo una base pública, no una copia del estado efectivo privado. Los archivos de
sistema siguen regulares root:root. Instalación, validación y recuperación en
[User configuration links](../docs/user-config-links.md).

## Verification

Desde la raíz:

```sh
python3 tools/verify-mirror.py
# En una copia revisada del proyecto sobre la portátil:
python3 tools/verify-mirror.py --remote --check
```

Sin `--check`, el verificador imprime SHA256. Con `--remote --check` exige
contenido, identidad del enlace, tipo, propietario y modo del manifiesto;
`private-overlay` se excluye de la comparación del archivo efectivo privado.
