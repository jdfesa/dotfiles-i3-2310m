# USB audio

## Volume control

La barra muestra el icono y porcentaje de la salida USB. Clic izquierdo o
Super+A abre/cierra **USB audio volume**, siempre bajo su bloque en la barra,
también al usar el teclado. Arrastrar el deslizador o usar las
flechas aplica inmediatamente de 0 a 100 %; **Mute** controla el silencio.
Escape o **Close** cierra sin deshacer cambios. Abrir el panel o conectar el
adaptador no cambia volumen ni mute. Subir desde cero no desmutea automáticamente.

La barra actualiza conexión, volumen y mute en su tick existente de 10 s.
`No audio` indica que falta el adaptador del perfil; `Audio ?` indica error,
control ausente o varios adaptadores iguales. El panel conserva el dispositivo
abierto: si cambia la tarjeta, bloquea escrituras; cerrar y reabrir para volver
a detectarla. Los cambios externos se reflejan al reabrir el panel y en el
próximo tick de la barra.

## Hardware and dependencies

El adaptador comprobado se enumera como **USB PnP Sound Device**, VID/PID
reportados `8086:0808`, driver nativo `snd-usb-audio`. Su control de salida es
`Speaker`, índice0; no tiene `Master`. El perfil público
[`usb-audio.json`](../config/audio/usb-audio.json) contiene sólo esos datos,
sin número de serie, puerto USB ni índice de tarjeta persistente. Las tarjetas
pueden cambiar de número al reconectar.
La selección no fija puerto, ruta USB ni hub: sirve al mover el adaptador
entre puertos compatibles. Si se mueve con el panel abierto, cerrarlo y
reabrirlo para enlazar el nuevo dispositivo, sin reutilizar el descriptor anterior.

`audio-control.py` identifica USB/driver en sysfs, abre su control ALSA y
revalida ruta/inodo antes de cada escritura. Un descriptor abierto permanece
ligado al dispositivo original; no se reasigna al nuevo ocupante de card0.
El deslizador enlaza los canales de salida; si tienen valores distintos,
el indicador usa el mayor. El porcentaje es lineal respecto al rango ALSA,
no una medida de potencia ni de volumen percibido. No se modifican `Mic`,
captura, monitorización del micrófono ni **Auto Gain Control**.

Se reutilizan Python estándar, `libasound2t64`, GTK3 y sus bindings de Debian.
`alsa-utils` aporta diagnóstico; versiones en [Dependencies](dependencies.md).
No se añaden paquetes en la portátil, servidores de audio, procesos por muestra,
daemons o timers. Cada tick abre/lee/cierra el mixer; el panel mantiene sólo
su descriptor mientras está abierto. El panel no sondea ni reproduce sonidos.

Para Super+A, el adaptador conserva el tramo de audio de la última muestra
visible en una propiedad del servidor X11, sin escribir archivos ni historiales.
Sólo publica si cambia ese tramo; el chevrón no vuelve a consultar datos.
Al abrir, el auxiliar mide texto con Pango y la fuente/DPI actuales de i3bar,
busca la barra de la pantalla enfocada y aplica el mismo anclaje que un clic.
Pango se carga sólo en ese auxiliar breve, no en el productor residente. Si no
hay barra/muestra disponible, no abre el panel en otra posición.

Para otro adaptador, verificar primero su VID/PID, driver y control de salida
de reproducción; actualizar el perfil y reiniciar el adaptador de la barra.
No elegir por el número de tarjeta ni usar un control de micrófono como salida.

## Installation

Desde la raíz, como `jd`, revisar los destinos y respaldarlos privadamente fuera
del checkout, registrando los ausentes. Reconciliar diferencias locales antes
de instalar. Fuentes, destinos completos y modos en el
[Manifest](../config/manifest.json). En una instalación nueva, revisar primero:

```sh
apt-get -s install --no-install-recommends python3 libasound2t64 libx11-6 alsa-utils python3-gi gir1.2-gtk-3.0 gir1.2-pango-1.0
sudo apt-get install --no-install-recommends python3 libasound2t64 libx11-6 alsa-utils python3-gi gir1.2-gtk-3.0 gir1.2-pango-1.0
```

Con el respaldo comprobado, instalar los componentes juntos:

```sh
umask 022
install -d -m 755 "$HOME/scripts" "$HOME/.config/audio" "$HOME/.config/calendar" "$HOME/.config/i3" "$HOME/.config/i3status"
install -m 755 scripts/audio-control.py scripts/audio-volume.py scripts/audio-position.py scripts/open-mixer.sh scripts/status-panel.py scripts/status-clicks.py scripts/status-bar.sh "$HOME/scripts/"
install -m 644 config/audio/usb-audio.json "$HOME/.config/audio/usb-audio.json"
install -m 644 config/calendar/calendar.css "$HOME/.config/calendar/calendar.css"
install -m 644 config/i3status-config "$HOME/.config/i3status/config"
install -m 644 config/keybindings-help.txt "$HOME/.config/i3/keybindings-help.txt"
```

En i3, sustituir sólo la regla anterior `BGH-Mixer` por la regla exacta de
`BGH-Audio-Volume`/`bgh-audio-volume` de `config/i3-config`, manteniendo las
diferencias locales. En una restauración limpia, instalar esa fuente completa
como `~/.config/i3/config`, modo644. Validar:

```sh
sh -n scripts/status-bar.sh scripts/open-mixer.sh
i3 -C -c "$HOME/.config/i3/config"
python3 "$HOME/scripts/audio-control.py"
i3-msg restart
```

El JSON debe indicar `ready`, porcentaje y estado de mute si está conectado.
El restart renueva i3bar conservando ventanas; un reload puede conservar el
adaptador anterior. Comparar contenidos, modos y propietarios: scripts755,
JSON/CSS/configuración/ayuda644, todos jd:jd. Los comentarios locales de i3
pueden diferir si se conservaron deliberadamente.

## Verification

Diagnóstico de sólo lectura, usando el número actual comprobado:

```sh
cat /proc/asound/cards
aplay -l
amixer -c Device sget Speaker
python3 scripts/audio-control.py
python3 -m unittest discover -s tests -p test_audio_control.py
```

Verificar el porcentaje, abrir/cerrar el panel y ajustar a un nivel cómodo
durante una reproducción elegida localmente. Confirmar el cambio audible y
que mute responde sólo a su control. No iniciar una prueba de sonido ni subir
volumen automáticamente. Para comprobar desconexión/reconexión, coordinar la
retirada de sólo el adaptador de audio y esperar hasta un tick por transición;
la barra debe pasar por `No audio` y recuperar el porcentaje sin reiniciarla.
Una desconexión con el panel abierto debe impedir nuevas escrituras.

Las pruebas sintéticas cubren selección, controles de reproducción, errores,
ambigüedad e IDs reutilizados; no demuestran audición, reinstalación limpia ni
coste sostenido de CPU.

## Current verification — 2026-11-15

- Detectado el USB con `Speaker` estéreo, rango ALSA0…151. Lectura inicial
  17 % y cambio manual a 30 % contrastados con amixer; volumen audible y Mute
  comprobados localmente. Micrófono, captura y AGC conservaron sus valores.
- Barra con porcentaje real, sin errores del mixer Master. Clic y Super+A
  alternan el panel bajo audio; anclaje de teclado `(986,24)` y ventana
  360×233 en `(806,28)` comprobados en la pantalla de 1366×768.
- Reconexión real en otro puerto USB y mediante hub: porcentaje recuperado y
  ajuste de volumen confirmado, sin reiniciar la barra. Perfil sin puerto ni
  número de tarjeta fijo; reapertura del panel enlaza la nueva conexión.
- Doce archivos de usuario instalados, con respaldo privado, contenidos,
  propietario y modos contrastados; dos comentarios anteriores de i3 y el
  README runtime divergente conservados. Parsers i3/shell/GTK y 17 regresiones
  específicas de audio/posición correctos; suite e inventario general en
  [Verification status](mirror-status.md).
- Sin paquetes, servidores de audio ni procesos residentes nuevos. El panel
  no sondea; la barra mantiene su tick de 10 s y SIGSTOP/SIGCONT. No se midió
  consumo sostenido ni se probó una reinstalación limpia.

## Recovery

Cerrar sólo el panel de audio y restaurar desde el respaldo los scripts,
perfil, i3status, regla i3, CSS y ayuda afectados. Mantener el adaptador de barra
y su configuración i3status de la misma revisión. Retirar sólo los dos scripts
nuevos, el módulo de posición y el perfil si antes no existían. Validar i3 y renovar con
`i3-msg restart`; no retirar bibliotecas compartidas, cambiar servicios o tocar
otras tarjetas. Los cambios de volumen aplicados son estado ALSA del dispositivo;
cerrar/restaurar archivos no los revierte ni garantiza persistencia al reconectar.

## References

- [ALSA mixer interface](https://www.alsa-project.org/alsa-doc/alsa-lib/group___mixer.html).
- [ALSA simple mixer API](https://www.alsa-project.org/alsa-doc/alsa-lib/mixer_8h.html).
- [amixer](https://manpages.debian.org/trixie/alsa-utils/amixer.1.en.html).
- [GTK3 Scale](https://docs.gtk.org/gtk3/class.Scale.html).
- [i3bar text widths and positioning](https://github.com/i3/i3/blob/4.24/i3bar/src/xcb.c).
