# PDF reader

Zathura con Poppler es el lector de archivos PDF predeterminado. La paleta
Mocha oscurece la interfaz y las páginas, en modo normal y a pantalla
completa. `Ctrl+R` no alterna el recolor.
El modo oscuro no modifica el PDF. Helium sigue como navegador predeterminado;
no se añaden servicios, lanzadores propios ni vistas previas en Yazi.

## Installation

Paquetes del repositorio firmado de Debian estable: [Zathura](https://packages.debian.org/trixie/zathura)
y [Poppler plugin](https://packages.debian.org/trixie/zathura-pdf-poppler).
Versiones en [Dependencies and versions](dependencies.md). La paleta procede de
la configuración MIT registrada en [Third-party notices](third-party-notices.md).

```sh
apt-get -s install --no-install-recommends zathura zathura-pdf-poppler
sudo apt-get install --no-install-recommends zathura zathura-pdf-poppler
```

Como cuenta de sesión, desde la raíz del repositorio. Si el destino ya existe,
respaldarlo en privado fuera del árbol y revisar diferencias antes de copiar.
El destino administrado es `~/.config/zathura/zathurarc`, modo 644.

```sh
install -d -m 755 "$HOME/.config/zathura"
install -m 644 config/zathura/zathurarc "$HOME/.config/zathura/zathurarc"
```

## PDF association

En la sesión gráfica, como cuenta de usuario. Guardar el lector anterior y
respaldar `~/.config/mimeapps.list` en privado si existe. Aplicar sólo la
asociación PDF, sin copiar la plantilla completa sobre preferencias locales.

```sh
xdg-mime query default application/pdf
xdg-mime default org.pwmt.zathura-pdf-poppler.desktop application/pdf
xdg-mime query default application/pdf
```

El resultado debe ser `org.pwmt.zathura-pdf-poppler.desktop`. Ese ID declara
`application/pdf`; `org.pwmt.zathura.desktop` es la entrada del lanzador.
Las asociaciones de HTML, HTTP y HTTPS no cambian.

## Usage and verification

```sh
zathura --version
cmp config/zathura/zathurarc "$HOME/.config/zathura/zathurarc"
gio mime application/pdf
gio open /path/to/document.pdf
```

Abrir un PDF con doble clic desde el gestor de archivos y verificar que se
abre en Zathura con páginas e interfaz oscuras. También se puede abrir
**Zathura** desde Rofi (`Super+Space`). `/` busca y `q` cierra.

Para copiar texto, seleccionarlo con el ratón y pegar con `Ctrl+V` en otra
aplicación. Para un enlace externo, pulsar `c` y confirmar el número que
muestra Zathura (sin abrir el enlace). Referencia de opciones en
[zathurarc(5)](https://manpages.debian.org/trixie/zathura/zathurarc.5.en.html)
y teclas en [zathura(1)](https://manpages.debian.org/trixie/zathura/zathura.1.en.html).

En Debian 13/Xorg se verificaron la apertura de un archivo local mediante
GIO, el modo oscuro con `Ctrl+R` desactivado en ambos modos y la copia de
texto y enlaces.

## Recovery

Antes de desinstalar, restaurar sólo la entrada `application/pdf` del
respaldo de `[Default Applications]`. Si antes no existía, retirar la línea
que se añadió. Comprobar el resultado con `xdg-mime query default application/pdf`;
no sustituir el archivo completo.

Cerrar Zathura normalmente y restaurar el respaldo de `zathurarc`. Si no había
configuración previa, retirar sólo la copia gestionada después de comprobar que
no contiene cambios locales. No eliminar el historial ni los marcadores.

Para retirar el visor, simular `apt-get -s remove zathura zathura-pdf-poppler`
y retirar esos paquetes con sudo si el plan no afecta otros programas. No
ejecutar una limpieza global de paquetes.
