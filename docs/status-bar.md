# Status bar

## Appearance

i3bar superior, opaca y compacta, Catppuccin Mocha; texto **JetBrainsMono Nerd Font
Mono Regular 10**, iconos de clima/métricas/brillo/audio/batería/Bluetooth/trackpad **Propo Regular 12**.
Sin blur/compositor. Sólo workspaces existentes, manteniendo
los diez accesibles por teclado. Textos en inglés, hora 24 h y temperaturas °C.

Los pictogramas Propo conservan su proporción sin comprimirse en una celda Mono.
Clima usa sol/luna/nube sólidos y conserva °C, `~` de caché y `--°C` sin datos.
Wi-Fi mantiene BGH Status Icons 12; batería conserva la lectura nativa con iconos Propo. Audio tiene
área mínima de 24 píxeles y separación posterior de 4; Wi-Fi conserva 28 y 12.
Procedencia, tamaño y hash de la única fuente añadida en
[Proportional icons](../config/fonts/README.md#proportional-icons).

| Bloque | Dato / acción |
|---|---|
| Clima | Icono de condición + temperatura; sin ciudad |
| ↑ / ↓ | Tráfico `wlp2s0` por diferencia de contadores; K=KiB/s, M=MiB/s |
| RAM / CPU | Iconos sin etiquetas, con uso de RAM según MemAvailable y uso de CPU agregado; clic en el icono CPU abre/cierra btop |
| Temperatura | Sensor CPU coretemp/x86_pkg_temp; no temperatura exterior |
| Disco | Espacio disponible de `/`; G=GiB |
| Paquetes | Candidatos APT locales; click o Super+U abre lista |
| Brillo | Sol y porcentaje del panel interno; clic alterna el deslizador |
| Audio | Icono y porcentaje/mute de la salida USB; `No audio` si falta, `Audio ?` si no se puede leer; clic/Super+A abre deslizador |
| Wi-Fi | Sólo icono por calidad, sin SSID/cifra; click/Super+N |
| Bluetooth / trackpad | Estado del adaptador y batería inalámbrica; clic en el icono del trackpad abre [Trackpad speed](bluetooth-setup.md#pointer-speed) |
| Batería | Icono de ausencia, carga, descarga, completa, reposo o estado desconocido; porcentaje válido |
| Reloj | Fecha en inglés y hora local; clic abre/cierra calendario |

Falta de audio/batería no se representa como 0%. Detección y control de salida
en [USB audio](audio-setup.md). Redes se abre con `nmtui-connect` en Kitty;
mantiene la autorización normal de NetworkManager.

## Battery icons

El bloque de batería sustituye la leyenda `No battery` por una batería con cruz,
sin porcentaje ficticio. Reutiliza i3status y la fuente Propo ya instalada.
No consulta otro lector ni añade procesos, dependencias, avisos o sondeos.

| State | Presentation |
|---|---|
| `absent` | Batería tachada gris, sin texto ni porcentaje |
| `charging` | Batería con rayo y nivel por tramos de 10 %, en verde; porcentaje |
| `discharging` | Batería con nivel por tramos de 10 %; porcentaje |
| `full` | Batería con marca de verificación verde; porcentaje informado |
| `idle` | Batería con nivel y pausa amarilla; no afirma carga activa |
| `unknown` | Batería con interrogación; conserva el porcentaje válido si existe |

Se respeta el estado del driver: 100 % no implica por sí solo `full`, y estar
conectado a CA no demuestra carga activa. i3status convierte **Not charging**
en `idle`; no se usan estados del trackpad u otras baterías HID como batería
del equipo. La configuración conserva su selección nativa `BAT*`, el tick de
10 s, `last_full_capacity` y el umbral de batería baja. En descarga, el icono
es rojo por debajo de 15 % y amarillo por debajo de 30 %; se conservan color
y urgencia nativos. Datos malformados muestran interrogación, sin inventar 0 %.

`absent` es la salida `format_down` de i3status: también puede indicar que no
dispone de lectura. En la portátil sin batería no hay dispositivo `BAT*`;
esa ausencia está comprobada. Carga, descarga, completa y reposo sólo se
validan con datos simulados hasta poder colocar la batería físicamente.

Para actualizar esta presentación, revisar y respaldar privadamente los dos
destinos del [Manifest](../config/manifest.json), fuera del checkout. Instalar
adaptador y configuración nativa juntos, tras reconciliar diferencias:

```sh
umask 022
python3 -m unittest discover -s tests -p test_battery_status.py
python3 -m unittest discover -s tests -p 'test_status*.py'
i3status -c config/i3status-config --run-once
install -m 755 scripts/status-clicks.py "$HOME/scripts/status-clicks.py"
install -m 644 config/i3status-config "$HOME/.config/i3status/config"
cmp scripts/status-clicks.py "$HOME/scripts/status-clicks.py"
cmp config/i3status-config "$HOME/.config/i3status/config"
i3-msg restart
```

Ambos archivos deben ser jd:jd, modos755/644 respectivamente. El restart
conserva ventanas. Para revertir sólo los iconos, restaurar esos dos archivos
desde su respaldo, comprobar contenidos/modos y renovar i3. No cambiar fuentes,
servicios ni estado de energía para esta presentación.

### Battery verification — 2026-11-15

- Ausencia real representada por el icono tachado en i3bar de 1366×24, sin
  leyenda ni porcentaje, sin recortes. Los 26 glifos existen en Propo; vista
  previa de carga, descarga, completa, reposo y desconocido inspeccionada.
- Siete escenarios de archivos temporales pasaron por i3status 2.15 y el
  adaptador. Se comprobaron también límites/errores del porcentaje, urgencia
  conservada y carga a 100 % distinta de estado completo. Suite general en
  [Verification status](mirror-status.md).
- Dos archivos instalados con respaldo privado, contenidos y modos755/644
  jd:jd comprobados. Ventanas conservadas al renovar i3; el anclaje de audio
  por teclado se recalcula con el nuevo ancho del bloque. Sin nuevas fuentes,
  consultas o procesos. Los estados con batería instalada siguen sin prueba física.

## Screen brightness

El sol, junto al audio, permanece visible con la barra contraída. Clic izquierdo
abre/cierra **Screen brightness** debajo del bloque. El deslizador y las flechas
izquierda/derecha aplican cambios al instante; Escape o **Close** cierra sin
revertirlos. Abrir y cerrar no cambia el nivel. El panel muestra la lectura
validada y la barra se actualiza en el próximo tick de 10 s.

Al iniciar una sesión i3 nueva, el brillo se fija en **43 %** (paso 3 de 7).
Los cambios manuales se conservan durante la sesión: el valor inicial no se
reaplica al recargar o reiniciar i3 ni al abrir el deslizador. No altera la
retroiluminación antes de iniciar i3.

En la BGH A470 usa únicamente `/sys/class/backlight/acpi_video0` de tipo
`firmware`. El porcentaje es la relación entre el paso real y el máximo del
driver; en esta portátil, los pasos seleccionables son 1 a 7. No escribe cero
y no modifica gamma, monitores externos ni iluminación de teclado. Si la
lectura no está disponible, el bloque muestra `?` y el panel no permite ajustar.
La escritura usa [logind SetBrightness](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.login1.html)
mediante Gio desde la sesión i3 local activa; no usa sudo, reglas propias ni
permisos adicionales. Reutiliza Python y GTK3 de Debian y systemd/logind ya
instalados (versiones en [Dependencies](dependencies.md)), sin nuevos servicios
ni sondeos. La barra sólo lee sysfs, sin abrir conexiones D-Bus de brillo.

### Brightness installation and recovery

Comprobar el dispositivo en la portátil y revisar el [manifest.json](../config/manifest.json).
Como `jd`, respaldar los destinos existentes de `status-clicks.py`,
`status-panel.py`, `~/.config/calendar/calendar.css` y `~/.config/i3/config` en
un directorio privado externo (modo 700). Registrar si el nuevo auxiliar no
existe; si existe, revisar y respaldarlo también. Desde la raíz, con las
dependencias del adaptador y [Status panels](status-panels.md) ya instaladas:

```sh
umask 022
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_screen_brightness.py
install -m 755 scripts/screen-brightness.py scripts/status-panel.py scripts/status-clicks.py "$HOME/scripts/"
install -m 644 config/calendar/calendar.css "$HOME/.config/calendar/calendar.css"
```

Añadir la regla `BGH-Screen-Brightness`/`bgh-screen-brightness` y el
`exec` de `screen-brightness.py --set-percent 43` de `config/i3-config`
al archivo activo, conservando sus diferencias locales. En
una instalación limpia, instalar la fuente completa en modo 644. Comprobar
`i3 -C -c "$HOME/.config/i3/config"` y comparar contenidos, modos y propietario
con el manifiesto. Ejecutar `i3-msg restart` en la sesión vigente para renovar
el adaptador conservando las ventanas. Comprobar el sol, el anclaje, un paso en
cada dirección y el segundo clic; devolver el brillo a su valor anterior.
Para comprobar el valor inicial sin salir de la sesión, ejecutar desde ella
`~/scripts/screen-brightness.py --set-percent 43` y verificar que el indicador
muestra 43 % en el próximo tick.

Para revertir, cerrar el panel, restaurar sólo los destinos respaldados y retirar
el nuevo auxiliar si no existía. Validar i3 y renovar de la misma forma; no hay
paquetes que retirar ni permisos que deshacer.

## Collapsible metrics

La barra inicia contraída. El chevrón antes del contador de paquetes alterna
con un clic izquierdo: `›` expande y `‹` contrae tráfico, RAM, CPU, temperatura
y disco. Clima, paquetes, brillo, audio, Wi-Fi, Bluetooth, trackpad, batería y reloj permanecen visibles.
Un bloque marcado por el productor con `urgent: true` también permanece visible.

El estado vive sólo en memoria y vuelve a contraído cuando se reinicia el
adaptador. El clic redibuja la última muestra sin ejecutar comandos, consultar
sensores ni releer contadores. Las métricas siguen actualizándose cada 10 s
estando ocultas, conservando el intervalo de las tasas de tráfico. No añade
dependencias, procesos residentes, timers ni archivos de estado. La contracción
reduce ocupación visual; no demuestra menor uso de CPU.

## On-demand panels

Clic izquierdo en el reloj alterna el calendario; en CPU, btop. Expandir las
métricas con el chevrón para acceder a CPU. Cada panel tiene identidad propia
y se coloca bajo el bloque pulsado, limitado a la pantalla. Apertura/cierre
por eventos, sin cambiar el tick de 10 s ni SIGSTOP/SIGCONT.
Dependencias, operación, muestra de recursos y recuperación en
[Status panels](status-panels.md).

## Scheduled work and events

1. `status-bar.sh` selecciona sensor al iniciar y ejecuta i3status.
2. i3status obtiene datos cada **10 s**, sin shell por indicador.
3. `status-clicks.py` es un adaptador Python **residente**. Espera eventos con
   selectores, formatea indicadores y lee dos contadores sysfs de tráfico en el
   tick existente; no consulta Internet ni nmcli cada tick. Bluetooth consulta
   una propiedad D-Bus por controlador en ese mismo tick; el lector HID fijado
   sólo se ejecuta brevemente al conectar y cada 5 min, sin servicio/timer propio.
   Audio verifica el USB y lee su mixer con libasound en ese tick de 10 s,
   sin procesos hijos ni consulta a una tarjeta ausente.
4. Los clicks sólo abren helpers fijos; no interpolan SSID o datos arbitrarios
   como comandos.
5. La conexión/desconexión de audio se refleja en el próximo tick, sin reiniciar
   la barra ni generar una variante temporal de i3status.

## Caches

- Clima: Open-Meteo HTTPS, centro público configurable de Orán en
  `config/weather.json`, sin geolocalización. Timer **30 min** con desfase;
  timeout de petición 20 s y servicio 30 s, validación y escritura atómica.
  Cache fallida de hasta 3 h se marca `~`; vencida/ausente, `--°C`.
- Paquetes: cada **6 h**, `LC_ALL=C apt-get --simulate upgrade` sobre índices
  existentes. No apt update, descargas, instalaciones ni sudo. Fallo: `?`.
  `0` sólo significa cero candidatos en los índices disponibles.
- Ambos refrescos son oneshot `Nice=10`, `NoNewPrivileges=yes`, umask 0077.
  No son clientes Python residentes.

Después de actualizar manualmente los índices:

```sh
systemctl --user start packages-refresh.service
```

La lista Super+U también es de sólo lectura. Fuentes y ciclo de vida:
[scripts/README.md](../scripts/README.md).

## Installation and recovery

Usa i3bar/i3status, Python 3 estándar, `libsystemd0` y `libasound2t64`; procedencia y versiones en
[Dependencies](dependencies.md). En una instalación nueva, instalar primero las
fuentes Mono, BGH y sus licencias según [Fonts](apps-setup.md#fonts).
El TTF Propo es un archivo regular en [manifest.json](../config/manifest.json), sin enlaces.
Instalar antes el módulo, lector/licencia, regla limitada y auxiliar de velocidad de
[Bluetooth and Magic Trackpad 2](bluetooth-setup.md#indicator-installation-and-recovery);
el adaptador actualizado los necesita. Esa guía cubre también su recuperación.
Instalar también el módulo/perfil y panel de [USB audio](audio-setup.md#installation)
y el auxiliar de [Screen brightness](#brightness-installation-and-recovery)
antes de renovar el adaptador.
Desde la raíz, como `jd`, respaldar los archivos afectados fuera del repositorio:

```sh
umask 022
mkdir -p "$HOME/.local/state/bgh-config-backups"
backup=$(mktemp -d "$HOME/.local/state/bgh-config-backups/bar-XXXXXXXX")
(umask 077
 cp -- "$HOME/scripts/status-clicks.py" "$backup/status-clicks.py"
 cp -- "$HOME/.config/i3/keybindings-help.txt" "$backup/keybindings-help.txt"
 if [ -e "$HOME/.local/share/fonts/jetbrains-mono-nerd-font-propo-regular.ttf" ]; then
     cp -- "$HOME/.local/share/fonts/jetbrains-mono-nerd-font-propo-regular.ttf" "$backup/propo.ttf"
 fi)
```

Con el respaldo comprobado, validar e instalar las fuentes. Conservar las
diferencias de `~/.config/i3/config` al añadir las reglas de paneles; no
reemplazar toda la configuración activa para modificar la barra.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_status*.py' -q
i3 -C -c "$HOME/.config/i3/config"
install -m 755 scripts/status-clicks.py "$HOME/scripts/status-clicks.py"
install -m 644 config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
install -m 644 config/fonts/jetbrains-mono-nerd-font-propo-regular.ttf "$HOME/.local/share/fonts/"
fc-cache "$HOME/.local/share/fonts"
fc-match 'JetBrainsMono Nerd Font Propo'
cmp scripts/status-clicks.py "$HOME/scripts/status-clicks.py"
cmp config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
cmp config/fonts/jetbrains-mono-nerd-font-propo-regular.ttf "$HOME/.local/share/fonts/jetbrains-mono-nerd-font-propo-regular.ttf"
stat -c '%a %U:%G %n' "$HOME/scripts/status-clicks.py" "$HOME/.config/i3/keybindings-help.txt" \
  "$HOME/.local/share/fonts/jetbrains-mono-nerd-font-propo-regular.ttf"
i3-msg restart
```

Esperado: `jd:jd`, adaptador 755, ayuda y TTF 644; fontconfig debe resolver
Propo al TTF instalado. El restart de i3 renueva el adaptador y
conserva las ventanas. Comprobar ambos estados con el chevrón y la ayuda con
Super+K. Un reload puede conservar el proceso anterior.

Para revertir, seleccionar el respaldo privado revisado e instalar el adaptador
y la ayuda con sus modos anteriores. Restaurar `propo.ttf` al destino si existía;
si antes estaba ausente, retirar sólo el TTF añadido después de restaurar el
adaptador. Ejecutar `fc-cache "$HOME/.local/share/fonts"` e `i3-msg restart`.
La recuperación no requiere cerrar la sesión ni restaurar otros archivos.

## Verification

Comprobado en la portátil el 2026-11-15: expansión y contracción mediante
eventos de clic X11 en i3bar, renderizado de ambos estados y conservación de las
ventanas al reiniciar i3. Tres ciclos de ocultar/mostrar la barra pausaron y
reanudaron los mismos tres procesos del grupo productor. La barra quedó visible
y contraída. Propo resuelve al TTF instalado y cubre todos los pictogramas usados;
ambos estados se renderizan sin recortes en la franja de 1366 × 24 píxeles.
Contenido, propietario y modos de adaptador, ayuda y TTF contrastados.
Validaciones `i3 -C` y `sh -n` correctas; suite completa y estado de destinos
en [Verification status](mirror-status.md).

Las pruebas de estado cubren datos esenciales/ausentes, urgencia explícita,
muestreo sólo por tick, clics inválidos y redibujo inmediato con el productor
inactivo, incluso después de SIGSTOP/SIGCONT. No equivalen a una restauración
limpia ni a una medida de consumo sostenido.

## Troubleshooting

- Muestra acotada: `~/scripts/status-clicks.py --run-once`.
- Error tras fullscreen: conservar SIGSTOP/SIGCONT del protocolo; i3bar señaliza
  todo el grupo. No anunciar USR1/USR2 ni desactivar la pausa con stop_signal=0.
- Si un reload conserva el adaptador antiguo, `i3-msg restart` renueva i3bar
  manteniendo ventanas.
- Cajas en lugar de iconos: `fc-match`, `fc-cache ~/.local/share/fonts` y renovar
  i3bar; no instalar colecciones de fuentes adicionales como primer paso.
- `tools/capture-bar.py` captura sólo la franja superior; imágenes/logs fuera
  del repositorio.
- Pruebas: `tests/test_status_lifecycle.py` cubre el grupo shell/adaptador/backend.
  También pasaron ciclos con i3status nativo y fullscreen gráfico.

Muestras cortas de CPU/RSS no constituyen un benchmark ni justifican prometer
un consumo fijo. Mantener los intervalos y medir tareas representativas.

Referencias: [i3status](https://i3wm.org/docs/i3status.html),
[protocolo i3bar](https://i3wm.org/docs/i3bar-protocol.html),
[Open-Meteo](https://open-meteo.com/en/docs).
