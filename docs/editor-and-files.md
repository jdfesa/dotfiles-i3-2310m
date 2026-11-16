# Editor and file management

## Current state

Neovim usa [LazyVim setup](lazyvim-setup.md) como perfil predeterminado.
[Neovim installation](neovim-installation.md) documenta el binario oficial y
sus alternativas. Yazi gestiona archivos desde la misma terminal; limita las
vistas previas a texto y directorios y abre texto con `nvim`. No se cambian
asociaciones MIME ni el editor global del sistema.

Thunar y Visual Studio Code siguen como [alternativas gráficas](#graphical-tools)
bajo demanda. Versiones y procedencia en [Dependencies](dependencies.md).

## Graphics compatibility

Zed no se instala en esta portátil. La Intel HD 3000 (Sandy Bridge) no aparece
como dispositivo Vulkan; la consulta local del **2026-11-02** sólo enumeró
`llvmpipe`, de tipo CPU. Tener el loader/ICD de Vulkan instalado o acelerar
OpenGL no proporciona por sí mismo una GPU Vulkan compatible.

[Zed usa Vulkan para su interfaz en Linux](https://zed.dev/docs/linux#graphics-issues).
No se fuerza renderizado por CPU ni se cambian drivers para eludir esta
limitación: se conserva el presupuesto de CPU para el trabajo y el navegador.
No se descargó/instaló Zed ni se creó configuración vacía; reconsiderar sólo
ante un alcance nuevo o hardware compatible.

## Graphical tools

### Thunar

Thunar funciona bajo demanda en i3 con GTK3 existente. Se instala desde Debian
sin GVfs, tumbler, gestor de volúmenes ni escritorio Xfce; integraciones de
papelera y volúmenes no forman parte de esta instalación mínima.

#### Installation

Como `jd`, revisar y respaldar en privado los dos destinos del
[manifest.json](../config/manifest.json) antes de instalar sus copias regulares
con modo644. Si un destino no existía, registrar esa ausencia para la reversión.

```sh
apt-get -s install --no-install-recommends thunar
sudo apt-get install --no-install-recommends thunar

desktop-file-validate config/thunar/thunar.desktop
install -d -m 755 "$HOME/.local/share/applications" \
  "$HOME/.config/systemd/user/thunar.service.d"
install -m 644 config/thunar/thunar.desktop "$HOME/.local/share/applications/thunar.desktop"
install -m 644 config/thunar/10-dark-theme.conf \
  "$HOME/.config/systemd/user/thunar.service.d/10-dark-theme.conf"
systemctl --user daemon-reload
```

El lanzador de usuario reemplaza el ID `thunar.desktop`. En **Super+Space**,
abrir **Thunar File Manager**: aplica `Adwaita:dark` sólo al proceso lanzado,
sin modificar ajustes globales de GTK. En terminal usar
`GTK_THEME=Adwaita:dark thunar "$HOME"`.

**Show in folder** de Helium usa la interfaz D-Bus `org.freedesktop.FileManager1`,
que no pasa por el lanzador. Los descriptores Debian de esa interfaz y de
`org.xfce.Thunar` delegan en `thunar.service`; el drop-in añade el mismo
`GTK_THEME` al servicio de usuario existente sin sustituir su comando.
No habilitarlo al inicio ni lanzar manualmente `--daemon`: D-Bus lo activa
bajo demanda. No se añaden unidades, paquetes ni sondeos; las asociaciones
MIME se conservan. La precedencia de configuración del servicio se describe
en [systemd.unit](https://www.freedesktop.org/software/systemd/man/latest/systemd.unit.html),
y la interfaz en [File Manager Interface](https://www.freedesktop.org/wiki/Specifications/file-manager-interface/).

Una instancia que ya estaba abierta conserva su tema; cerrar ventanas puede
dejar el daemon de Debian activo. Esperar a que terminen todas las operaciones
y cerrar las ventanas de Thunar antes de ejecutar `thunar --quit`. La siguiente
apertura recibe el ajuste nuevo. No renovar Thunar mientras haya copias,
movimientos o diálogos activos; no reiniciar el navegador ni la sesión.

#### Validation

```sh
thunar --version
systemd-analyze --user verify thunar.service
systemctl --user show thunar.service -p Environment
```

`Environment` debe incluir `GTK_THEME=Adwaita:dark`. Comprobar una ventana real
desde **Thunar File Manager** y otra mediante la misma interfaz del navegador,
con un archivo temporal ajeno a las descargas personales:

```sh
probe=$(mktemp -d /tmp/thunar-dark-check.XXXXXX)
touch "$probe/theme-check.txt"
gdbus call --session --dest org.freedesktop.FileManager1 \
  --object-path /org/freedesktop/FileManager1 \
  --method org.freedesktop.FileManager1.ShowItems \
  "['file://$probe/theme-check.txt']" ''
```

Ambas ventanas deben verse oscuras. Para comprobar una activación nueva por
D-Bus, usar primero `thunar --quit` sólo cuando no queden ventanas ni operaciones;
así no se reutiliza una instancia que ya tenía el tema del lanzador.
Cerrar únicamente la ventana de comprobación y retirar el fixture:

```sh
rm "$probe/theme-check.txt"
rmdir "$probe"
```

#### Recovery

Restaurar los dos archivos previos o retirar sólo las copias de usuario que
antes no existían; no eliminar otros drop-ins de `thunar.service`. Ejecutar
`systemctl --user daemon-reload` y renovar Thunar con las mismas precauciones.
Sin estas copias vuelve al tema de sus rutas Debian. La desinstalación es
independiente; revisar `apt-get -s remove thunar`, sin autoremove a ciegas.

### Visual Studio Code

El paquete `code` proviene del [APT oficial estable de Microsoft](https://code.visualstudio.com/docs/setup/linux).
Se usa amd64 y pin sólo para `code`, no para Insiders ni para otros paquetes.
La huella de la [clave pública](https://learn.microsoft.com/en-us/linux/packages)
se contrastó con la firma real de `InRelease`:
`BC52 8686 B50D 79E3 39D3 721C EB3E 94AD BE12 29CF`.
Respaldar destinos existentes en privado antes de instalar archivos de sistema.

```sh
gpg --show-keys --with-fingerprint config/vscode/apt/microsoft.asc
sudo install -o root -g root -m 644 config/vscode/apt/microsoft.asc /etc/apt/keyrings/bgh-vscode.asc
sudo install -o root -g root -m 644 config/vscode/apt/vscode.sources /etc/apt/sources.list.d/vscode.sources
sudo install -o root -g root -m 644 config/vscode/apt/vscode.pref /etc/apt/preferences.d/vscode
sudo apt-get -o Dir::Etc::sourcelist=/etc/apt/sources.list.d/vscode.sources \
  -o Dir::Etc::sourceparts=- -o APT::Get::List-Cleanup=false \
  -o APT::Update::Error-Mode=any update
apt-cache policy code code-insiders
apt-get -s install --no-install-recommends code
printf '%s\n' 'code code/add-microsoft-repo boolean false' | sudo debconf-set-selections
sudo apt-get install --no-install-recommends code
```

El ajuste de debconf evita que el paquete gestione otra copia del origen.
Abrir `code --version` y probar **Visual Studio Code** como usuario normal en i3.
No se configura inicio automático, cuenta, extensiones ni flags que desactiven
el sandbox o la aceleración. Ajustes, proyectos y datos de extensión no forman
parte del espejo. Para retirar el origen, restaurar o retirar sólo sus tres
archivos según el respaldo; simular la retirada de `code` por separado.

## Layout

`config/lazyvim/` contiene el perfil predeterminado y su lockfile;
`config/nvim/` queda como fuente del perfil Lua de recuperación con
`mini.files`, no se instala sobre LazyVim. `config/yazi/` contiene la
configuración de archivos y su metadato APT. Los destinos y modos activos
se declaran en [manifest.json](../config/manifest.json); plugins, historial,
undo y cachés son datos privados, no se enlazan ni se publican.

## Installation

Ejecutar desde una copia revisada en la portátil como `jd`. Revisar destinos
y respaldarlos privadamente fuera del árbol antes de reemplazar archivos.
No ejecutar estos pasos automáticamente durante login o arranque de Neovim.

### Debian packages

Neovim activo procede del archivo estable oficial, no del paquete Debian;
ver [Neovim installation](neovim-installation.md) para instalación, actualización
manual, alternativas y recuperación. Se conserva el paquete Debian como respaldo.
Yazi usa su
[APT oficial stable](https://github.com/yazi-rs/builds), autenticado por clave
Ed25519 con fingerprint público:

```text
B77B 412E 5B65 3539 B786 95DC 9243 8579 6056 0E6C
```

La clave del árbol se contrastó con el proveedor; SHA256 y ubicación tienen
regresión. Comprobar su fingerprint antes de instalarla. El pin permite sólo
el paquete `yazi` desde este origen, no sustituir paquetes Debian arbitrarios.

```sh
gpg --batch --show-keys --with-fingerprint config/yazi/apt/yazi-keyring.gpg
sudo install -o root -g root -m 644 config/yazi/apt/yazi-keyring.gpg /usr/share/keyrings/yazi-keyring.gpg
sudo install -o root -g root -m 644 config/yazi/apt/yazi.list /etc/apt/sources.list.d/yazi.list
sudo install -o root -g root -m 644 config/yazi/apt/yazi.pref /etc/apt/preferences.d/yazi

# Refresco explícito limitado al origen nuevo; conserva los otros índices.
sudo apt-get update -o Dir::Etc::sourcelist=sources.list.d/yazi.list \
  -o Dir::Etc::sourceparts=- -o APT::Get::List-Cleanup=0
apt-get -s --no-install-recommends --no-upgrade install yazi
sudo apt-get install --no-install-recommends --no-upgrade yazi
```

La instalación APT inicial, incluido el Neovim Debian de recuperación, añadió
once paquetes sin recomendaciones multimedia/búsqueda/portapapeles. `file` ya
estaba instalado. vi/vim/ex/view/vimdiff seleccionan ahora el Neovim oficial;
no se añaden aliases ni se cambia `$EDITOR` o la alternativa global `editor`.

### User links

`tools/link-user-config.py` sólo selecciona entradas con `deployment=symlink`:
sólo la configuración de Yazi en este perfil. El resto del manifiesto permanece intacto.

```sh
umask 022
# Tras revisar las fuentes públicas, normalizar también un checkout anterior.
chmod 644 config/yazi/yazi.toml
python3 tools/link-user-config.py                    # revisar el plan completo
backup="$HOME/.local/state/bgh-config-backups/productivity-$(date -u +%Y%m%dT%H%M%SZ)"
python3 tools/link-user-config.py --apply --backup-dir "$backup"
python3 tools/link-user-config.py                    # todos unchanged
```

Rechaza fuentes/destinos inseguros, padres enlazados, archivos diferentes y
enlaces distintos/rotos. Una copia regular idéntica puede migrarse tras backup.
También rechaza una fuente con modo incorrecto: Git no conserva los bits de
lectura/escritura 644 frente a 664. No omitir esta comprobación después de un pull.
El directorio de respaldo debe ser nuevo, externo y privado; el journal600
registra destinos ausentes o copias anteriores. No sustituye una revisión de
preferencias de aplicaciones. Los enlaces tienen modo de sistema 777; el
manifiesto exige 644 al archivo fuente y propiedad de la cuenta en ambos.

## Operation

Abrir `nvim archivo` o `nvim .`; `yazi` abre el gestor general. En LazyVim,
`Space e` abre el explorador y `Space Space` busca archivos en el proyecto.
Ver [LazyVim keymaps](https://www.lazyvim.org/keymaps) para la lista completa.

## Validation

```sh
python3 tools/link-user-config.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
dpkg --audit
```

La suite incluye fixtures de Yazi, de rollback de enlaces y del perfil Lua de
recuperación, sin usar documentos personales. La validación del perfil activo
y el trabajo pendiente están en [LazyVim setup](lazyvim-setup.md).

## Recovery and growth

Para volver al perfil anterior o editar sin plugins, ver
[LazyVim recovery](lazyvim-setup.md#recovery). El perfil de recuperación
usa `mini.files` fijado por `tools/install-mini-files.py`; el paquete y su
papelera no se instalan sobre LazyVim. Para deshacer un cambio de enlace de
Yazi, ejecutar `python3 tools/link-user-config.py --rollback "$backup/journal.json"`
con el respaldo de esa operación.

Para retirar el origen Yazi, revisar sus tres archivos root contra las fuentes
y el backup administrativo antes de eliminarlos/restaurarlos; no borrar índices
ni otras fuentes APT indiscriminadamente. Revisar la simulación antes de retirar
paquetes, sin autoremove a ciegas ni borrar datos XDG.

## References

- [Yazi installation](https://yazi-rs.github.io/docs/installation/) y
  [configuration](https://yazi-rs.github.io/docs/configuration/yazi/).
- [mini.files](https://nvim-mini.org/mini.nvim/readmes/mini-files.html) y
  [Neovim package layout](https://neovim.io/doc/user/pack/).
