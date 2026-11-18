# Bluetooth and Magic Trackpad 2

La configuración pública de usuario se enlaza siguiendo
[User configuration links](user-config-links.md); sus comandos distinguen
el dry-run del despliegue con respaldo. No instalar copias paralelas de scripts.

## Scope

El Magic Trackpad 2 usa la pila incluida en Debian: `btusb` para el adaptador,
BlueZ para el enlace, `hid_magicmouse` del kernel y libinput en Xorg para la
entrada. `bluetoothctl` se ejecuta bajo demanda; no se añade gestor gráfico,
agente permanente, sondeo ni servicio de gestos.

Las [versiones verificadas](dependencies.md) identifican los paquetes probados.
No se instalan controladores externos, módulos DKMS ni firmware descargado
manualmente para estos dispositivos.

## Detection and installation

Comprobar primero el hardware y el estado existente:

```sh
lsusb -d 0a12:0001
lsusb -d 05ac:0265                 # Sólo aparece mientras usa el cable USB.
/usr/sbin/rfkill list bluetooth
systemctl is-active bluetooth.service
systemctl is-enabled bluetooth.service
bluetoothctl list
bluetoothctl show
```

El adaptador debe aparecer como controlador y mostrar `Powered: yes`; Bluetooth
no debe tener bloqueo físico ni lógico. No desbloquear todas las radios ni
modificar Wi-Fi para resolver el enlace del trackpad.

En una reinstalación, únicamente si faltan estos paquetes y usando los
repositorios Debian firmados:

```sh
sudo apt-get --simulate install --no-install-recommends \
  bluez xserver-xorg-input-libinput
sudo apt-get install --no-install-recommends \
  bluez xserver-xorg-input-libinput
sudo systemctl enable --now bluetooth.service
```

Revisar la simulación antes de instalar. El servicio ya activo/habilitado no
necesita reinicio. Usar `bluetoothctl` como cuenta de sesión con la autorización
estándar de Debian; `jd` ya pertenece al grupo `bluetooth`. No cambiar políticas
D-Bus/polkit ni conceder sudo sin contraseña.

## Pairing

Desconectar sólo el cable del trackpad, conservar el adaptador conectado y
encender el trackpad. Si no aparece, apagarlo y encenderlo con su interruptor;
si sigue asociado a otro equipo, desvincularlo allí antes de continuar.

Abrir `bluetoothctl --agent KeyboardDisplay` como cuenta de sesión. En su prompt:

```text
power on
scan on
devices
info <TRACKPAD_ADDRESS>
```

Sustituir `<TRACKPAD_ADDRESS>` por la dirección observada localmente; no ejecutar
el marcador literal. Identificar el dispositivo por nombre y por el modalias
`bluetooth:v004Cp0265…`, no sólo por una dirección o proximidad. Limitar cada
escaneo a unos 30 segundos y ejecutar `scan off` si no aparece.

Para un trackpad nuevo con `Paired: no`:

```text
pair <TRACKPAD_ADDRESS>
trust <TRACKPAD_ADDRESS>
connect <TRACKPAD_ADDRESS>
scan off
info <TRACKPAD_ADDRESS>
pairable off
show
quit
```

Esperar el resultado de cada operación. Sólo confiar en el trackpad identificado.
`info` debe mostrar `Paired`, `Bonded`, `Trusted` y `Connected` en `yes`.
La conexión inicial puede cerrarse después de emparejar; `trust` y `connect`
explícitos completaron el enlace comprobado. Para un dispositivo ya emparejado,
usar `connect`, sin repetir `pair` ni eliminar sus claves.

Al terminar, conservar `Powered: yes`, `Discoverable: no`, `Pairable: no` y
`Discovering: no`. Cerrar el agente temporal no desconecta el trackpad.

## Verification

Con el cable retirado, probar movimiento, clic físico, desplazamiento con dos
dedos y clic derecho presionando con dos dedos. Xorg debe registrar el
dispositivo como `Apple Inc. Magic Trackpad 2`, tipo `TOUCHPAD`, con libinput:

```sh
grep -F 'Apple Inc. Magic Trackpad 2' ~/.local/share/xorg/Xorg.0.log
bluetoothctl info <TRACKPAD_ADDRESS>
bluetoothctl show
```

No confundir la entrada USB con una conexión inalámbrica. La batería y los
gestos adicionales dependen del soporte del dispositivo/aplicación; no añadir
un daemon sólo para completar esta comprobación.

## Status indicators

La barra conserva dos bloques visibles, incluso contraída:

| Indicador | Estado |
|---|---|
| Bluetooth azul | Adaptador presente y encendido; variante conectada cuando el trackpad Bluetooth está activo |
| Bluetooth gris / rojo | Gris: presente pero apagado; rojo: sin adaptador; `?`: no se pudo consultar BlueZ |
| Trackpad `N%` | Porcentaje obtenido del informe HID del trackpad conectado; `+` indica carga reportada |
| Trackpad `off` / `--%` | `off`: sin enlace Bluetooth activo; `--%`: conectado, sin lectura válida |
| Trackpad `~N%` | Última lectura conservada tras un fallo; se descarta al superar 10 min |

El 0 % de `/sys/class/power_supply/` observado por Bluetooth no es una medida
válida en esta combinación de kernel/dispositivo. Se reutiliza `read_battery`
del proveedor [magic-trackpad-battery](../config/bluetooth/vendor/upstream.md),
sin modificarlo ni ejecutar su daemon, notificaciones o timer de reconexión.
La identificación por HID exacto funciona también con nombres personalizados.

`bluetooth-status.py` se importa en el adaptador residente de la barra. Consulta
`Powered` de BlueZ mediante `libsystemd0`/ctypes en el tick existente de 10 s,
con timeout de 1 s por controlador. Una consulta HID breve se inicia al conectar
y cada 5 min; la barra no espera su respuesta. Si sigue pendiente después de
15 s se cancela en el siguiente tick. Sólo ese auxiliar breve es un proceso
adicional; cache y estado viven en memoria. El chevrón redibuja sin consultas.
Una lectura fresca de hasta 15 % activa urgencia si no se está cargando.

## Pointer speed

Los deslizamientos de tres dedos para cambiar de escritorio se configuran en
[Trackpad gestures](trackpad-gestures.md), por separado del enlace Bluetooth.

Clic izquierdo sobre el bloque del trackpad (icono o batería) alterna **Trackpad
speed** bajo el bloque, con el estilo del calendario. Elegir desde **Slowest**
hasta **Fastest** con las flechas o el ratón; Enter o **Apply** aplica y cierra.
**Default** vuelve al valor nativo del driver (+0.00). Un segundo clic en el
bloque, **Close** o Escape cierra sin aplicar. Sólo se ajusta
`libinput Accel Speed` del Magic Trackpad 2 por Bluetooth, no el perfil de
aceleración, el panel interno ni el ratón. Los cambios manuales duran la conexión
actual; al reconectar o iniciar Xorg se aplica **Slightly faster** (+0.25),
el nivel existente inmediatamente posterior a **Default**.

Instalar [xinput de Debian](https://manpages.debian.org/trixie/xinput/xinput.1.en.html),
sin recomendaciones. Comparte GTK3, CSS y posicionamiento con el calendario
(véase [Status panels](status-panels.md)). No requiere sudo al abrir el panel
ni sondeo adicional.

```sh
apt-get -s install --no-install-recommends xinput
sudo apt-get install --no-install-recommends xinput
```

El auxiliar comprueba el HID Bluetooth y el nodo XInput antes de cualquier
escritura. Si se pierde la conexión con el menú abierto, no cambia otro
dispositivo. Para comprobarlo, seleccionar un nivel y comparar el valor actual
al reabrir el panel. Para retirar el control manual, seleccionar **Default** y
restaurar adaptador y auxiliar según el respaldo.

### Initial speed

`config/bluetooth/90-bgh-magic-trackpad-speed.conf` fija únicamente
`AccelSpeed` a `0.25` cuando Xorg crea el dispositivo. La regla udev existente
marca sólo el evento de entrada del HID Bluetooth `0005:004C:0265`, driver
`magicmouse` y tipo touchpad, mediante `ID_INPUT.tags`; conserva etiquetas
previas y no amplía permisos. El InputClass exige esa etiqueta, `libinput` y
un touchpad. No afecta al trackpad por USB ni a otros punteros.

Ambos archivos de sistema se instalan como root, regulares y con modo 644,
según [Indicator installation and recovery](#indicator-installation-and-recovery).
No hay servicio, proceso de inicio, sondeo ni escritura desde la barra para
reaplicar el valor. El panel sigue permitiendo cambiarlo durante la conexión.

Validar la regla con `udevadm verify` y ejecutar
`python3 -m unittest discover -s tests -p test_trackpad_speed.py`.
La configuración nueva necesita que Xorg vuelva a leer sus archivos; recargar
i3 no basta. En el siguiente inicio local coordinado, abrir el panel antes de
ajustarlo y comprobar **Current: +0.25** y **Slightly faster** seleccionado.
No reiniciar X ni desconectar el trackpad sólo para forzar esta comprobación.

Para revertir la velocidad inicial, restaurar la regla udev anterior desde el
respaldo privado y restaurar o retirar sólo el InputClass añadido. La siguiente
sesión Xorg usará de nuevo el valor del driver; el panel manual permanece.

## Indicator installation and recovery

Como `jd`, respaldar primero los destinos existentes en un directorio privado
fuera del checkout y registrar cuáles no existían. La regla udev y el InputClass
se instalan por separado con sudo autenticado. Fuentes, destinos y modos en el
[manifiesto](../config/manifest.json):

```sh
umask 022
python3 tools/link-user-config.py  # Dry-run; apply the reviewed link plan separately.
udevadm verify config/bluetooth/72-bgh-magic-trackpad.rules
sudo install -o root -g root -m 644 config/bluetooth/72-bgh-magic-trackpad.rules \
  /etc/udev/rules.d/72-bgh-magic-trackpad.rules
sudo install -d -o root -g root -m 755 /etc/X11/xorg.conf.d
sudo install -o root -g root -m 644 config/bluetooth/90-bgh-magic-trackpad-speed.conf \
  /etc/X11/xorg.conf.d/90-bgh-magic-trackpad-speed.conf
sudo udevadm control --reload-rules
```

La regla concede acceso hidraw sólo a la sesión local activa (`uaccess`, seat0)
y al HID Bluetooth `004c:0265` con driver `magicmouse`. No añade grupos, permisos
globales ni acceso root a la barra. Para aplicarla al dispositivo conectado,
identificar primero su `hidrawN` por `device/uevent` y ejecutar sólo para él:

```sh
sudo udevadm trigger --action=add --settle /sys/class/hidraw/hidrawN
~/dotfiles-i3-2310m/scripts/bluetooth-status.py --read-battery hidrawN
i3-msg restart
```

Sustituir `hidrawN` por el nodo comprobado; no disparar todos los dispositivos.
El informe debe devolver `[porcentaje, cargando]`, o `null` si no hay lectura.
Contrastar hashes y modos: archivos de usuario jd:jd, auxiliar/adaptador755,
proveedor/licencia644; regla e InputClass root:root644, regulares. El restart
conserva ventanas, pero no recarga el InputClass de Xorg.

Para revertir, restaurar primero el adaptador anterior y reiniciar i3. Restaurar
la regla previa desde su respaldo; si estaba ausente, retirar sólo la regla
añadida. Recargar reglas y coordinar desconexión/reconexión sólo del trackpad
para recrear su nodo sin la ACL añadida. Restaurar
o retirar únicamente los archivos de usuario adicionales según el registro
previo. La reversión de los indicadores conserva el emparejamiento.

## Current verification — 2026-11-15

- Detectados adaptador CSR USB `0a12:0001` y trackpad USB `05ac:0265`.
- BlueZ ya instalado y servicio activo/habilitado; controlador encendido y sin
  bloqueo Bluetooth. No se instalaron paquetes ni se cambiaron servicios.
- Emparejamiento, claves persistidas y confianza verificados; enlace activo
  después de cerrar el agente, con escaneo y emparejamiento nuevos desactivados.
- Driver nativo `magicmouse` enlazado a HID Bluetooth `004c:0265`; alta real
  en Xorg con libinput. Movimiento, ambos clics y scroll confirmados localmente
  sin cable. Lector fijado devolvió 99 % como `jd`, con acceso limitado por udev.
- Ambos pictogramas Propo12 renderizados en i3bar, sin recortes; retirada real
  del dongle produjo Bluetooth rojo y trackpad `off`, sin porcentaje anterior.
  Al reinsertar, BlueZ recuperó encendido y claves; hizo falta `connect` explícito.
  No se añade reconexión periódica. No se probaron reinicio/suspensión ni
  estabilidad prolongada; no se midió consumo sostenido.

## Recovery and private state

Si se pierde el enlace, comprobar carga/interruptor, adaptador, bloqueo Bluetooth
y `bluetoothctl info`; intentar `connect <TRACKPAD_ADDRESS>`. El cable USB
permite usar/cargar el trackpad mientras se revisa Bluetooth.

Para retirar sólo este emparejamiento, con otro dispositivo de entrada disponible,
usar `bluetoothctl remove <TRACKPAD_ADDRESS>`; después hará falta emparejar otra
vez. No apagar el controlador ni detener el servicio si atiende otros dispositivos.

`/etc/bluetooth/` conserva los archivos del paquete; `/var/lib/bluetooth/`
es estado privado de root con claves de enlace,
fuera del repositorio. Direcciones, números de serie y nombres
personales tampoco se publican. Una reinstalación requiere nuevo emparejamiento;
Git no restaura esas claves.

## References

- [BlueZ 5.82 bluetoothctl](https://github.com/bluez/bluez/blob/5.82/client/bluetoothctl.rst).
- [Apple Magic Trackpad connection troubleshooting](https://support.apple.com/en-gb/102498).
