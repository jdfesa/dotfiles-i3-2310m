# Boot troubleshooting

## Status

| Tema | Resultado |
|---|---|
| Suspensión inicial con tapa abierta | Corregida; reinicio y encendido completo comprobados |
| Wi-Fi en frío | Auxiliar experimental; alcance y validación en [Wi-Fi startup radio](wifi-radio.md) |
| Unidad temporal de diagnóstico | Retirada; no instalar al restaurar |
| Cierre real de tapa / bloqueo automático | Prueba pendiente |

Plataforma: BIOS Phoenix SecureCore 1.04.00.BH, KBC 1.05, SATA AHCI y NX
habilitados. No hay firmware alternativo compatible verificado. Conservar
actualizaciones normales de kernel/microcódigo; no flashear ni escribir EC/ACPI
desconocidos como atajo de configuración. La única escritura EC de radio
verificada se delimita en [Wi-Fi startup radio](wifi-radio.md).

## Initial lid state

El firmware podía reportar tapa cerrada durante el inicio aunque permaneciera
abierta. logind suspendía alrededor de sus 30 s de holdoff; no era el temporizador
de inactividad.

`config/grub-lid.cfg` → `/etc/default/grub.d/60-bgh-lid.cfg`, modo 644 root:root.
Añade `button.lid_init_state=open` preservando opciones y una selección explícita
previa. No desactiva ACPI ni los eventos posteriores de tapa.

Después de revisar y respaldar el destino, en Debian:

```sh
sh -n config/grub-lid.cfg
sudo install -m 644 config/grub-lid.cfg /etc/default/grub.d/60-bgh-lid.cfg
sudo update-grub
sudo grub-script-check /boot/grub/grub.cfg
```

Se aplica en el siguiente arranque coordinado. Sintaxis/GRUB y pruebas de
reinicio/encendido pasaron; cierre/reapertura y bloqueo automático siguen pendientes.

Para revertir, retirar únicamente este drop-in y regenerar/validar GRUB.
Si no arranca, quitar temporalmente el parámetro desde el editor de GRUB o usar
recovery. No restaurar un grub.cfg antiguo después de cambiar kernels.

## Wi-Fi radio

La RTL8188CE inicia en algunos ciclos con soft unblocked/hard blocked antes de
Fn+F11. El auxiliar intenta activar la radio en cada arranque compatible; no establece
persistencia en el BIOS. Hard block es un estado del controlador, no prueba
de daño físico; comandos de desbloqueo software no garantizan resolverlo.

- La unidad oneshot temporal capturó el hard block y fue retirada.
  `config/wifi-boot-state.service` queda fuera del manifiesto, sólo referencia.
- `tools/probe-wifi-keys.py` observó durante 45 s únicamente eventos
  Fn/F11/WLAN/RFKILL permitidos y cambios de radio. No registró otras teclas,
  inyectó eventos ni escribió en el controlador.
- Se observó un cambio hard 0→1 sin eventos de teclado de esa lista. Esto no
  descarta todos los códigos/dispositivos, pero no proporcionó una vía simple
  de activación por script. El capturador terminó; radio/SSH se recuperaron.
- Fn+F11 externo no equivale necesariamente a Fn+F11 integrado. No remapear ni
  simular combinaciones a ciegas, ni inferir que falta de IP implica radio apagada.
- La DSDT y el cambio físico de radio identifican un campo EC que permite
  activarla mediante un auxiliar acotado. No requiere blacklists, emulación
  de teclas, otro controlador ni cambiar la pila RTC.

Instalación, límites y validación de activación y estabilidad en
[Wi-Fi startup radio](wifi-radio.md). No reinstalar la unidad diagnóstica
retirada ni repetir capturas de teclado para activar la solución.

Referencias: [ACPI lid](https://www.kernel.org/doc/html/v6.12/firmware-guide/acpi/acpi-lid.html),
[rfkill](https://docs.kernel.org/driver-api/rfkill.html),
[eventos Linux](https://github.com/torvalds/linux/blob/v6.12/include/uapi/linux/input-event-codes.h).
