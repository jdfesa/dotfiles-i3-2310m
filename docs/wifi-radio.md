# Wi-Fi startup radio

## Status and scope

La activación inicial de la RTL8188CE desde un encendido completo está
comprobada en la BGH A470: el auxiliar pasa de `soft=0 / hard=1` a
`soft=0 / hard=0`, termina y NetworkManager conecta sin pulsar Fn+F11.
Esto verifica la activación en ese arranque; no demuestra que el BIOS
conserve la radio encendida entre apagados ni la estabilidad posterior.

**La estabilidad sigue pendiente**: se observó una pérdida posterior del
enlace con la radio habilitada. Su causa no está determinada. Mantener el
TODO abierto y la rama sin integrar hasta repetir la comprobación con uso
normal sostenido, sin recuperación manual.

El auxiliar es específico de Phoenix `1.04.00.BH` del `06/09/2011`, la tarjeta
`10ec:8176` con subsistema `10ec:8181` y `rtl8192ce`. Comprueba además los
identificadores DMI y la huella completa de la DSDT fijados en
[`enable-wifi-radio.py`](../scripts/enable-wifi-radio.py). Una diferencia
detiene la operación; no sustituir la huella automáticamente.

## Operation

El BIOS conserva el campo `E45B` del controlador integrado al suspender y lo
restaura en `_WAK`. En este equipo, el bit 7 del byte `0x5b` cambia con
Fn+F11 y permite activar la radio mediante `ec_sys` del kernel instalado.
El auxiliar acepta sólo los valores completos comprobados: `0x00` con
hard block para escribir una vez `0x80`; si ya está encendida, no escribe.
No modifica otros indicadores, un soft block, perfiles ni contraseñas.

Las escrituras EC deben empezar deshabilitadas. Se habilitan sólo durante
la operación y se restauran incluso ante errores ordinarios o señales de
terminación. Un marcador privado en `/run/bgh-wifi-radio` permite que
`ExecStopPost` restaure ese permiso después de una interrupción abrupta.
Un lock evita dos invocaciones simultáneas del auxiliar; no sustituye la
sincronización interna del firmware. No pulsar otras teclas de radio durante
la operación. No se flashea firmware ni se escribe la memoria CMOS.

La unidad de sistema arranca después de NetworkManager, espera como máximo
10 s a que aparezca su radio y comprueba el resultado durante hasta 10 s.
Tiene un límite de inicio de 25 s, no reinicia servicios de red, no reintenta
la escritura y termina sin proceso residente, timer ni monitor de teclas.
Un fallo conserva Fn+F11 como recuperación manual.

## Dependencies and installation

Usa Python 3 con biblioteca estándar, systemd y el kernel Debian existentes;
no instala paquetes, DKMS ni controladores de terceros. Entorno comprobado:
Debian 13, kernel `6.12.111+deb13-amd64`, systemd 257 y
`CONFIG_ACPI_EC_DEBUGFS=y`. Requiere debugfs montado, DSDT accesible para root
y `/sys/module/ec_sys/parameters/write_support` inicialmente en `N`.

Fuentes, destinos y modos se declaran en el
[Configuration manifest](../config/manifest.json):

| Source | Installation |
|---|---|
| `scripts/enable-wifi-radio.py` | `/usr/local/libexec/bgh-wifi-radio`, root:root 755, archivo regular |
| `config/wifi-radio/bgh-wifi-radio.service` | `/etc/systemd/system/bgh-wifi-radio.service`, root:root 644 |

La instalación privilegiada se separa de la operación. Desde la raíz del
checkout, revisar el plan y después aplicarlo con sudo autenticado:

```sh
python3 tools/install-wifi-radio.py
sudo python3 tools/install-wifi-radio.py --apply
```

El instalador comprueba conflictos por archivo y rechaza enlaces simbólicos.
Respalda destinos existentes y el estado de habilitación en un directorio
root:root 700 bajo `/var/backups/bgh-wifi-radio-*`, fuera del repositorio.
Instala, compara contenido/propietarios/modos, valida la unidad y la habilita
para el siguiente arranque; **no la inicia ni reinicia el equipo**.
Los archivos de sistema no enlazan al checkout modificable por jd.

## Verification

Las pruebas simuladas no acceden al controlador ni demuestran un arranque:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_wifi_radio.py -v
sudo /usr/local/libexec/bgh-wifi-radio
systemctl is-enabled bgh-wifi-radio.service
```

La invocación sin argumentos sólo inspecciona. Con Wi-Fi ya encendido,
`sudo systemctl start bgh-wifi-radio.service` debe terminar sin escribir.
Consultar `systemctl show bgh-wifi-radio.service -p Result -p ExecMainStatus -p MainPID`
y `sudo journalctl -b -u bgh-wifi-radio.service --no-pager`.

Para validar el objetivo, guardar el trabajo y coordinar un apagado y encendido
completos. No basta reiniciar, reanudar ni probar con la radio ya encendida.
Al encender, no pulsar Fn+F11. Comprobar:

```sh
/usr/sbin/rfkill --output ID,TYPE,SOFT,HARD
nmcli -f GENERAL.STATE device show wlp2s0
cat /sys/module/ec_sys/parameters/write_support
sudo journalctl -b -u bgh-wifi-radio.service --no-pager
curl --interface wlp2s0 --connect-timeout 5 --max-time 15 -I https://deb.debian.org/
```

Exigir hard block eliminado, interfaz conectada, `write_support=N`, unidad
terminada y HTTPS por `wlp2s0`. Una conexión USB o Ethernet no demuestra que
funcione el Wi-Fi. Conservar una conexión alternativa durante las pruebas.

Continuar con uso normal durante al menos 15 minutos, incluidos intervalos
sin tráfico deliberado, y repetir las comprobaciones de radio y conexión.
Repetir también desde otro encendido completo coordinado. Una petición HTTPS
o unos pocos pings correctos no demuestran estabilidad sostenida.

### Link loss after startup

La X de la barra no distingue una radio bloqueada de una pérdida de enlace.
Si reaparecen lentitud o desconexión, consultar el estado **antes de pulsar
Fn+F11**, reiniciar servicios o modificar parámetros:

```sh
date --iso-8601=seconds
/usr/sbin/rfkill --output ID,TYPE,SOFT,HARD
nmcli -f GENERAL.STATE,GENERAL.REASON device show wlp2s0
/usr/sbin/iw dev wlp2s0 link
/usr/sbin/iw dev wlp2s0 get power_save
sudo journalctl -b -o short-monotonic --no-pager \
  -u bgh-wifi-radio.service -u NetworkManager.service -u wpa_supplicant.service
sudo journalctl -b -k -o short-monotonic --no-pager
```

`iw` es la herramienta de diagnóstico de Debian; estas consultas no cambian
la conexión. Los registros y la salida del enlace pueden incluir SSID y
direcciones: conservarlos en privado fuera del repositorio.

Con `hard=0 / soft=0`, revisar la pérdida de asociación y las respuestas del
punto de acceso; no repetir la escritura EC para resolver ese estado. Con
`hard=1`, revisar el momento del bloqueo respecto de las pulsaciones físicas.
Un ciclo manual de apagado/encendido puede recuperar el enlace, pero cambia
el estado que se necesita diagnosticar.

El ahorro de energía activo por sí solo no identifica la causa. Cualquier
prueba que lo cambie debe comparar una sola variable, conservar su valor
anterior y coordinarse antes de alterar la conexión. No añadir un monitor
permanente ni reinicios automáticos para ocultar la caída.

## Recovery and maintenance

Si no se activa, usar Fn+F11 integrado y consultar el error de la unidad.
Deshabilitar únicamente esta automatización si hace falta:

```sh
sudo systemctl disable --now bgh-wifi-radio.service
sudo /usr/local/libexec/bgh-wifi-radio --restore-guard
cat /sys/module/ec_sys/parameters/write_support
```

El último valor debe ser `N`. `--restore-guard` sólo restaura un permiso
respaldado por su marcador propio; no escribe en la radio. Si un proceso se
interrumpió fuera de systemd, ejecutar esa recuperación antes de retirar archivos.

Para desinstalar la primera instalación, verificar `rollback.json` del respaldo:
si ambos destinos figuraban ausentes, retirar sólo esos dos archivos después
de deshabilitar la unidad y ejecutar `sudo systemctl daemon-reload`. Si había
versiones previas, restaurarlas con sus modos/propietarios registrados y
recuperar el estado anterior de habilitación. No restaurar otros servicios.

Un cambio de BIOS, DSDT, kernel o tarjeta exige revisar compatibilidad antes
de ampliar el perfil. Los identificadores y la operación viven en el script;
destinos/modos, en el manifiesto; instalación, en `tools/install-wifi-radio.py`.
Mantener fallos de identidad, flags desconocidos, carreras e interrupciones
cubiertos por pruebas simuladas y coordinar cualquier nueva prueba física.
Las tablas completas, capturas y respaldos permanecen privados.

Referencias: [Linux ec_sys](https://github.com/torvalds/linux/blob/v6.12/drivers/acpi/ec_sys.c),
[RTL8192CE radio state](https://github.com/torvalds/linux/blob/v6.12/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.c),
[iw diagnostics](https://wireless.docs.kernel.org/en/latest/en/users/documentation/iw.html),
[systemd.service](https://www.freedesktop.org/software/systemd/man/257/systemd.service.html).
