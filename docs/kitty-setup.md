# Kitty setup

## Dependencies and behavior

Kitty y su integración de shell proceden de Debian; versiones comprobadas en
[Dependencies](dependencies.md). Bash sigue siendo la shell existente. La fuente
es JetBrainsMono Nerd Font Mono Regular 11, con fondo Mocha, cursor sin
animación, `repaint_delay 20` y scrollback de 5000 líneas.

La barra nativa aparece arriba incluso con una sola pestaña. Powerline distingue
la pestaña activa con el color melocotón de Mocha. La etiqueta muestra el nombre
de la carpeta activa, no la ruta completa. `cd` actualiza la etiqueta; `/`
aparece como `/`. Si Kitty no obtiene el directorio, usa el título como respaldo.

`tab.active_wd` realiza la consulta nativa al redibujar. No hay renderer propio,
script de prompt, daemon ni sondeo adicional. El control remoto permanece
deshabilitado y las confirmaciones nativas de cierre se conservan.

## Background opacity

Todas las instancias, incluidos los auxiliares que abren Kitty, cargan
`background_opacity 0.85`: 85 % de opacidad para las celdas con el color de
fondo de la terminal. El texto no se atenúa; aplicaciones que pintan su propio
fondo pueden seguir opacas. No se activa opacidad dinámica ni desenfoque.

Xorg necesita un compositor para ese canal alfa. i3 ejecuta una sola vez
`/usr/bin/xcompmgr -n` al iniciar la sesión. Es un proceso de usuario con
composición XRender básica, sin sombras, desenfoque, shaders ni animaciones.
i3bar y las decoraciones permanecen opacas. El compositor procesa el
escritorio; una opacidad cercana a 1 no elimina el coste de composición.
Queda por verificar la respuesta con el flujo habitual y vídeo en Helium.

```sh
sudo apt-get install --no-install-recommends xcompmgr
```

Antes de instalar las fuentes existentes de Kitty e i3, respaldar
`~/.config/kitty/kitty.conf` y `~/.config/i3/config` fuera del repositorio.
Conservar las diferencias locales al añadir la línea de arranque de
`config/i3-config`. Validar con el parser de Kitty y
`i3 -C -c "$HOME/.config/i3/config"`. En la sesión abierta, recargar i3 y,
sólo si no hay otro compositor, iniciarlo una vez sin cerrar aplicaciones:

```sh
i3-msg reload
i3-msg 'exec --no-startup-id /usr/bin/xcompmgr -n'
```

Abrir Kitty normalmente con Super+Enter. Las ventanas que se crearon
opacas deben volver a abrirse; la recarga de Kitty no cambia su canal alfa.
No cerrarlas hasta guardar el trabajo o terminar los comandos en ejecución.

Para revertir, restaurar los dos archivos respaldados o volver a
`background_opacity 1.0` y retirar el `exec` de xcompmgr. Validar y recargar
i3. Identificar con `pgrep -a -u "$(id -u)" -x xcompmgr` el proceso de esta
sesión que se inició con `/usr/bin/xcompmgr -n` y enviar `kill -TERM` sólo a
ese PID. Las ventanas nuevas volverán a abrirse opacas. Si ya no se usa el
paquete, revisar primero `apt-get -s remove xcompmgr`.

## Shortcuts

| Atajo | Acción |
|---|---|
| Ctrl+Shift+T | Abrir pestaña en la carpeta de la ventana activa |
| Ctrl+Shift+Q | Cerrar pestaña activa; la última cierra esa ventana de Kitty |
| Ctrl+Shift+Izquierda / Derecha | Pestaña anterior / siguiente |

Las confirmaciones de Kitty pueden intervenir si hay un comando ejecutándose.
La ayuda visible con Super+K incluye estos atajos; referencia común en
[Keyboard shortcuts](keybindings.md).

Las ventanas auxiliares Wi-Fi, APT y energía reciben
`--override=tab_bar_min_tabs=2`: con una sola pestaña mantienen su presentación
compacta. El parámetro sólo cambia la visibilidad de la barra de esa ventana.
El [volumen USB](audio-setup.md) utiliza un panel GTK3 independiente de Kitty.

## Installation and recovery

Fuentes y destinos existentes de [manifest.json](../config/manifest.json):

| Fuente | Destino | Modo |
|---|---|---|
| `config/kitty.conf` | `/home/jd/.config/kitty/kitty.conf` | 644 |
| `config/keybindings-help.txt` | `/home/jd/.config/i3/keybindings-help.txt` | 644 |
| `scripts/open-networks.sh` | `/home/jd/scripts/open-networks.sh` | 755 |
| `scripts/open-updates.sh` | `/home/jd/scripts/open-updates.sh` | 755 |
| `scripts/power-menu` | `/home/jd/scripts/power-menu` | 755 |

Desde la raíz, como `jd`, revisar las diferencias con cada destino antes de
actualizarlo y conservar ajustes locales. Respaldar la lista acotada fuera del
repositorio:

```sh
umask 022
mkdir -p "$HOME/.local/state/bgh-config-backups"
backup=$(mktemp -d "$HOME/.local/state/bgh-config-backups/kitty-XXXXXXXX")
install -m 600 "$HOME/.config/kitty/kitty.conf" "$backup/kitty.conf"
install -m 600 "$HOME/.config/i3/keybindings-help.txt" "$backup/keybindings-help.txt"
for script in open-networks.sh open-updates.sh power-menu; do
    install -m 600 "$HOME/scripts/$script" "$backup/$script"
done
```

Validar con el parser instalado y `sh -n`:

```sh
kitty +runpy 'from pathlib import Path; from kitty.config import load_config; bad=[]; load_config(str(Path("config/kitty.conf").resolve()), accumulate_bad_lines=bad); assert not bad, bad; print("Kitty config: OK")'
for script in open-networks.sh open-updates.sh power-menu; do
    sh -n "scripts/$script"
done
```

Con el respaldo y las diferencias revisados, instalar las fuentes como archivos
regulares. Si un auxiliar conserva cambios locales, aplicar sólo el override
de Kitty a su invocación existente en vez de reemplazarlo completo.

```sh
install -m 644 config/kitty.conf "$HOME/.config/kitty/kitty.conf"
install -m 644 config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
for script in open-networks.sh open-updates.sh power-menu; do
    install -m 755 "scripts/$script" "$HOME/scripts/$script"
done
cmp config/kitty.conf "$HOME/.config/kitty/kitty.conf"
cmp config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
stat -c '%a %U:%G %n' "$HOME/.config/kitty/kitty.conf" "$HOME/scripts/open-networks.sh"
```

Esperado: propietario `jd:jd`, configuración/ayuda 644 y auxiliares 755.
Abrir una ventana nueva con Super+Enter; las terminales existentes conservan
su estado. Ctrl+Shift+F5 recarga opciones compatibles, no el canal alfa
descrito en [Background opacity](#background-opacity).

Para revertir, seleccionar el respaldo privado revisado, instalar `kitty.conf`
y la ayuda con modo 644, y los cuatro auxiliares con modo 755 en sus destinos.
Abrir otra ventana o recargar Kitty con Ctrl+Shift+F5. No restaurar carpetas
completas de configuración ni la shell para revertir estos seis archivos.

## Verification

Comprobar una ventana nueva en el directorio de trabajo, ejecutar `cd` hacia
otra carpeta y verificar la etiqueta. Abrir una pestaña con Ctrl+Shift+T y
comprobar `pwd`; alternar con las flechas y cerrar una con Ctrl+Shift+Q.
La otra pestaña debe permanecer abierta. Con una sola pestaña, la etiqueta
continúa visible.

Las comprobaciones acotadas usan carpetas sintéticas y una instancia aislada:
parser real, bindings efectivos y acciones nativas de crear, alternar y cerrar.
Se contrastan directorios con espacios, raíz y fallback del título. Los paneles
se validan sin ejecutar operaciones reales de red, audio o energía.

Verificado el 2026-11-15 en la portátil: etiquetas tras `cd`, herencia de carpeta
con espacios, navegación, cierre de la pestaña seleccionada y de la última
pestaña de prueba; las ventanas preexistentes se conservaron. Revisados contenidos,
modos y propietarios de los seis destinos, preservando diferencias locales previas.

## References

- [Kitty tab bar](https://sw.kovidgoyal.net/kitty/conf/#tab-bar).
- [Kitty tab actions](https://sw.kovidgoyal.net/kitty/actions/#tab-management).
- [Kitty shell integration](https://sw.kovidgoyal.net/kitty/shell-integration/).
- [Kitty background opacity](https://sw.kovidgoyal.net/kitty/conf/#opt-kitty.background_opacity).
- [xcompmgr manual](https://manpages.debian.org/trixie/xcompmgr/xcompmgr.1.en.html).
