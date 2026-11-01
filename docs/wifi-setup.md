# Network setup

## Interface ownership and status

NetworkManager administra Ethernet `enp4s0` y Wi-Fi `wlp2s0` (RTL8188CE,
controlador `rtl8192ce`). DHCP proporciona dirección, gateway y DNS; no se fija
una IP de la red de instalación en este repositorio.

| Fuente | Destino / función |
|---|---|
| `config/network-interfaces` | `/etc/network/interfaces`; ifupdown sólo loopback |
| `config/networkmanager.conf` | `/etc/NetworkManager/conf.d/20-network-ownership.conf`; DHCP interno/DNS |

El estado final no utiliza la exclusión temporal `10-preserve-ethernet.conf`.
Evitar que dhcpcd/ifupdown y NetworkManager compitan por interfaces o resolv.conf.
Aplicar una migración de red con acceso físico o conexión alternativa, nunca
reiniciando servicios a ciegas por la única sesión SSH.

Dependencias: [dependencies.md](dependencies.md). Los perfiles con secretos no
son archivos administrados por este árbol.

## Creating a connection

Comprobar primero perfiles existentes para no duplicarlos. Ejemplo con nombres
de sustitución, desde la terminal local:

```sh
nmcli connection show
nmcli device status
nmcli --ask device wifi connect 'YOUR_SSID' ifname wlp2s0 name wifi-main
nmcli connection modify wifi-main connection.autoconnect yes \
  connection.autoconnect-retries 0 ipv4.route-metric 2000 ipv6.route-metric 2000
```

`--ask` solicita el secreto interactivamente; no escribirlo en comandos, archivos
del proyecto o historiales. Si faltan permisos, autorizar administrativamente la
operación puntual, no ampliar permisos globales de NetworkManager.
Un perfil Ethernet con DHCP/métrica 1000 tiene prioridad sobre Wi-Fi/métrica 2000.

Los perfiles `/etc/NetworkManager/system-connections/*.nmconnection` pueden
contener PSK y deben permanecer privados, normalmente root:root/600. No copiarlos
al repositorio; recrearlos mediante el flujo interactivo.

## Checks

```sh
rfkill list
nmcli radio
nmcli device status
ip -brief address show dev wlp2s0
ip route
getent ahostsv4 deb.debian.org
wget --spider https://www.debian.org/
```

Una IP en loopback/Ethernet no demuestra conexión Wi-Fi. Verificar interfaz,
radio, ruta y DNS por separado. SSH usa `ssh jd@<HOST>` con el nombre/dirección
DHCP vigente: contrastar la identidad mediante consola o known_hosts previamente
verificado; no aceptar una clave cambiada automáticamente.

Si sólo falla DNS, revisar `/etc/resolv.conf` y sus gestores. NetworkManager
debe regenerarlo con los servidores recibidos; no hacerlo inmutable ni añadir
otro resolvedor para ocultar un conflicto de propiedad.

## Startup limitation

Wi-Fi puede iniciar con **Soft blocked: no / Hard blocked: yes**. El procedimiento
actual es Fn+F11 del teclado integrado. `nmcli radio wifi on` o
`rfkill unblock` no garantizan eliminar un bloqueo hardware.
Autoconexión y reintentos ya están configurados; no añadir bucles o perfiles
duplicados. [Diagnóstico y límites](boot-troubleshooting.md).

Wi-Fi/DNS/SSH sin cable fueron verificados; la recuperación física por Ethernet
sigue pendiente. No exponer SSH mediante el router como parte de esta instalación.

Referencias: [NetworkManager.conf](https://networkmanager.dev/docs/api/latest/NetworkManager.conf.html),
[nmcli](https://networkmanager.dev/docs/api/latest/nmcli.html).
