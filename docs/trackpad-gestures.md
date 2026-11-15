# Trackpad gestures

## Workspace swipes

| Gesto en el Magic Trackpad 2 | Acción al levantar los dedos |
|---|---|
| Tres dedos hacia la izquierda | Siguiente escritorio existente de la pantalla enfocada |
| Tres dedos hacia la derecha | Escritorio anterior existente de la pantalla enfocada |

Se usan `workspace next_on_output` y `workspace prev_on_output` de i3, con
vuelta al otro extremo. No se crean escritorios ni se mueven ventanas. Un
deslizamiento debe acumular al menos 100 unidades XInput horizontales y superar
el doble del desplazamiento vertical absoluto. Los gestos breves, diagonales,
verticales, cancelados o con otro número de dedos no cambian el escritorio.

## Runtime and dependencies

`scripts/trackpad-gestures.py` usa Python estándar, `libxi6` y `libx11-6`
existentes mediante ctypes. Requiere XInput 2.4 y el driver libinput de Xorg;
versiones comprobadas en [Dependencies](dependencies.md). No requiere paquetes
adicionales en la portátil ni cambia ajustes del driver.

i3 inicia un único auxiliar por display X. Espera en el socket de Xorg sin
timeout ni sondeo y detecta altas/bajas por `XI_HierarchyChanged`. Comprueba la
propiedad XInput **Device Node**, el HID y el driver `magicmouse` en sysfs:
Bluetooth `0005:004c:0265` o USB `0003:05ac:0265`. No usa nombres personales,
direcciones Bluetooth ni identificadores XInput persistentes. Otros dispositivos
no heredan los gestos; no abre `/dev/input`, solicita sudo ni requiere grupo
`input` o un servicio systemd. Al cerrar X termina la conexión; reiniciar i3
conserva el auxiliar y las ventanas.

La captura pasiva de XInput reserva los **swipes** del dispositivo completo,
incluso los verticales y los de cuatro dedos que se descartan. Esos swipes no
llegan a la aplicación bajo el puntero. No se capturan pinzas, teclas, botones,
movimiento ni scroll de dos dedos. El zoom por pinza sigue dependiendo de la
aplicación X11. Un grab activo de otra aplicación puede impedir recibir gestos.
No se reproducen animaciones de escritorio.

## Installation

Como `jd`, revisar y respaldar privadamente los destinos antes de escribir,
fuera del checkout; registrar los ausentes. Comparar primero los archivos
activos con las fuentes y conservar cambios locales. Rutas y modos en el
[Manifest](../config/manifest.json).

En una instalación nueva, con repositorios Debian firmados, revisar primero:

```sh
apt-get -s install --no-install-recommends python3 libxi6 libx11-6 xserver-xorg-core xserver-xorg-input-libinput i3-wm
sudo apt-get install --no-install-recommends python3 libxi6 libx11-6 xserver-xorg-core xserver-xorg-input-libinput i3-wm
```

Desde la raíz del checkout y dentro de la sesión Xorg autenticada:

```sh
umask 022
install -d -m 755 "$HOME/scripts" "$HOME/.config/i3"
install -m 755 scripts/trackpad-gestures.py "$HOME/scripts/trackpad-gestures.py"
python3 "$HOME/scripts/trackpad-gestures.py" --check
i3 -C -c config/i3-config
```

Después de reconciliar diferencias, instalar `config/i3-config` como
`~/.config/i3/config` y `config/keybindings-help.txt` como
`~/.config/i3/keybindings-help.txt`, ambos644 y jd:jd. La línea nueva es:

```text
exec --no-startup-id ~/scripts/trackpad-gestures.py
```

`exec` se ejecuta al entrar en i3; una recarga no lo inicia. Para activar ahora,
sin salir ni reiniciar i3:

```sh
i3-msg reload
i3-msg 'exec --no-startup-id ~/scripts/trackpad-gestures.py'
```

Una selección X11 privada evita duplicar auxiliares en ese display. Comparar
contenidos, propietario y modos con el manifiesto antes de dar el despliegue
por válido.

## Verification

`--check` comprueba el protocolo y cuenta los dispositivos compatibles sin
capturarlos; cero dispositivos es válido si está desconectado. Para una prueba
sin cambiar escritorios, detener sólo este auxiliar y ejecutarlo en primer plano:

```sh
~/scripts/trackpad-gestures.py --stop
~/scripts/trackpad-gestures.py --dry-run
```

Hacer ambos gestos amplios de tres dedos; debe imprimir el comando correspondiente
una vez al terminar. Probar cuatro dedos, verticales y gestos cortos: **Swipe
ignored.** Comprobar clics y scroll habituales. Ctrl+C cierra la prueba; volver
a iniciar con el comando `i3-msg exec` anterior. `--dry-run` también reserva
los swipes mientras está abierto, pero nunca envía acciones a i3.

Para la prueba real, mantener ventanas en tres escritorios de la misma pantalla,
empezar en el central y comprobar ambos sentidos con `i3-msg -t get_workspaces`.
Sólo deben cambiar foco/escritorio. La detección y las pruebas sintéticas no
demuestran por sí solas reconocimiento físico, reconexión ni consumo sostenido.

Pruebas offline desde el checkout:

```sh
python3 -m unittest discover -s tests -p test_trackpad_gestures.py
```

## Recovery

Para detener exclusivamente los gestos en el display actual:

```sh
~/scripts/trackpad-gestures.py --stop
```

Para retirarlos permanentemente, quitar sólo la línea `exec` nueva de la
configuración i3, restaurar la ayuda previa y recargar. Restaurar el auxiliar
anterior desde el respaldo o retirar sólo ese archivo si antes no existía.
No cambiar Bluetooth, libinput, ACL, grupos o velocidad para revertir los gestos.
Una retirada del trackpad descarta la secuencia pendiente; su próxima alta
XInput vuelve a identificar el hardware sin temporizador de reconexión.

## References

- [libXi XInput2 API](https://gitlab.freedesktop.org/xorg/lib/libxi/-/blob/libXi-1.8.2/include/X11/extensions/XInput2.h).
- [libXi passive gesture grabs](https://gitlab.freedesktop.org/xorg/lib/libxi/-/blob/libXi-1.8.2/man/XIGrabButton.txt).
- [XInput 2.4 protocol definitions](https://www.x.org/releases/individual/proto/xorgproto-2024.1.tar.xz).
- [i3 workspace commands](https://i3wm.org/docs/4.24/userguide.html#_changing_named_workspaces_moving_to_workspaces).
