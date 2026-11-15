# Status panels

## Operation

- Clic izquierdo en el reloj: abrir/cerrar calendario GTK3. Flechas del widget
  o PgUp/PgDn cambian de mes; Today/Home vuelve a hoy; Close/Escape cierra.
- Clic izquierdo en CPU: abrir/cerrar btop en una ventana Kitty identificada.
  Expandir primero las métricas con el chevrón. `q` cierra el monitor.
- Clic izquierdo en el bloque del trackpad: alternar el panel GTK3
  [Trackpad speed](bluetooth-setup.md#pointer-speed). Comparte el tema del
  calendario; Enter aplica y cierra, Escape cierra sin aplicar.

Cada clic alterna sólo el panel correspondiente. Un lock independiente descarta
activaciones simultáneas mientras abre/cierra. Las ventanas se colocan bajo el
bloque pulsado y se limitan al monitor; sin coordenadas válidas se centran.
El calendario es de sólo lectura: no agenda eventos ni consulta servicios.

`status-panel.py` consulta i3 y espera eventos de ventana con un plazo total de
4 s; termina tras abrir, colocar o cerrar. Usa clase e instancia exactas y cierra
por ID numérico, no por títulos o patrones de procesos. Una falla de IPC no
lanza otra ventana como fallback. No añade daemon ni polling al tick de 10 s.

btop refresca cada 2000 ms mientras está abierto. Su ventana exclusiva omite
barra de pestañas y confirmación de cierre; esa excepción sólo afecta al monitor.
Las preferencias y confirmaciones de las terminales normales se conservan.

## Dependencies

Versiones/procedencia en [Dependencies](dependencies.md). Se reutilizan Kitty,
btop y la biblioteca GTK3 de Debian; el calendario necesita sus bindings:

```sh
sudo apt-get install --no-install-recommends btop python3-gi gir1.2-gtk-3.0
```

No hay servicios de inicio nuevos. GTK3 vive mientras está abierto su panel;
Kitty/btop viven mientras está abierto el monitor. La cache/configuración privada
de btop permanece fuera del repositorio.

## Installation and recovery

[manifest.json](../config/manifest.json) declara las fuentes y destinos.
Fuentes nuevas, como archivos regulares propiedad de `jd`:

| Fuente | Destino | Modo |
|---|---|---|
| `scripts/status-panel.py` | `/home/jd/scripts/status-panel.py` | 755 |
| `scripts/calendar-popup.py` | `/home/jd/scripts/calendar-popup.py` | 755 |
| `scripts/open-trackpad-speed.py` | `/home/jd/scripts/open-trackpad-speed.py` | 755 |
| `config/calendar/calendar.css` | `/home/jd/.config/calendar/calendar.css` | 644 |

También cambian `config/i3-config`, `scripts/status-clicks.py`,
`config/keybindings-help.txt` y `scripts/README.md`, con sus destinos existentes.
Antes de actualizar, respaldarlos en un directorio privado externo con modo 700,
anotar contenidos/modos y marcar los destinos que todavía no existen. Revisar
las diferencias locales y conservarlas; no sustituir toda la configuración i3
para añadir reglas de ventanas.

Desde la raíz, como `jd`, tras comprobar el respaldo:

```sh
umask 022
install -d "$HOME/scripts" "$HOME/.config/i3" "$HOME/.config/calendar"
install -m 755 scripts/status-panel.py scripts/calendar-popup.py scripts/open-trackpad-speed.py "$HOME/scripts/"
install -m 644 config/calendar/calendar.css "$HOME/.config/calendar/calendar.css"
install -m 755 scripts/status-clicks.py "$HOME/scripts/status-clicks.py"
install -m 644 config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
```

Aplicar las reglas `BGH-Calendar`/`bgh-calendar`, `BGH-Resources`/`bgh-resources`
y `BGH-Trackpad-Speed`/`bgh-trackpad-speed` de `config/i3-config` al destino activo.
En una restauración limpia se instalan esas fuentes completas con
modo 644. Validar antes de renovar i3bar:

```sh
i3 -C -c "$HOME/.config/i3/config"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_status*.py' -q
cmp scripts/status-panel.py "$HOME/scripts/status-panel.py"
cmp scripts/calendar-popup.py "$HOME/scripts/calendar-popup.py"
cmp config/calendar/calendar.css "$HOME/.config/calendar/calendar.css"
stat -c '%a %U:%G %n' "$HOME/scripts/status-panel.py" "$HOME/scripts/calendar-popup.py" \
  "$HOME/.config/calendar/calendar.css"
i3-msg restart
```

Esperado: `jd:jd`, auxiliares 755 y CSS 644. El restart conserva las ventanas.
Comprobar apertura y segundo clic de cierre, sin ventanas duplicadas ni procesos
del monitor después de cerrar. También se pueden ejecutar manualmente
`~/scripts/status-panel.py calendar` y `~/scripts/status-panel.py resources`.

Para revertir, cerrar sólo estos paneles, restaurar desde el respaldo los
archivos que existían y retirar únicamente los auxiliares/CSS antes ausentes.
Validar i3 y ejecutar `i3-msg restart`. Mantener las preferencias privadas de btop;
no eliminar paquetes compartidos como parte del rollback de archivos.

## Verification and cost

Comprobado en la portátil el 2026-11-15: tres ciclos de abrir/cerrar cada panel,
identidades reales y posición dentro de 1366 × 768. El calendario mide 360 × 427
píxeles y el monitor 960 × 560; su altura depende de la fuente y las decoraciones.
Verificados CSS y callbacks GTK de mes siguiente, Home y Escape. Las pruebas
cubren identidades, coordenadas negativas, límites de pantalla, IPC fragmentado,
fallos de conexión, locks y conservación de ventanas ajenas.

El panel de velocidad comparte el fondo y ancho de 360 píxeles del calendario.
Se verificaron su anclaje justo bajo la barra, el segundo clic sin cambios y
la selección con flechas y Enter, con lectura XInput y restauración posterior.

Muestra acotada de btop solo, sin contar Kitty: 10 s, 0,50 % de una CPU lógica
y RSS de 5,92 MiB, con actualización de 2 s y la carga existente. No es una
comparación de terminales ni un benchmark de uso sostenido. La restauración
limpia continúa como validación independiente.

## References

- [i3 IPC](https://i3wm.org/docs/ipc.html).
- [i3bar click events](https://i3wm.org/docs/i3bar-protocol.html#click_events).
- [GTK3 Calendar](https://docs.gtk.org/gtk3/class.Calendar.html).
- [btop](https://github.com/aristocratos/btop).
