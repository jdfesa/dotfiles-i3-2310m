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

### Native file chooser

**Save image as…**, **Save as…** y **Open File** usan el selector GTK3 del
proceso Helium. La ventana **Save File** permite elegir carpeta y nombre;
**Show in folder** abre [Thunar](editor-and-files.md#thunar) por otra ruta.
El tema oscuro de las páginas o del navegador no configura ese selector.

`scripts/launch-helium.sh` se enlaza como `~/.local/bin/helium`, modo755,
según el [manifest.json](../config/manifest.json). Exporta
`GTK_THEME=Adwaita:dark` y ejecuta `/usr/bin/helium` con todos los argumentos
originales; el paquete APT y su sandbox siguen intactos. La sesión i3 antepone
`~/.local/bin` en `PATH`: sus dos atajos y las entradas `Exec=helium` del
desktop oficial usan la misma entrada. No se cambia el tema GTK global, los
handlers MIME ni las preferencias privadas del perfil. No necesita portales,
paquetes nuevos ni procesos residentes.

La regla de `config/i3-config` se limita a `class=Helium` y
`window_role=GtkFileChooserDialog`: abre el selector flotante, centrado y de
1000×640 píxeles. Mantiene **Save** y **Cancel** visibles en la pantalla interna
1366×768 con barra superior. El tamaño que GTK conserve en su estado privado
no debe dejar esos botones fuera de pantalla. La regla sólo fija la geometría
inicial; permite redimensionar manualmente después.

#### Installation and validation

Como `jd`, revisar el destino y respaldar la fuente i3 activa antes de editarla.
Preparar el enlace, comprobar el plan y aplicarlo con respaldo privado externo:

```sh
umask 022
sh -n scripts/launch-helium.sh
i3 -C -c config/i3-config
python3 tools/link-user-config.py --source scripts/launch-helium.sh
backup="$HOME/.local/state/bgh-config-backups/helium-launcher-$(date -u +%Y%m%dT%H%M%SZ)"
python3 tools/link-user-config.py --source scripts/launch-helium.sh \
  --apply --backup-dir "$backup"
command -v helium
readlink "$HOME/.local/bin/helium"
i3-msg reload
```

`command -v` debe resolver el enlace de usuario, no `/usr/bin/helium`.
La recarga de i3 aplica la regla a selectores nuevos sin cerrar ventanas.
Para corregir uno que ya quedó fuera de pantalla, sin confirmar ni cancelar
su operación:

```sh
i3-msg '[class="^Helium$" window_role="^GtkFileChooserDialog$"] resize set 1000 640, move position center'
```

El color se hereda cuando inicia el proceso principal de Helium. Abrir otra
ventana con un navegador anterior todavía en ejecución reutiliza ese proceso
y no cambia su entorno. Guardar trabajo y coordinar un cierre normal completo
antes de volver a abrirlo; no terminar procesos ni cerrar aplicaciones ajenas.

Validación acotada: usar una imagen sintética desde un servidor HTTP local
temporal y **Save image as…**. Comprobar el selector oscuro, ambos botones
visibles, guardar en un directorio temporal nuevo y comparar el SHA256 con
la imagen original. Reabrir y usar **Cancel**: no debe crear otro archivo.
Un perfil temporal separado permite probar un arranque nuevo sin cerrar el
navegador personal. Conservar el sandbox y no copiar el perfil personal a ese
directorio. Cerrar sólo las ventanas de prueba y retirar el servidor temporal.
Comprobado con Helium 0.19.2.1-1, GTK 3.24.49 y la pantalla interna.

#### Recovery

Revertir sólo el enlace mediante el journal de su operación:

```sh
python3 tools/link-user-config.py --rollback "$backup/journal.json"
```

Restaurar la fuente i3 revisada del respaldo, validar con `i3 -C` y recargar.
No reemplazar todo el checkout ni retirar otras reglas. El tema anterior vuelve
en el siguiente arranque normal de Helium; no es necesario reiniciar Debian,
cambiar asociaciones ni modificar el perfil privado.

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
