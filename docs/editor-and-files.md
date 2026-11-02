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
- Sin servicios, watchers, actualizaciones ni descargas al iniciar el editor.
  El perfil y las asociaciones globales de aplicaciones no se modifican.

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
