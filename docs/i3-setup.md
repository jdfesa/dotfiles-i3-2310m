# i3 setup

La configuración pública de usuario se enlaza siguiendo
[User configuration links](user-config-links.md); sus comandos distinguen
el dry-run del despliegue con respaldo. No instalar copias paralelas de scripts.

## Minimal session

Xorg + i3 de Debian; sin escritorio completo, display manager ni autologin.
La composición básica de Kitty se describe en
[Background opacity](kitty-setup.md#background-opacity).
Paquetes y versiones en [Dependencies](dependencies.md).
La sesión física y ventanas de Kitty/Rofi/Helium fueron comprobadas.

| Fuente | Destino |
|---|---|
| `config/i3-config` | `~/.config/i3/config` |
| `config/i3status-config` | `~/.config/i3status/config` |
| `config/profile` | `~/.profile`, revisar/combinar antes de reemplazar |
| `config/xinitrc` | `~/.xinitrc` |
| `config/login-autostart.sh` | Fragmento de referencia ya incluido en profile |

`.xinitrc` utiliza `/etc/X11/Xsession` para conservar los hooks D-Bus de Debian.
No duplicar el fragmento de inicio ni crear otro servicio para lanzar X.

## Startup

Después del login autenticado como `jd` en la tty1 física, `.profile` ejecuta
`startx` sólo si no existe DISPLAY, no es SSH y no está activo el escape hatch.
tty2+, SSH y terminales gráficas no disparan otro Xorg. Si X termina o falla,
el shell permanece disponible: no hay bucle de relanzamiento.

El inicio manual se hace **sólo desde la consola física**, sin sudo:

```sh
startx
```

No lanzarlo por SSH ni como root. Una sesión con barra y sin iconos de escritorio
es el comportamiento normal de i3. El servidor X mantiene TCP deshabilitado.

## Wallpaper

i3 aplica [Pixel Car](../wallpapers/pixel-car.png) al abrir una sesión.
`xwallpaper --zoom` llena la pantalla conservando la proporción; puede
recortar bordes en pantallas con otra relación de aspecto. No queda ningún
proceso residente para el fondo. Un cambio de resolución o
monitor no reaplica el fondo automáticamente.

Instalar `xwallpaper` desde Debian estable y enlazar la imagen del checkout
mediante el [manifest.json](../config/manifest.json). Como `jd`, revisar y
respaldar en privado el archivo i3 activo y cualquier imagen previa en el
destino antes de reemplazarlos:

```sh
sudo apt-get install --no-install-recommends xwallpaper
python3 tools/link-user-config.py  # Dry-run; apply the reviewed link plan separately.
cmp wallpapers/pixel-car.png "$HOME/.local/share/wallpapers/pixel-car.png"
```

Añadir sólo el `exec` de xwallpaper de `config/i3-config` al archivo activo si
tiene diferencias locales. Desde la sesión i3 abierta, validar y aplicar sin
cerrar aplicaciones:

```sh
i3 -C -c "$HOME/.config/i3/config"
i3-msg reload
xwallpaper --zoom "$HOME/.local/share/wallpapers/pixel-car.png"
```

Comprobar el fondo en un escritorio vacío. Para revertir, retirar sólo esa
línea o restaurar el respaldo revisado, validar y recargar i3; reaplicar el
fondo anterior o ejecutar `xsetroot -def` para volver al fondo predeterminado
de Xorg. Retirar sólo el enlace añadido si antes no existía.

## Verification

```sh
i3 -C -c ~/.config/i3/config
sh -n ~/.profile
sh -n ~/.xinitrc
~/dotfiles-i3-2310m/scripts/status-clicks.py --run-once
```

La última orden produce una muestra de estado; revisar JSON y datos disponibles.
`No battery` es correcto cuando no hay dispositivo Battery; no equivale a 0%.

- Atajos/configuración: `i3-msg reload` o Super+Shift+C.
- Renovar i3bar después de instalar fuentes/cambiar el adaptador:
  `i3-msg restart` o Super+Shift+R, conservando ventanas.
- Un parser correcto no sustituye una prueba gráfica del binding o aplicación.
  En bindings Alt usar `Mod1`.

[Atajos](keybindings.md) · [Barra](status-bar.md)

## Recovery

Entrar por Ctrl+Alt+F2 o SSH con identidad del host verificada:

```sh
touch ~/.config/i3/disable-autostart
```

Corregir desde tty2/SSH y revisar `~/.local/share/xorg/Xorg.0.log` o
`~/.xsession-errors` sin publicar registros privados. Quitar únicamente el
marcador anterior vuelve a permitir el inicio en el próximo login tty1.

El menú Suspend bloquea primero; bloqueo automático por tapa/inactividad sigue
pendiente. Conservar login con contraseña y las vías de recuperación.

Referencias: [i3](https://i3wm.org/docs/userguide.html),
[paquete Debian](https://packages.debian.org/trixie/i3-wm).
