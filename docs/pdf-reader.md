# PDF reader

Zathura usa Poppler para leer PDF bajo demanda. La paleta Mocha oscurece la
interfaz y las páginas, conservando el matiz cuando es posible. El recolor es
sólo visual; no altera el archivo. No hay lanzador propio, servicio, autostart,
cambios de asociaciones MIME ni vistas previas nuevas en Yazi.

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

## Usage and verification

```sh
zathura --version
cmp config/zathura/zathurarc "$HOME/.config/zathura/zathurarc"
xdg-mime query default application/pdf
zathura /path/to/document.pdf
```

El visor utiliza la entrada de escritorio del paquete, disponible en Rofi
(`Super+Space`). Verificar páginas e interfaz oscuras y comprobar que la
asociación PDF conserva el valor anterior a la instalación. `Ctrl+R` alterna
el recolor para consultar colores originales; `/` busca y `q` cierra.

Para copiar texto, seleccionarlo con el ratón y pegar con `Ctrl+V` en otra
aplicación. Para un enlace externo, pulsar `c` y confirmar el número que
muestra Zathura (sin abrir el enlace). Referencia de opciones en
[zathurarc(5)](https://manpages.debian.org/trixie/zathura/zathurarc.5.en.html)
y teclas en [zathura(1)](https://manpages.debian.org/trixie/zathura/zathura.1.en.html).

En Debian 13/Xorg se comprobó el render de páginas y barras, el cambio
entre paleta Mocha y original, y la copia de texto y de un enlace externo
con un PDF de prueba. La asociación PDF permaneció en Helium. Esta prueba
no mide rendimiento sostenido ni una restauración limpia.

## Recovery

Cerrar Zathura normalmente y restaurar el respaldo de `zathurarc`. Si no había
configuración previa, retirar sólo la copia gestionada después de comprobar que
no contiene cambios locales. No eliminar el historial ni los marcadores.

Para retirar el visor, simular `apt-get -s remove zathura zathura-pdf-poppler`
y retirar esos paquetes con sudo si el plan no afecta otros programas. No
ejecutar una limpieza global de paquetes ni restaurar asociaciones a ciegas.
