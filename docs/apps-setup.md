# Desktop applications

Dependencias y versiones: [dependencies.md](dependencies.md).
Aplicar cambios con respaldo previo según [restore-guide.md](restore-guide.md).

La configuración pública de usuario se enlaza siguiendo
[User configuration links](user-config-links.md); sus comandos distinguen
el dry-run del despliegue con respaldo. No instalar copias paralelas de scripts.

## Terminal and launcher

Kitty y Rofi proceden de Debian, instalados sin recomendaciones. Kitty fue
probado en Intel HD 3000 con i915/Mesa, OpenGL core 3.3 y renderizado acelerado;
no se fuerza renderizado software. `xfce4-terminal` queda como alternativa.

- `config/kitty.conf` → `~/.config/kitty/kitty.conf`: Mocha al 85%, Regular 11,
  ligaduras y animación de cursor desactivadas; `repaint_delay 20`.
  Pestañas y directorio activo en [Kitty setup](kitty-setup.md).
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

JetBrains Mono Nerd Font Mono **Regular/Bold**, **Propo Regular** y `BGH Status Icons`.
Procedencia, hashes y licencias en [config/fonts/README.md](../config/fonts/README.md).
Mono Regular se utiliza en el texto de barra (10), Rofi/Kitty (11);
Propo Regular en iconos de barra (12). Bold no se fuerza en la barra.

```sh
python3 tools/link-user-config.py  # Dry-run; apply the reviewed link plan separately.
fc-cache "$HOME/.local/share/fonts"
fc-match 'JetBrainsMono Nerd Font Mono'
fc-match 'JetBrainsMono Nerd Font Propo'
```

Si i3bar conserva cajas en lugar de iconos, renovar i3 con `i3-msg restart`
conservando ventanas, no cerrar sesión o reiniciar Debian sólo para las fuentes.
Kitty aplica su configuración en terminales nuevas.

### Browser emoji

Instalar [Noto Color Emoji](https://packages.debian.org/trixie/fonts-noto-color-emoji)
desde Debian estable firmado. El paquete instala la fuente en
`/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf` (root:root, 644); el trigger
de Fontconfig actualiza la caché. La licencia se conserva en
`/usr/share/doc/fonts-noto-color-emoji/copyright`. No añadir copias al home,
reglas propias de fallback ni cambiar las fuentes de texto, i3bar o Kitty. El
archivo lo gestiona APT; no es una fuente del manifiesto del repositorio.

```sh
apt-cache policy fonts-noto-color-emoji
apt-get -s install --no-install-recommends fonts-noto-color-emoji
sudo apt-get install --no-install-recommends fonts-noto-color-emoji
dpkg -V fonts-noto-color-emoji
fc-match emoji
for point in 1f44d 1f680 1f642; do
  fc-match -f '%{family}\n' "emoji:charset=$point"
done
```

`fc-match` debe mostrar Noto Color Emoji y `dpkg -V` no debe informar cambios.
Comprobar el render en Helium con 👍 🚀 🙂 y, además, una secuencia compuesta
como 👩‍💻. Si un proceso ya abierto no detecta la fuente, guardar el trabajo,
cerrar Helium normalmente y volver a abrirlo; no reiniciar i3 ni Debian.

Para volver al estado anterior si el paquete no estaba instalado, simular y
retirar sólo esta dependencia si APT no propone otros cambios:

```sh
apt-get -s remove fonts-noto-color-emoji
sudo apt-get remove fonts-noto-color-emoji
```

## PDF reader

Los archivos PDF se abren en Zathura con modo oscuro. Helium sigue como
navegador predeterminado. Instalación y reversión en [PDF reader](pdf-reader.md).

## Audio

ALSA/libasound controla la salida del adaptador USB mediante el deslizador de
[USB audio](audio-setup.md). `alsamixer`/`amixer` quedan disponibles para
diagnóstico. La barra detecta el adaptador en su tick normal, sin servidores de
audio ni cambios automáticos de volumen o mute al conectar.

Codex y RTK/Engram son opcionales: [codex-setup.md](codex-setup.md) y
[development-tools.md](development-tools.md).
