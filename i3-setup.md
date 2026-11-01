# i3 setup

## Minimal session

Xorg + i3 de Debian; sin escritorio completo, display manager, compositor o
autologin. Paquetes y versiones en [dependencies.md](dependencies.md).
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

## Verification

```sh
i3 -C -c ~/.config/i3/config
sh -n ~/.profile
sh -n ~/.xinitrc
~/scripts/status-clicks.py --run-once
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
