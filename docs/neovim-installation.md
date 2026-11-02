# Neovim installation

## Source and selection

Se usa la última estable revisada, **v0.12.6**, no nightly. El archivo oficial
Linux x86_64 evita compilar en Sandy Bridge; se comprobó con glibc 2.41 y la
configuración existente. No implica una mejora medida de CPU/RAM.

- [Release oficial](https://github.com/neovim/neovim/releases/tag/v0.12.6).
- Archivo: `nvim-linux-x86_64.tar.gz`, 11 404 582 bytes.
- SHA256 contrastado con `digest` del
  [API oficial de la release](https://api.github.com/repos/neovim/neovim/releases/tags/v0.12.6):
  `474430d53e6264f6d6dd18db42d6dc9df3a1b56ca9e88a325bbf860e1a811d87`.

Binario, runtime, ayuda y licencias juntos en `/opt/nvim-0.12.6`, root:root,
directorios/ejecutables755 y datos644. Los enlaces administrativos apuntan allí,
nunca a un home escribible. `/usr/local/bin/nvim` precede a `/usr/bin/nvim`;
Yazi y el desktop entry existente ejecutan `nvim`. vi/vim/ex/view/vimdiff usan
alternativas de prioridad60 en modo automático. `editor` continúa sin cambios.
Los wrappers ex/view/vimdiff conservan `-e`/`-R`/`-d`: los de Debian fijan
`/usr/bin/nvim`, por lo que cambiar sólo PATH sería insuficiente.

El paquete Debian y su runtime quedan disponibles explícitamente en
`/usr/bin/nvim`; no se reemplaza ningún archivo propiedad de dpkg. **APT no
actualiza la copia de /opt**: revisar nuevas estables y sus cambios incompatibles,
fijar nuevo URL/hash, probar y cambiar la selección en una operación manual.
No actualizar MINI ni añadir `vim.pack`, LSP o servicios como efecto colateral.

## Installation

En la portátil como `jd`, tras revisar destinos, propietarios y las consultas
`update-alternatives --query` de los cinco grupos. El procedimiento comprobado
parte de destinos nuevos y alternativas automáticas; detenerse si hay archivos
o selecciones diferentes. Conservar un baseline administrativo privado antes
de cambiar nada; no sobrescribir ni usar `ln -sf`.

Comprobar el éxito de cada orden antes de continuar; un fallo de checksum o
preflight detiene la instalación. Descargar y comprobar **antes de ejecutar**:

```sh
work=$(mktemp -d)
archive="$work/nvim-linux-x86_64.tar.gz"
curl --fail --location --proto '=https' --proto-redir '=https' \
  https://github.com/neovim/neovim/releases/download/v0.12.6/nvim-linux-x86_64.tar.gz \
  --output "$archive"
printf '%s  %s\n' \
  474430d53e6264f6d6dd18db42d6dc9df3a1b56ca9e88a325bbf860e1a811d87 \
  "$archive" | sha256sum --check
tar -xzf "$archive" -C "$work"
"$work/nvim-linux-x86_64/bin/nvim" --version
"$work/nvim-linux-x86_64/bin/nvim" --headless --clean -i NONE -n +qa!
```

Ejecutar la batería del [editor](editor-and-files.md#validation) con
`PATH="$work/nvim-linux-x86_64/bin:$PATH"` antes de activar. El checksum no es
una firma independiente: la confianza procede del proveedor oficial vía HTTPS.

Instalación privilegiada, sin ejecutar Neovim como root. Revalidar el archivo
desde staging **root:root700** después de copiarlo, para no extraer directamente
desde un directorio modificable por la cuenta:

```sh
prefix=/opt/nvim-0.12.6
test ! -e "$prefix" && test ! -L "$prefix"
test ! -e /usr/local/bin/nvim && test ! -L /usr/local/bin/nvim
test ! -e /usr/local/share/man/man1/nvim.1 && test ! -L /usr/local/share/man/man1/nvim.1
backup=$(sudo mktemp -d /var/backups/bgh-neovim.XXXXXX)
sudo sh -c 'for n in vi vim ex view vimdiff; do update-alternatives --query "$n"; done > "$1/alternatives-before.txt"
printf "%s\n" /opt/nvim-0.12.6 /usr/local/bin/nvim /usr/local/share/man/man1/nvim.1 > "$1/previously-absent.txt"' sh "$backup"
stage=$(sudo mktemp -d /var/tmp/bgh-neovim.XXXXXX)
sudo install -o root -g root -m 600 "$archive" "$stage/archive.tar.gz"
printf '%s  %s\n' \
  474430d53e6264f6d6dd18db42d6dc9df3a1b56ca9e88a325bbf860e1a811d87 \
  "$stage/archive.tar.gz" | sudo sha256sum --check
sudo install -d -o root -g root -m 755 "$prefix"
sudo sh -c 'umask 022; exec tar -xzf "$1/archive.tar.gz" -C "$2" --strip-components=1 --no-same-owner' sh "$stage" "$prefix"
sudo sh -c 'gzip -n -c "$1/share/man/man1/nvim.1" > "$1/share/man/man1/nvim.1.gz"' sh "$prefix"
sudo chmod 644 "$prefix/share/man/man1/nvim.1.gz"
for pair in ex:e view:R vimdiff:d; do
  name=${pair%:*}; flag=${pair#*:}
  printf '#!/bin/sh\nexec %s/bin/nvim -%s "$@"\n' "$prefix" "$flag" \
    | sudo tee "$prefix/bin/$name" >/dev/null
  sudo chmod 755 "$prefix/bin/$name"
done
sudo ln -s "$prefix/bin/nvim" /usr/local/bin/nvim
sudo install -d -o root -g root -m 755 /usr/local/share/man/man1
sudo ln -s "$prefix/share/man/man1/nvim.1" /usr/local/share/man/man1/nvim.1
for name in vi vim; do
  sudo update-alternatives --install "/usr/bin/$name" "$name" "$prefix/bin/nvim" 60
done
for name in ex view vimdiff; do
  sudo update-alternatives --install "/usr/bin/$name" "$name" "$prefix/bin/$name" 60
done
hash -r
```

Tras verificar, retirar únicamente el staging y la descarga temporal conocidos;
conservar el pequeño baseline privado. El árbol de /opt y los wrappers generados
son artefactos de instalación, no fuentes ni binarios para añadir a Git.

## Validation

```sh
command -v nvim
nvim --version
nvim --headless -i NONE -n \
  '+lua assert(vim.fn.has("nvim-0.12")==1); assert(type(MiniFiles)=="table")' +qa!
view --headless -u NONE -i NONE -n '+lua assert(vim.o.readonly)' +qa!
vimdiff --headless -u NONE -i NONE -n '+lua assert(vim.wo.diff)' +qa!
for name in vi vim ex view vimdiff; do update-alternatives --query "$name"; done
dpkg --audit
```

Repetir tests, checks del módulo/enlaces y revisión de propietarios/modos.
Probar edición desde Yazi sólo con un fixture temporal, no documentos personales.
No requiere reiniciar i3, terminales o sesión. Actualizar inventario/estado y
sincronizar por GitHub; regenerar el snapshot secundario desde el commit limpio.

## Recovery

`nvim --clean archivo` omite configuración/plugins. `/usr/bin/nvim --clean archivo`
usa explícitamente la versión Debian conservada; es un recurso temporal, no la
selección habitual. Debian 0.10.4-8 tiene pendiente
[CVE-2026-11487](https://security-tracker.debian.org/tracker/CVE-2026-11487),
corregida upstream desde 0.12.3; no volver a ella permanentemente sin revisar fixes.

Para deshacer esta instalación, comprobar primero que los enlaces siguen apuntando
al prefijo esperado y cotejar el baseline. Retirar **sólo** las alternativas nuevas:

```sh
for name in vi vim; do
  sudo update-alternatives --remove "$name" /opt/nvim-0.12.6/bin/nvim
done
for name in ex view vimdiff; do
  sudo update-alternatives --remove "$name" "/opt/nvim-0.12.6/bin/$name"
done
# Tras comprobar sus destinos exactos:
sudo unlink /usr/local/bin/nvim
sudo unlink /usr/local/share/man/man1/nvim.1
hash -r
/usr/bin/nvim --version
```

Las selecciones automáticas previas se recuperan sin cambiar `editor`; si el
baseline difiere, restaurar su selección, no imponer `--auto` indiscriminadamente.
Retirar el prefijo conocido sólo después de comprobar que nada lo selecciona y
que no hay editores ejecutándolo. No tocar la configuración, undo, ShaDa o MINI.
