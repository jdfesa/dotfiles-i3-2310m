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
| BlueZ | 5.82-1.1 | Debian; bluetoothctl y servicio existentes, comprobados 2026-11-15 |
| libinput / Xorg libinput | 1.28.1-1+deb13u1 / 1.5.0-1 | Debian; Magic Trackpad 2 USB/Bluetooth comprobado 2026-11-15 |
| xinput | 1.6.4-1 | Debian; ajuste de velocidad del Magic Trackpad 2 en Xorg |
| Xorg / libXi / libX11 | 21.1.16-1.3+deb13u4 / 2:1.8.2-1 / 2:1.8.12-1 | Debian; XInput 2.4 para gestos, comprobados 2026-11-15 |
| Magic Trackpad battery reader | commit 09e72af43a803575ae537b161e6504e1f8130d76 | mmarfil/magic-trackpad-battery, MIT; fuente fijada y licencia en config/bluetooth/vendor/ |
| i3-wm / i3status | 4.24-1 / 2.15-2 | Debian |
| xwallpaper | 0.7.6-1 | Debian estable; aplica el fondo de Xorg una vez y termina |
| Flameshot / xclip | 12.1.0+ds-2 / 0.13-4 | Debian estable; selección, edición X11 y portapapeles bajo demanda |
| Mesa / OpenGL observado | 25.0.7 / core 3.3 acelerado | Debian / i915 |
| Kitty | 0.41.1-2+deb13u2 | Debian |
| Zsh / zsh-common | 5.9-8+b24 / 5.9-8 | Debian estable; shell interactiva de Kitty |
| Starship | 1.22.1-5 | Debian estable; prompt de Zsh |
| xcompmgr | 1.1.8-1 | Debian; compositor básico existente para el fondo 85% de Kitty |
| btop | 1.3.2-0.1 | Debian; comprobado 2026-11-15 |
| GTK3 / Python GI | 3.24.49-3 / 3.50.0-4+b1 | Debian; gir1.2-gtk-3.0 3.24.49-3; comprobados 2026-11-15 |
| Pango / PangoCairo bindings | 1.56.3-1 | Debian; gir1.2-pango-1.0 y libpangocairo-1.0-0 existentes, posición del audio bajo demanda |
| Rofi | 1.7.5-0.1+b2 | Debian |
| Thunar | 4.20.2-1+deb13u1 | Debian; modo oscuro en i3 comprobado 2026-11-15 |
| polkitd | 126-2 | Debian, política login1 estándar |
| ALSA utils / xdg-utils | 1.2.14-1 / 1.2.1-2 | Debian |
| libasound2t64 | 1.2.14-1+deb13u1 | Debian; salida USB Speaker mediante biblioteca existente, sin servidor de audio |
| Git | 1:2.47.3-0+deb13u1 | Debian |
| GitHub CLI | 2.46.0-3 | Debian; comprobado 2026-11-02 |
| GNOME Keyring / módulo PAM | 48.0-1 / 48.0-1 | Debian; comprobado 2026-11-02 |
| libsecret-tools | 0.21.7-1 | Debian; comprobado 2026-11-02 |
| curl / jq | 8.14.1-2+deb13u5 / 1.7.1-6+deb13u4 | Debian |
| Helium | 0.19.2.1-1 | APT oficial Helium, canal stable |
| LocalSend | 1.18.2+64 | .deb oficial amd64 de [LocalSend v1.18.2](https://github.com/localsend/localsend/releases/tag/v1.18.2); uso bajo demanda, sin autostart |
| Noto Color Emoji | 2.051-0+deb13u1 | Debian estable; paquete fonts-noto-color-emoji, comprobado 2026-11-16 |
| JetBrains Mono Nerd Font | Nerd Fonts 3.5.1, base 2.304 | Publicación oficial; Mono Regular/Bold y Propo Regular; Propo comprobada 2026-11-15 |
| Codex CLI | 0.165.0, Linux x64 musl | Instalador oficial standalone |
| RTK / Engram | 1.1.0 / 3.6.0 | Binarios de publicaciones oficiales |
| Plugin Engram | 0.1.5, tag v3.6.0 | Marketplace oficial fijado |
| Neovim / runtime | 0.12.6 | Archivo oficial Linux x86_64, SHA256 verificado; comprobado 2026-11-02; Debian 0.10.4-8 sólo para recuperación |
| LazyVim / lazy.nvim | v16.0.2 / v11.17.5 | Publicaciones oficiales; commits de plugins en el lockfile; sin extras de lenguaje |
| Tree-sitter CLI | 0.26.13 | Publicación oficial Linux x86_64, SHA256 verificado; GCC y cabeceras de Debian para parsers |
| gcc / libc6-dev | 4:14.2.0-1 / 2.41-12+deb13u4 | Debian estable, sin recomendaciones |
| ripgrep / fd-find | 14.1.1-1+b4 / 10.2.0-1+b5 | Debian estable; `rg` y `fdfind` para el buscador |
| Zathura / Poppler plugin | 0.5.11-1 / 0.3.3-1 | Debian estable; comprobados 2026-11-16 en Xorg/i3 |
| Visual Studio Code | 1.146.0-1794340865 | APT oficial de Microsoft, canal stable amd64; comprobado 2026-11-15 |
| Yazi / Ya | 26.9.1-1 / 26.9.1 | APT oficial stable firmado; comprobado 2026-11-02 |
| mini.files | v0.18.0, commit a5689dae6b732955e33eec225b798d6815063179 | Sólo recuperación del perfil anterior; hashes en tools/install-mini-files.py |
| PHP CLI / extensiones | 8.4.27-1~deb13u1 | Debian estable/seguridad; [Local Web Stack](laravel-setup.md), comprobado 2026-11-18 |
| Apache / PHP module | 2.4.71-1~deb13u1 / 8.4.27-1~deb13u1 | Debian estable/seguridad; solo loopback, bajo demanda |
| acl / polkitd | 2.3.2-2+b1 / 126-2 | Debian; ACL de logs y autorización limitada de la sesión local |
| Composer | 2.8.8-1+deb13u3 | Debian estable; ejecución como jd |
| MariaDB server | 1:11.8.6-0+deb13u1 | Debian estable; inicio manual y escucha en loopback |
| phpMyAdmin | 4:5.2.2-really+dfsg-1+deb13u1 | Debian estable; Apache local bajo demanda |

Python 3 de Debian ejecuta la barra y los refrescos con biblioteca estándar.
El [volumen USB](audio-setup.md) usa libasound mediante ctypes en el tick
existente; su deslizador reutiliza GTK3 sólo mientras está abierto.
Su posición por teclado usa libX11 existente y `gir1.2-pango-1.0`, dependencia
ya presente de GTK3, sólo bajo demanda.
El calendario usa `python3-gi` y `gir1.2-gtk-3.0`; btop abre sólo bajo demanda.
Bluetooth usa BlueZ y los controladores nativos del kernel/libinput;
instalación y emparejamiento en [Bluetooth and Magic Trackpad 2](bluetooth-setup.md).
Sus indicadores usan `libsystemd0` existente mediante ctypes y la biblioteca
estándar; no requieren UPower, python3-dbus, pip, Blueman ni el daemon/timer
del proveedor.
Los [gestos del trackpad](trackpad-gestures.md) usan Python estándar y
`libxi6`/`libx11-6` mediante ctypes; Xorg y su driver libinput deben admitir
XInput 2.4. Son bibliotecas existentes de la sesión; no requieren pip,
libinput-tools, xdotool, compilación ni gestores externos de gestos.
`xfce4-terminal` y `dmenu`/`suckless-tools` permanecen instalados como
alternativas, pero no son procesos de inicio ni requisitos del lanzador Rofi.

## Debian packages

El perfil opcional de Apache/PHP 8.4, Composer, MariaDB y phpMyAdmin usa únicamente
paquetes Debian firmados. Dependencias directas, instalación bajo demanda y
recuperación en [Local Web Stack](laravel-setup.md).

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
  i3-wm i3status i3lock kitty rofi xdg-utils xcompmgr \
  fonts-dejavu-core fonts-liberation2 fonts-noto-color-emoji alsa-utils polkitd

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

El [PDF reader](pdf-reader.md) se instala por separado: usa `zathura` y
`zathura-pdf-poppler`, sin recomendaciones ni servicio.

## External packages

- [Helium y fuentes](apps-setup.md): repositorio APT firmado y licencias TTF.
- [Codex](codex-setup.md): instalador revisado, versión explícita y autenticación
  separada de la configuración.
- [RTK/Engram](development-tools.md): URLs y SHA256 fijados en
  `tools/install-user-tools.py`; sin compilación local.
- [Editor and file management](editor-and-files.md): Neovim oficial, perfil
  [LazyVim setup](lazyvim-setup.md) y Yazi desde su APT stable firmado.
- [Visual Studio Code](editor-and-files.md#visual-studio-code): APT estable
  firmado de Microsoft, restringido a `code`.

No añadir un escritorio, compositor, toolchain o servicio sólo como dependencia
implícita de una utilidad. Revisar necesidad, compatibilidad y coste de fondo.

## Maintenance

Las actualizaciones son una operación administrativa explícita. Mantener
repositorios, firmware, kernel y navegador; el contador de la barra sólo muestra
candidatos de los índices locales. Tras un cambio de versión, registrar la
comprobación relevante en [CHANGELOG.md](../CHANGELOG.md) y actualizar este inventario.
