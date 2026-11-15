# Bluetooth and Magic Trackpad 2

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

## Current verification — 2026-11-15

- Detectados adaptador CSR USB `0a12:0001` y trackpad USB `05ac:0265`.
- BlueZ ya instalado y servicio activo/habilitado; controlador encendido y sin
  bloqueo Bluetooth. No se instalaron paquetes ni se cambiaron servicios.
- Emparejamiento, claves persistidas y confianza verificados; enlace activo
  después de cerrar el agente, con escaneo y emparejamiento nuevos desactivados.
- Driver nativo `magicmouse` enlazado a HID Bluetooth `004c:0265`; alta real
  en Xorg con libinput. Movimiento, ambos clics y scroll confirmados localmente
  sin cable. No se probó reconexión tras reinicio/suspensión ni estabilidad
  prolongada; no se midió consumo sostenido.

## Recovery and private state

Si se pierde el enlace, comprobar carga/interruptor, adaptador, bloqueo Bluetooth
y `bluetoothctl info`; intentar `connect <TRACKPAD_ADDRESS>`. El cable USB
permite usar/cargar el trackpad mientras se revisa Bluetooth.

Para retirar sólo este emparejamiento, con otro dispositivo de entrada disponible,
usar `bluetoothctl remove <TRACKPAD_ADDRESS>`; después hará falta emparejar otra
vez. No apagar el controlador ni detener el servicio si atiende otros dispositivos.

No se desplegaron archivos propios: el [manifiesto](../config/manifest.json)
no añade destinos para este componente. `/etc/bluetooth/` conserva los archivos
del paquete; `/var/lib/bluetooth/` es estado privado de root con claves de enlace,
fuera del repositorio y del snapshot. Direcciones, números de serie y nombres
personales tampoco se publican. Una reinstalación requiere nuevo emparejamiento;
Git no restaura esas claves.

## References

- [BlueZ 5.82 bluetoothctl](https://github.com/bluez/bluez/blob/5.82/client/bluetoothctl.rst).
- [Apple Magic Trackpad connection troubleshooting](https://support.apple.com/en-gb/102498).
