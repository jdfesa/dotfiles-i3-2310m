# Managed configuration mirror

Fuentes de los archivos administrados. Este proyecto es la **fuente de verdad**; `/home/jd/setup-guide` es copia secundaria. Editar local primero, revisar destino remoto, respaldar, desplegar, validar y comparar hashes. No contiene secretos Wi-Fi ni claves privadas.

Mapa legible; la misma lista para verificaciones está en `manifest.json`, con fuentes relativas a la raíz del proyecto. Los scripts se explican en `../scripts/README.md` y se instalan en `/home/jd/scripts/`. Estado de coincidencia comprobada en `../mirror-status.md`.

| Fuente local desde raíz del proyecto | Destino real en portátil | Modo |
|---|---|---|
| `config/grub-lid.cfg` | `/etc/default/grub.d/60-bgh-lid.cfg` | `644` (root) |
| `config/i3-config` | `/home/jd/.config/i3/config` | `644` |
| `config/i3status-config` | `/home/jd/.config/i3status/config` | `644` |
| `config/xinitrc` | `/home/jd/.xinitrc` | `644` |
| `config/profile` | `/home/jd/.profile` | `644` |
| `config/network-interfaces` | `/etc/network/interfaces` | `644` |
| `config/networkmanager.conf` | `/etc/NetworkManager/conf.d/20-network-ownership.conf` | `644` |
| `config/locale` | `/etc/default/locale` | `644` |
| `config/helium.list` | `/etc/apt/sources.list.d/helium.list` | `644` |
| `config/kitty.conf` | `/home/jd/.config/kitty/kitty.conf` | `644` |
| `config/rofi-config.rasi` | `/home/jd/.config/rofi/config.rasi` | `644` |
| `config/keybindings-help.txt` | `/home/jd/.config/i3/keybindings-help.txt` | `644` |
| `config/mimeapps.list` | `/home/jd/.config/mimeapps.list` | `644` |
| `scripts/status-bar.sh` | `/home/jd/scripts/status-bar.sh` | `755` |
| `scripts/status-clicks.py` | `/home/jd/scripts/status-clicks.py` | `755` |
| `scripts/open-networks.sh` | `/home/jd/scripts/open-networks.sh` | `755` |
| `scripts/open-mixer.sh` | `/home/jd/scripts/open-mixer.sh` | `755` |
| `scripts/open-updates.sh` | `/home/jd/scripts/open-updates.sh` | `755` |
| `config/bgh-status-icons.ttf` | `/home/jd/.local/share/fonts/bgh-status-icons.ttf` | `644` |
| `config/weather.json` | `/home/jd/.config/i3/weather.json` | `644` |
| `scripts/update-weather.py` | `/home/jd/scripts/update-weather.py` | `755` |
| `config/weather-refresh.service` | `/home/jd/.config/systemd/user/weather-refresh.service` | `644` |
| `config/weather-refresh.timer` | `/home/jd/.config/systemd/user/weather-refresh.timer` | `644` |
| `scripts/update-packages.py` | `/home/jd/scripts/update-packages.py` | `755` |
| `config/packages-refresh.service` | `/home/jd/.config/systemd/user/packages-refresh.service` | `644` |
| `config/packages-refresh.timer` | `/home/jd/.config/systemd/user/packages-refresh.timer` | `644` |
| `config/fonts/JetBrainsMonoNerdFontMono-Regular.ttf` | `/home/jd/.local/share/fonts/JetBrainsMonoNerdFontMono-Regular.ttf` | `644` |
| `config/fonts/JetBrainsMonoNerdFontMono-Bold.ttf` | `/home/jd/.local/share/fonts/JetBrainsMonoNerdFontMono-Bold.ttf` | `644` |
| `config/fonts/OFL.txt` | `/home/jd/.local/share/fonts/bgh-font-licenses/OFL.txt` | `644` |
| `config/fonts/UPSTREAM.md` | `/home/jd/.local/share/fonts/bgh-font-licenses/UPSTREAM.md` | `644` |
| `scripts/power-menu` | `/home/jd/scripts/power-menu` | `755` |
| `scripts/power-action.sh` | `/home/jd/scripts/power-action.sh` | `755` |
| `config/bgh-power-menu.desktop` | `/home/jd/.local/share/applications/bgh-power-menu.desktop` | `644` |
| `scripts/README.md` | `/home/jd/scripts/README.md` | `644` |
| `config/codex-config.toml` | `/home/jd/.codex/config.toml` | `600` |
| `config/codex-agents.md` | `/home/jd/.codex/AGENTS.md` | `600` |
| `config/codex-rtk.md` | `/home/jd/.codex/RTK.md` | `600` |
| `config/codex-hooks.json` | `/home/jd/.codex/hooks.json` | `600` |
| `config/rtk-config.toml` | `/home/jd/.config/rtk/config.toml` | `600` |

## Special cases

- `wifi-boot-state.service` es referencia diagnóstica inactiva, fuera del
  manifiesto: no instalar/habilitar al restaurar.
- `grub-lid.cfg` requiere instalación root y regenerar/validar GRUB; no copiar
  un grub.cfg generado. [Diagnóstico](../boot-troubleshooting.md).
- `helium-signing-key.asc` es clave pública: convertir a keyring binario y
  comparar fingerprint oficial, no hash entre formatos.
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
La instalación actual usa copias, no una migración general a symlinks.

## Verification

Desde la raíz:

```sh
python3 tools/verify-mirror.py
# En una copia revisada del proyecto sobre la portátil:
python3 tools/verify-mirror.py --remote
```

El verificador imprime SHA256; comparar también permisos/propietarios por
separado. No aplicar configuración de red desde la única conexión remota.
[Restauración](../restore-guide.md) · [Estado](../mirror-status.md)
