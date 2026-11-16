# Status panels

La configuración pública de usuario se enlaza siguiendo
[User configuration links](user-config-links.md); sus comandos distinguen
el dry-run del despliegue con respaldo. No instalar copias paralelas de scripts.

## Operation

- Clic izquierdo en el reloj: abrir/cerrar calendario GTK3. Flechas del widget
  o PgUp/PgDn cambian de mes; Today/Home vuelve a hoy; Close/Escape cierra.
- Clic izquierdo en CPU: abrir/cerrar btop en una ventana Kitty identificada.
  Expandir primero las métricas con el chevrón. `q` cierra el monitor.
- Clic izquierdo en el bloque del trackpad: alternar el panel GTK3
  [Trackpad speed](bluetooth-setup.md#pointer-speed). Comparte el tema del
  calendario; Enter aplica y cierra, Escape cierra sin aplicar.
- Clic izquierdo en audio o Super+A: alternar el deslizador de
  [USB audio](audio-setup.md). Flechas/ratón aplican volumen inmediatamente;
  Mute cambia sólo el silencio de salida; Escape cierra.
- Clic izquierdo en el sol: alternar el deslizador de
  [Screen brightness](status-bar.md#screen-brightness).

Cada clic alterna sólo el panel correspondiente. Un lock independiente descarta
activaciones simultáneas mientras abre/cierra. Las ventanas se colocan bajo el
bloque pulsado y se limitan al monitor; sin coordenadas válidas se centran,
salvo audio: Super+A calcula su bloque actual y siempre lo coloca debajo.
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
Fuentes de usuario enlazadas al checkout o ejecutadas directamente desde él:

| Fuente | Destino | Modo |
|---|---|---|
| `scripts/status-panel.py` | `/home/jd/dotfiles-i3-2310m/scripts/status-panel.py` | 755 |
| `scripts/calendar-popup.py` | `/home/jd/dotfiles-i3-2310m/scripts/calendar-popup.py` | 755 |
| `scripts/open-trackpad-speed.py` | `/home/jd/dotfiles-i3-2310m/scripts/open-trackpad-speed.py` | 755 |
| `config/calendar/calendar.css` | `/home/jd/.config/calendar/calendar.css` | 644 |

Aplicar [User configuration links](user-config-links.md), con respaldo privado,
dry-run y revisión de diferencias. Las reglas de identidad permanecen en la
fuente i3 enlazada; no mantener otra copia editable para los paneles.
Antes de renovar el adaptador, disponer también de los módulos y perfiles de
[USB audio installation](audio-setup.md#installation) y
[Brightness installation and recovery](status-bar.md#brightness-installation-and-recovery).

```sh
i3 -C -c "$HOME/.config/i3/config"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_status*.py' -q
python3 tools/verify-mirror.py --remote --check
i3-msg restart
```

El restart conserva las ventanas y renueva el adaptador. Comprobar apertura y
segundo clic de cierre, sin duplicados ni monitor residente después de cerrar.
También se pueden ejecutar `scripts/status-panel.py calendar` y
`scripts/status-panel.py resources` desde el checkout.

Para revertir enlaces, usar el journal de la migración. Para revertir el
comportamiento, modificar las fuentes mediante Git y renovar sólo lo necesario.
Mantener las preferencias privadas de btop y los paquetes compartidos.

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
