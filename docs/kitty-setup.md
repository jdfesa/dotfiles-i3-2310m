# Kitty setup

## Dependencies and behavior

Kitty y su integración de shell proceden de Debian; versiones comprobadas en
[Dependencies](dependencies.md). Las nuevas terminales usan Zsh y Starship,
como se describe en [Interactive shell](#interactive-shell). La fuente es
JetBrainsMono Nerd Font Mono Regular 11, con fondo Mocha, cursor sin
animación, `repaint_delay 20` y scrollback de 5000 líneas.

La barra nativa aparece arriba incluso con una sola pestaña. Powerline distingue
la pestaña activa con el color melocotón de Mocha. La etiqueta muestra el nombre
de la carpeta activa, no la ruta completa. `cd` actualiza la etiqueta; `/`
aparece como `/`. Si Kitty no obtiene el directorio, usa el título como respaldo.

`tab.active_wd` realiza la consulta nativa al redibujar. No hay renderer
propio ni sondeo de pestañas. El control remoto permanece deshabilitado y las
confirmaciones nativas de cierre se conservan.

## Interactive shell

Kitty inicia `/usr/bin/zsh` en nuevas ventanas y pestañas sin un comando
explícito. Bash permanece como shell de la cuenta para tty1 y SSH; no se
cambian `.profile`, `.bashrc` ni los intérpretes de los scripts. Los procesos
de las terminales abiertas conservan su shell.

Instalar sin recomendaciones desde Debian estable:

```sh
sudo apt-get install --no-install-recommends zsh starship
```

El perfil [Starship](https://starship.rs/config/) conserva sin cambios
[starship.toml de mydotfiles](https://github.com/jdfesa/mydotfiles/blob/e904679e51d70d0f12b5318e680919b096df3850/shared/starship/starship.toml).
Usa Catppuccin Mocha y los glifos de la fuente ya instalada. Zsh muestra el
prompt derecho cuando hay módulos activos; no se añade un framework. El
perfil incluye dos comandos Git locales y módulos contextuales. El coste
con la carga habitual sigue por medir.

Instalar los paquetes antes de desplegar el cambio de Kitty, comprobar
`zsh -n config/zsh/zshrc` y crear los enlaces de esta guía con el procedimiento
de [User configuration links](user-config-links.md). Zsh inicia Starship sólo si
su binario está presente. El historial `~/.zsh_history` es privado, separado
del historial de Bash y no se restaura desde Git.

Abrir una ventana con Super+Enter y comprobar
`printf '%s\n' "$ZSH_VERSION" "$STARSHIP_SHELL"`. Abrir un directorio Git para
comprobar la rama y un proyecto con módulos activos para el lado derecho.
Para abrir Bash sin cambiar el predeterminado, usar `kitty /bin/bash`.
Para revertir, retirar `shell /usr/bin/zsh` de la fuente de Kitty mediante
una rama revisada, revertir sólo los enlaces de esta instalación con su
journal y abrir una ventana nueva. Conservar el historial privado.

## Background opacity

Kitty usa `background_opacity 0.85` en todas las instancias, incluidas las
ventanas auxiliares. Sólo se atenúan las celdas con el color de fondo de la
terminal; el texto no cambia y las aplicaciones que pintan su propio fondo
pueden seguir opacas. El desenfoque y la opacidad dinámica están deshabilitados.

El canal alfa en Xorg requiere un compositor. Instalar `xcompmgr` desde Debian
estable (véase [Dependencies](dependencies.md)):

```sh
sudo apt-get install --no-install-recommends xcompmgr
```

i3 ejecuta una vez `/usr/bin/xcompmgr -n` al iniciar la sesión. Usa composición
XRender básica sin sombras, desenfoque, shaders ni animaciones. i3bar y las
decoraciones se mantienen opacas. Si hace falta aplicar esta configuración
durante una sesión abierta, validar primero con `i3 -C -c "$HOME/.config/i3/config"`
y recargar i3. Iniciar el compositor desde la sesión local sólo si no hay otro
compositor activo, con `i3-msg 'exec --no-startup-id /usr/bin/xcompmgr -n'`.

Abrir Kitty normalmente con Super+Enter. Ctrl+Shift+F5 puede recargar otras
opciones, pero no el canal alfa de una ventana existente. Volver a abrir
sólo las ventanas que deban cambiar, tras guardar su trabajo.

Para revertir la opacidad, preparar una rama revisada que vuelva a
`background_opacity 1.0` y retire el arranque de xcompmgr en i3. Validar las
fuentes enlazadas y recargar i3. Si el compositor sigue activo en la sesión,
identificar el proceso de usuario de esa pantalla iniciado con
`/usr/bin/xcompmgr -n` y enviar `kill -TERM` sólo a ese PID.

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
| `config/zsh/zshrc` | `/home/jd/.zshrc` | 644 |
| `config/starship/starship.toml` | `/home/jd/.config/starship.toml` | 644 |
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

Para revertir la migración de archivos a enlaces, usar su journal privado.
La operación y recuperación del compositor se describen por separado en
[Background opacity](#background-opacity).

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
