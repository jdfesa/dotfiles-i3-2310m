# Kitty setup

## Dependencies and behavior

Kitty y su integración de shell proceden de Debian; versiones comprobadas en
[Dependencies](dependencies.md). Bash sigue siendo la shell existente. La fuente
es JetBrainsMono Nerd Font Mono Regular 11, con fondo Mocha al 85%, cursor sin
animación, `repaint_delay 20` y scrollback de 5000 líneas.

La barra nativa aparece arriba incluso con una sola pestaña. Powerline distingue
la pestaña activa con el color melocotón de Mocha. La etiqueta muestra el nombre
de la carpeta activa, no la ruta completa. `cd` actualiza la etiqueta; `/`
aparece como `/`. Si Kitty no obtiene el directorio, usa el título como respaldo.

`tab.active_wd` realiza la consulta nativa al redibujar. No hay renderer propio,
script de prompt, daemon ni sondeo adicional. El control remoto permanece
deshabilitado y las confirmaciones nativas de cierre se conservan.

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
| `scripts/open-networks.sh` | `/home/jd/dotfiles-i3-2310m/scripts/open-networks.sh` | 755 |
| `scripts/open-updates.sh` | `/home/jd/dotfiles-i3-2310m/scripts/open-updates.sh` | 755 |
| `scripts/power-menu` | `/home/jd/dotfiles-i3-2310m/scripts/power-menu` | 755 |

Los archivos de configuración se enlazan al checkout y los auxiliares se
invocan directamente desde él. Aplicar el procedimiento de
[User configuration links](user-config-links.md), con revisión de diferencias,
dry-run y rollback privado; no instalar otras copias de los scripts.

Validar con el parser instalado y `sh -n`:

```sh
kitty +runpy 'from pathlib import Path; from kitty.config import load_config; bad=[]; load_config(str(Path("config/kitty.conf").resolve()), accumulate_bad_lines=bad); assert not bad, bad; print("Kitty config: OK")'
for script in open-networks.sh open-updates.sh power-menu; do
    sh -n "scripts/$script"
done
python3 tools/link-user-config.py
```

Se conserva la opacidad estática 85% instalada: `background_opacity 0.85`,
`background_blur 0` y `dynamic_background_opacity no`, con `xcompmgr -n`
al inicio de i3. El compositor es una dependencia residente existente para
mostrar el canal alfa; no se añaden efectos ni se atribuyen mejoras de CPU.
Versiones en [Dependencies](dependencies.md).

Abrir una ventana nueva con Super+Enter; las terminales existentes conservan
su estado. Para aplicar a una terminal abierta se puede usar Ctrl+Shift+F5.
Para revertir contenido, editar las fuentes mediante una rama revisada; para
revertir la migración de archivos a enlaces, usar su journal privado.

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
