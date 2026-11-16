# LazyVim setup

## Profile

LazyVim es el perfil predeterminado del [Neovim oficial](neovim-installation.md)
en Kitty: `nvim`, Yazi y las alternativas existentes siguen invocando el mismo
binario. Se conservan la interfaz, el explorador, el autocompletado y los
parsers base de [LazyVim](https://www.lazyvim.org/plugins). No hay extras por
lenguaje; se aplazan `lua_ls` y las instalaciones implícitas de herramientas
de Mason. Tampoco se comprueban actualizaciones de plugins en segundo plano.
Las revisiones probadas están en `config/lazyvim/lazy-lock.json`.

Python tiene resaltado sintáctico, igual que HTML y JavaScript; eso no
equivale a tener un LSP. Python es el primer candidato si se necesitan
diagnósticos o navegación. Java y web quedan por evaluar; no instalar JDK,
Node ni servidores por anticipado. Versiones y paquetes directos en
[Dependencies](dependencies.md).

## Installation

No instalar como root salvo los paquetes Debian. Revisar la simulación:

```sh
apt-get -s install --no-install-recommends gcc libc6-dev ripgrep fd-find
sudo apt-get install --no-install-recommends gcc libc6-dev ripgrep fd-find
```

La CLI de Tree-sitter de Debian 13 no alcanza el mínimo que requiere
[nvim-treesitter](https://github.com/nvim-treesitter/nvim-treesitter). Usar
el binario Linux x86_64 de la [publicación oficial](https://github.com/tree-sitter/tree-sitter/releases/tag/v0.26.13),
sin mezclar repositorios APT. Desde el checkout revisado, como `jd`:

```sh
umask 022
work=$(mktemp -d)
install -d "$work/config/nvim" "$work/data/nvim/lazy" "$work/state/nvim" "$work/cache" "$work/bin"
curl --fail --location --proto '=https' --proto-redir '=https' \
  https://github.com/tree-sitter/tree-sitter/releases/download/v0.26.13/tree-sitter-cli-linux-x64.zip \
  --output "$work/tree-sitter.zip"
printf '%s  %s\n' \
  1b781c0dc1dfefea44b5db2ec2a58440fe9d006856c3f5b3fd9a17119d1138a2 \
  "$work/tree-sitter.zip" | sha256sum --check
python3 - "$work" <<'PY'
from pathlib import Path
import sys
from zipfile import ZipFile

work = Path(sys.argv[1])
with ZipFile(work / "tree-sitter.zip") as archive:
    member, = (name for name in archive.namelist() if Path(name).name == "tree-sitter")
    target = work / "bin/tree-sitter"
    target.write_bytes(archive.read(member))
    target.chmod(0o755)
PY
"$work/bin/tree-sitter" --version
install -m 644 config/lazyvim/init.lua config/lazyvim/lazy-lock.json "$work/config/nvim/"
git clone --filter=blob:none --branch stable --no-checkout \
  https://github.com/folke/lazy.nvim.git "$work/data/nvim/lazy/lazy.nvim"
git -C "$work/data/nvim/lazy/lazy.nvim" checkout --detach 85c7ff3711b730b4030d03144f6db6375044ae82
env XDG_CONFIG_HOME="$work/config" XDG_DATA_HOME="$work/data" \
  XDG_STATE_HOME="$work/state" XDG_CACHE_HOME="$work/cache" \
  PATH="$work/bin:$PATH" BGH_LAZYVIM_SETUP=1 \
  nvim --headless -i NONE -n '+Lazy! restore' +qa!
```

Detenerse si falla un comando o cambia el lockfile sin revisión. Usar los
mismos valores XDG y PATH para abrir un archivo Python de prueba en el perfil
aislado; esperar que termine Tree-sitter. Comparar cada checkout de plugin
con su commit del lockfile. La primera instalación descarga plugins y compila
parsers, no el editor ni la CLI. No habilitar `BGH_LAZYVIM_SETUP` al iniciar el
editor normalmente.

Antes de activar, comprobar que no hay Neovim abierto y que los cuatro
directorios XDG `nvim` son rutas de usuario normales. Mover esos directorios
completos (configuración, datos, estado y caché) a un respaldo privado externo
modo 700, con nombres distintos, anotando los que no existían. Así se conservan
los enlaces anteriores, undo y ShaDa sin cargar `mini.files` por accidente.
No tocar el checkout que contienen los destinos de los enlaces antiguos.

Instalar los dos archivos de `$work/config/nvim` como copias regulares 644 en
`~/.config/nvim/`, según [manifest.json](../config/manifest.json). Mover el
árbol probado `$work/data/nvim` a `~/.local/share/nvim`; no copiar el caché de
prueba. Instalar `$work/bin/tree-sitter` como `~/.local/bin/tree-sitter` modo
755 sólo si el destino no existe o ya coincide. No cambiar `$EDITOR`, las
alternativas, paquetes Vim de recuperación ni preferencias de Yazi.

## Verification

Abrir `nvim` sin variables de staging y un archivo temporal vía Yazi.
Comprobar versión, lectura y escritura, búsqueda y parsers, y que
`:LspInfo` no muestre servidores activos en Python, Java o web.
Comparar los dos archivos de configuración contra el manifiesto.
Pendiente: medir respuesta, CPU y RAM en un proyecto representativo con una
o dos pestañas de Helium; la prueba aislada no mide rendimiento cotidiano.

## Recovery

`nvim --clean archivo` permite editar al instante sin cargar plugins.
Para volver al perfil anterior, cerrar Neovim, mover los cuatro directorios
activos a otro respaldo privado y devolver cada directorio original a su ruta,
incluidos los enlaces y cualquier ruta que originalmente no existía. No borrar
los datos escritos durante la prueba. Confirmar que Yazi sigue abriendo
`nvim`. Retirar sólo la CLI de usuario si ya no se usa; la eliminación de los
paquetes Debian es una operación aparte que requiere simulación y revisión.
No usar `autoremove` a ciegas.
