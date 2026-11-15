# Editor and file management

## Current state

Neovim y Yazi instalados el **2026-11-02**; versiones y procedencia en
[Dependencies](dependencies.md). Neovim usa configuración Lua propia y sólo
`mini.files`, no una distribución ni el generador MiniMax.

- Yazi: gestión general; vistas previas de texto/directorios, sin precargas.
  Editar texto abre Neovim en la misma terminal.
- Neovim: numeración absoluta, búsqueda sin distinguir mayúsculas salvo patrón
  con mayúsculas, splits abajo/derecha, undo persistente y colores Mocha nativos.
  La escritura copia backups sin sustituir los enlaces simbólicos.
  Indentación fallback de cuatro espacios; el runtime de cada filetype puede
  ajustarla. No hay LSP, proveedores de iconos ni otros módulos MINI activos.
- Seis archivos de usuario enlazados individualmente a fuentes residentes en
  la portátil. APT usa tres archivos regulares root:root644, nunca enlaces.
- Neovim/Yazi no añaden servicios, watchers ni descargas al inicio. Thunar y
  Visual Studio Code son [alternativas gráficas](#graphical-tools); no reemplazan
  las alternativas del editor ni se fijan asociaciones MIME nuevas.

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

```sh
apt-get -s install --no-install-recommends thunar
sudo apt-get install --no-install-recommends thunar

desktop-file-validate config/thunar/thunar.desktop
install -d -m 755 "$HOME/.local/share/applications"
install -m 644 config/thunar/thunar.desktop "$HOME/.local/share/applications/thunar.desktop"
```

El lanzador de usuario reemplaza el ID `thunar.desktop`. En **Super+Space**,
abrir **Thunar File Manager**: aplica `Adwaita:dark` sólo al proceso lanzado,
sin modificar ajustes globales de GTK. En terminal usar
`GTK_THEME=Adwaita:dark thunar "$HOME"`. Si ya está abierto con otro tema,
cerrar sus ventanas normalmente antes de lanzar la versión oscura. Verificar
una ventana real y `thunar --version`; no iniciar con `--daemon`.

Para revertir, restaurar el lanzador previo o retirar sólo la copia de usuario
si antes no existía. Thunar vuelve a su lanzador Debian. La desinstalación es
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

Fuentes desde la raíz del repositorio; destinos/modos en
[`config/manifest.json`](../config/manifest.json).

```text
config/
├── nvim/
│   ├── init.lua
│   └── lua/config/
│       ├── options.lua
│       ├── keymaps.lua
│       ├── autocmds.lua
│       └── mini.lua
└── yazi/
    ├── yazi.toml
    └── apt/
        ├── yazi.list
        ├── yazi.pref
        └── yazi-keyring.gpg
```

`init.lua` sólo fija leaders y carga módulos. Opciones, atajos y autocomandos
nativos permanecen independientes de MINI. `mini.lua` configura únicamente
el explorador. Añadir `config/nvim/after/ftplugin/<filetype>.lua` cuando un
lenguaje necesite opciones propias; no crear árboles vacíos anticipadamente.

Los paquetes descargados viven en `~/.local/share/nvim/site/pack/vendor/start/mini.files/`,
fuera de Git. Undo/ShaDa/caches permanecen en los directorios XDG de Neovim;
no enlazar esos datos ni el home completo. No mover/eliminar el checkout que
sostiene los enlaces; un cambio de ubicación exige nuevo plan y rollback.

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

### mini.files

El instalador fija tag, commit y SHA256 del archivo oficial y de cada archivo
instalado. Sólo copia código, ayuda y licencia MIT; conserva cambios existentes
deteniéndose si encuentra diferencias. No compila ni crea otro repositorio Git.

```sh
python3 tools/install-mini-files.py                 # dry-run, sin red
python3 tools/install-mini-files.py --apply          # descarga verificada explícita
python3 tools/install-mini-files.py --check          # hashes/modos/propietarios, sin red
nvim --headless -u NONE -i NONE -n \
  -c 'helptags /home/jd/.local/share/nvim/site/pack/vendor/start/mini.files/doc' -c 'qa!'
```

También admite `--apply --archive /ruta/archivo.tar.gz`, con las mismas
comprobaciones. Aunque Neovim actual incluye `vim.pack`, no se introduce otro
gestor para un único módulo fijado. No hacen falta lazy.nvim, mini.deps ni un
instalador en init.lua.

### User links

`tools/link-user-config.py` sólo selecciona entradas con `deployment=symlink`:
los seis archivos nuevos. El resto del manifiesto permanece intacto.

```sh
umask 022
# Tras revisar las fuentes públicas, normalizar también un checkout anterior.
chmod 644 config/nvim/init.lua config/nvim/lua/config/*.lua config/yazi/yazi.toml
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

Abrir `nvim archivo` o `nvim .`; `yazi` abre el gestor general. En Neovim:

| Tecla | Acción |
|---|---|
| `Space e` | Abrir mini.files en el archivo actual o directorio de trabajo |
| `Escape` en modo normal | Limpiar resaltado de búsqueda |
| `j/k`, `h/l` dentro del explorador | Mover selección, subir/entrar/abrir |
| `=` dentro del explorador | Revisar y confirmar operaciones editadas |
| `q` / `g?` dentro del explorador | Cerrar / ayuda |

En mini.files se editan nombres/líneas para crear, renombrar o retirar entradas;
se aplican con `=`, no simplemente con `:w`. `permanent_delete=false` conserva
retiradas en `~/.local/share/nvim/mini.files/trash/`; no es la papelera de Yazi.
No es un historial ni un backup: otra retirada con el mismo nombre puede
sustituir la entrada anterior. No vaciarla automáticamente. Sin el módulo,
el editor conserva opciones nativas
y `Space e` ofrece Netrw con un aviso inglés.

## Validation

```sh
python3 tools/install-mini-files.py --check
python3 tools/link-user-config.py
PYTHONDONTWRITEBYTECODE=1 \
NVIM_TEST_MINI_FILES="$HOME/.local/share/nvim/site/pack/vendor/start/mini.files" \
  python3 -m unittest discover -s tests -q
dpkg --audit
```

Las pruebas usan fixtures privados: config Lua con estado XDG aislado,
explorador y operaciones sintéticas, Yazi en pseudoterminal y rollback de
enlaces. No ejercitan archivos personales. Resultado vigente y límites en
[Verification status](mirror-status.md); necesidades futuras en [TODO](../TODO.md).
No equivalen a una restauración limpia ni a medir CPU/RAM con el navegador.

## Recovery and growth

```sh
python3 tools/link-user-config.py --rollback "$backup/journal.json"
nvim --clean archivo
```

Rollback verifica enlaces y backups antes de actuar; se detiene ante un destino
modificado y no elimina archivos ajenos ni fuentes. `--clean` permite editar
sin esta configuración. Para retirar mini.files, primero desactivar su carga
o usar el fallback; respaldar/revisar sólo su directorio instalado, no borrar
todo `~/.local/share/nvim`.

Para retirar el origen Yazi, revisar sus tres archivos root contra las fuentes
y el backup administrativo antes de eliminarlos/restaurarlos; no borrar índices
ni otras fuentes APT indiscriminadamente. La retirada de paquetes es separada;
revisar simulación y alternativas, sin autoremove ciego ni borrar datos XDG.

Agregar cada necesidad en su módulo o filetype, documentar motivo y atajos,
probar en fixtures y registrar validación/pendientes. Actualizar la revisión
fijada de MINI sólo tras revisar compatibilidad y nuevos hashes. No activar
módulos por estar disponibles ni atribuir rendimiento al número de plugins.

## References

- [Yazi installation](https://yazi-rs.github.io/docs/installation/) y
  [configuration](https://yazi-rs.github.io/docs/configuration/yazi/).
- [mini.files](https://nvim-mini.org/mini.nvim/readmes/mini-files.html) y
  [Neovim package layout](https://neovim.io/doc/user/pack/).
