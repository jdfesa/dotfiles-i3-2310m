# Desktop applications

Dependencias y versiones: [dependencies.md](dependencies.md).
Aplicar cambios con respaldo previo según [restore-guide.md](restore-guide.md).

## Terminal and launcher

Kitty y Rofi proceden de Debian, instalados sin recomendaciones. Kitty fue
probado en Intel HD 3000 con i915/Mesa, OpenGL core 3.3 y renderizado acelerado;
no se fuerza renderizado software. `xfce4-terminal` queda como alternativa.

- `config/kitty.conf` → `~/.config/kitty/kitty.conf`: Mocha opaco, Regular 11,
  ligaduras y animación de cursor desactivadas; `repaint_delay 20`.
- `config/rofi-config.rasi` → `~/.config/rofi/config.rasi`: Regular 11,
  `rofi -show drun` bajo demanda, sin daemon.
- `config/keybindings-help.txt` → `~/.config/i3/keybindings-help.txt`.

Pruebas desde la sesión gráfica existente:

```sh
glxinfo -B                  # mesa-utils; diagnóstico, no requisito de inicio
rofi -dump-config >/dev/null
kitty                       # comprobar una ventana real y cerrarla normalmente
```

Un parser o paquete instalado no demuestra que una aplicación abra correctamente.
Avisos de portales/notificaciones ausentes no justifican instalar un escritorio
si la funcionalidad necesaria ya opera.

## Helium

Repositorio APT oficial [helium-linux](https://github.com/imputnet/helium-linux#debianubuntu),
canal `stable` amd64. Ese canal no implica mantenimiento de seguridad por Debian.
Conservar sandbox y actualizaciones; nunca ejecutar como root o con `--no-sandbox`.

Fuente `config/helium.list` → `/etc/apt/sources.list.d/helium.list`.
`config/helium-signing-key.asc` es una **clave pública**, no una credencial.
Huella contrastada en la instalación de referencia:

```text
BE67 7C19 89D3 5EAB 2C5F 26C9 3516 01AD 01D6 378E
```

En Debian, después de revisar destinos existentes y contrastar la huella con
el origen oficial:

```sh
gpg --show-keys --with-fingerprint config/helium-signing-key.asc
work=$(mktemp -d)
gpg --dearmor < config/helium-signing-key.asc > "$work/helium.gpg"
sudo install -m 644 "$work/helium.gpg" /usr/share/keyrings/helium.gpg
sudo install -m 644 config/helium.list /etc/apt/sources.list.d/helium.list
sudo apt-get update
sudo apt-get install --no-install-recommends helium-bin
rm "$work/helium.gpg"
rmdir "$work"
```

El formato binario del keyring no tiene el mismo SHA256 que la fuente ASCII.
Verificar fingerprint y firma APT, no desactivar comprobaciones para instalar.

```sh
xdg-settings set default-web-browser helium.desktop
xdg-mime default helium.desktop x-scheme-handler/http x-scheme-handler/https
```

Comprobar ventana real como cuenta de sesión, versión y navegador predeterminado.
Respaldar `mimeapps.list` antes de restaurar: puede contener handlers adicionales.

## Fonts

Sólo JetBrains Mono Nerd Font Mono **Regular/Bold** y `BGH Status Icons`.
Procedencia, hashes y licencias en [config/fonts/README.md](../config/fonts/README.md).
Regular se utiliza en barra (10), Rofi/Kitty (11); Bold no se fuerza en la barra.

```sh
install -d "$HOME/.local/share/fonts/bgh-font-licenses"
install -m 644 config/fonts/*.ttf config/bgh-status-icons.ttf "$HOME/.local/share/fonts/"
install -m 644 config/fonts/OFL.txt config/fonts/UPSTREAM.md "$HOME/.local/share/fonts/bgh-font-licenses/"
fc-cache "$HOME/.local/share/fonts"
fc-match 'JetBrainsMono Nerd Font Mono'
```

Si i3bar conserva cajas en lugar de iconos, renovar i3 con `i3-msg restart`
conservando ventanas, no cerrar sesión o reiniciar Debian sólo para las fuentes.
Kitty aplica su configuración en terminales nuevas.

## Audio

ALSA utils proporciona `alsamixer`/`amixer`. Sin dispositivo enumerado, la barra
muestra `No audio` y omite consultas a un mixer inexistente. La tarjeta/mixer y
la reproducción del adaptador externo están pendientes; no añadir servidores
de audio ni desmutear/subir volumen automáticamente.

Codex y RTK/Engram son opcionales: [codex-setup.md](codex-setup.md) y
[development-tools.md](development-tools.md).
