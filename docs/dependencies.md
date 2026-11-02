# Dependencies and versions

Base verificada el **2026-11-01** en Debian 13 amd64. Estas versiones identifican
la configuración probada; no son una orden de congelar paquetes ni de omitir
actualizaciones de seguridad. La disponibilidad futura de versiones puede variar.

## Inventory

| Componente | Versión comprobada | Procedencia |
|---|---|---|
| Debian / kernel | 13.7 / 6.12.111+deb13-amd64 | Debian estable/seguridad |
| systemd | 257.13-1~deb13u1 | Debian |
| Intel microcode | 3.20251111.1~deb13u1 | Debian, non-free-firmware |
| NetworkManager | 1.52.1 | Debian |
| firmware-realtek | 20250410-2 | Debian, non-free-firmware |
| rfkill | 2.41.5-0+deb13u1 | Debian |
| i3-wm / i3status | 4.24-1 / 2.15-2 | Debian |
| Mesa / OpenGL observado | 25.0.7 / core 3.3 acelerado | Debian / i915 |
| Kitty | 0.41.1-2+deb13u2 | Debian |
| Rofi | 1.7.5-0.1+b2 | Debian |
| polkitd | 126-2 | Debian, política login1 estándar |
| ALSA utils / xdg-utils | 1.2.14-1 / 1.2.1-2 | Debian |
| Git | 1:2.47.3-0+deb13u1 | Debian |
| GitHub CLI | 2.46.0-3 | Debian; comprobado 2026-11-02 |
| GNOME Keyring / módulo PAM | 48.0-1 / 48.0-1 | Debian; comprobado 2026-11-02 |
| libsecret-tools | 0.21.7-1 | Debian; comprobado 2026-11-02 |
| curl / jq | 8.14.1-2+deb13u5 / 1.7.1-6+deb13u4 | Debian |
| Helium | 0.19.2.1-1 | APT oficial Helium, canal stable |
| JetBrains Mono Nerd Font | Nerd Fonts 3.5.1, base 2.304 | Publicación oficial; sólo Regular/Bold |
| Codex CLI | 0.165.0, Linux x64 musl | Instalador oficial standalone |
| RTK / Engram | 1.1.0 / 3.6.0 | Binarios de publicaciones oficiales |
| Plugin Engram | 0.1.5, tag v3.6.0 | Marketplace oficial fijado |
| Neovim / runtime | 0.12.6 | Archivo oficial Linux x86_64, SHA256 verificado; comprobado 2026-11-02; Debian 0.10.4-8 sólo para recuperación |
| Yazi / Ya | 26.9.1-1 / 26.9.1 | APT oficial stable firmado; comprobado 2026-11-02 |
| mini.files | v0.18.0, commit a5689dae6b732955e33eec225b798d6815063179 | Módulo oficial standalone, hashes fijados en tools/install-mini-files.py |

Python 3 de Debian ejecuta la barra y los refrescos con biblioteca estándar.
`xfce4-terminal` y `dmenu`/`suckless-tools` permanecen instalados como
alternativas, pero no son procesos de inicio ni requisitos del lanzador Rofi.

## Debian packages

En una instalación nueva, revisar los repositorios Debian firmados y la sección
`non-free-firmware` para los paquetes de firmware. Los siguientes grupos
describen dependencias, **no un instalador automático del equipo**.

```sh
# Red y firmware; no migrar una conexión SSH en uso a ciegas.
sudo apt-get install --no-install-recommends \
  network-manager iw rfkill wpasupplicant firmware-realtek intel-microcode

# Sesión gráfica mínima y aplicaciones.
sudo apt-get install --no-install-recommends \
  xserver-xorg-core xserver-xorg-input-libinput libgl1-mesa-dri \
  xinit x11-xserver-utils xauth dbus-user-session \
  i3-wm i3status i3lock kitty rofi xdg-utils \
  fonts-dejavu-core fonts-liberation2 alsa-utils polkitd

# Scripts y herramientas de instalación/desarrollo.
sudo apt-get install --no-install-recommends \
  python3 git curl jq wget ca-certificates gpg
```

`mesa-utils` proporciona `glxinfo` para comprobar gráficos; no se necesita en
cada inicio. La generación de la fuente de iconos es opcional y usa
`tools/requirements-font-build.txt` en un entorno de desarrollo, no en la sesión.

La autenticación Git usa además los paquetes de [Git workflow](git-workflow.md).
Instalación comprobada sin recomendaciones: 22 paquetes nuevos, 17.1 MB de
descarga y 79.4 MB adicionales; sin upgrades, compilación ni escritorio completo.
El servicio de secretos es local a la cuenta; el agente SSH adicional de gcr4
queda deshabilitado. No se midió aquí carga sostenida de CPU.

## External packages

- [Helium y fuentes](apps-setup.md): repositorio APT firmado y licencias TTF.
- [Codex](codex-setup.md): instalador revisado, versión explícita y autenticación
  separada de la configuración.
- [RTK/Engram](development-tools.md): URLs y SHA256 fijados en
  `tools/install-user-tools.py`; sin compilación local.
- [Editor y archivos](editor-and-files.md): Neovim estable oficial, Yazi APT stable
  firmado y sólo mini.files fijado, sin recomendaciones ni descargas al inicio.

No añadir un escritorio, compositor, toolchain o servicio sólo como dependencia
implícita de una utilidad. Revisar necesidad, compatibilidad y coste de fondo.

## Maintenance

Las actualizaciones son una operación administrativa explícita. Mantener
repositorios, firmware, kernel y navegador; el contador de la barra sólo muestra
candidatos de los índices locales. Tras un cambio de versión, registrar la
comprobación relevante en [CHANGELOG.md](../CHANGELOG.md) y actualizar este inventario.
