# Runtime scripts

Fuentes ejecutadas por i3, el lanzador o timers directamente desde
`/home/jd/dotfiles-i3-2310m/scripts/`, modo755; este README se lee en el checkout.
`~/.local/bin/codex` es un enlace al lanzador versionado. Las configuraciones de
usuario se enlazan según [User configuration links](../docs/user-config-links.md).
El [manifiesto](../config/manifest.json) define rutas completas y permisos.

| Fuente relativa al proyecto | Uso / ciclo de vida |
|---|---|
| `scripts/codex-launch.py` | Ejecuta el standalone oficial; recupera sólo su alias de socket obsoleto bajo lock; bajo demanda |
| `scripts/laravel-services.py` | Panel GTK3 bajo demanda para MariaDB/phpMyAdmin, con sudo autenticado en Kitty y estados por eventos; [Laravel development](../docs/laravel-setup.md) |
| `scripts/power-menu` | Rofi de energía, Super+Shift+P o entrada Power; bajo demanda |
| `scripts/power-action.sh` | Auxiliar logind/Polkit en Kitty tras confirmar; bajo demanda |
| `scripts/capture-screenshot.py` | Abre Flameshot bajo demanda; guarda y copia sólo el PNG aceptado; [Screen capture](../docs/screen-capture.md) |
| `scripts/status-bar.sh` | Selecciona sensor y ejecuta i3status al iniciar barra |
| `scripts/status-clicks.py` | Adaptador residente de i3bar; clicks, iconos y tráfico |
| `scripts/bluetooth-status.py` | Módulo del adaptador: estado BlueZ en cada tick y lector HID breve cada 5 min; sin servicio propio |
| `scripts/open-trackpad-speed.py` | Panel GTK3 bajo demanda que ajusta sólo la velocidad del Magic Trackpad 2 Bluetooth en Xorg |
| `scripts/trackpad-gestures.py` | Un residente por pantalla X: espera gestos XInput 2.4 del Magic Trackpad 2, sin sondeo; [Trackpad gestures](../docs/trackpad-gestures.md) |
| `scripts/status-panel.py` | Alterna calendario, btop, brillo, volumen y velocidad del trackpad por identidad; IPC breve por evento, sin sondeo |
| `scripts/screen-brightness.py` | Lee la retroiluminación interna en el tick existente; aplica el brillo inicial con logind y abre el panel GTK3 bajo demanda |
| `scripts/calendar-popup.py` | Calendario GTK3 de sólo lectura; vive sólo mientras está abierto |
| `scripts/open-networks.sh` | Panel único de `nmtui-connect` en Kitty; clic, Super+N o Rofi. [Network panel](../docs/wifi-setup.md#network-panel) |
| `scripts/open-mixer.sh` | Entrada Super+A al panel de volumen USB; sin terminal adicional |
| `scripts/audio-control.py` | Módulo ALSA: lectura de salida USB en el tick existente y escrituras explícitas del panel; ejecución directa sólo lee |
| `scripts/audio-volume.py` | Deslizador GTK3 de volumen/mute; vive sólo mientras está abierto |
| `scripts/audio-position.py` | Publica el tramo de audio de la barra en memoria X11; calcula el anclaje del teclado con Pango sólo al abrir |
| `scripts/refresh-helium-audio.py` | Comprueba el USB y renueva sólo AudioService de Helium con `--apply`; ejecución directa sólo revisa, sin servicio ni sondeo. [USB audio](../docs/audio-setup.md#helium-playback-after-replacing-usb) |
| `scripts/open-updates.sh` | Lista APT local de sólo lectura; click/Super+U |
| `scripts/update-weather.py` | Oneshot del timer de clima; cache cada 30 min |
| `scripts/update-packages.py` | Oneshot del timer APT; simulación local cada 6 h |

`status-bar.sh` no mantiene un shell adicional tras exec. El adaptador Python
sí es residente; el auxiliar de gestos espera eventos de Xorg. Los menús y
refrescos no tienen bucles permanentes.

## Services and triggers

| Fuente config/ | Destino bajo `~/.config/systemd/user/` | Disparo |
|---|---|---|
| `weather-refresh.service` / `.timer` | Mismos nombres | Primer refresco ~15 s; cada 30 min + desfase |
| `packages-refresh.service` / `.timer` | Mismos nombres | Primer refresco ~1 min; cada 6 h |

Servicios acotados a 30 s, Nice=10, umask 0077 y NoNewPrivileges.
Los temporizadores se habilitan en [restore-guide.md](../docs/restore-guide.md).
`config/wifi-boot-state.service` es referencia **inactiva**, no un servicio normal.
Herramientas manuales en [tools/README.md](../tools/README.md).

## Power menu

Orden: **Power off**, Reboot, Suspend, Log out, Lock, Cancel.
Yes está preseleccionado en todas las confirmaciones; **Enter confirma**.
Guardar trabajo antes de abrirlo. Escape, No y Cancel no ejecutan acciones.

- Lock usa i3lock; Log out sólo sale de i3 mediante i3-msg.
- Apagar/reiniciar/suspender abren Kitty y ejecutan el auxiliar como cuenta local,
  sin sudo ni contraseña. `polkitd` usa la política login1 estándar para sesión
  local activa: no reglas personalizadas, NOPASSWD, pkexec o agente GUI.
- El auxiliar sólo acepta `CanPowerOff/CanReboot/CanSuspend = yes`. Si la política
  necesita otra autorización o hay un bloqueo, cancela; no recurre a root.
- Suspend comprueba autorización y bloquea con i3lock antes de suspender.
  Si falla el lock, no suspende; un error posterior se consulta al desbloquear.
- Guardia **systemd >=257**, `--no-ask-password` y `--check-inhibitors=auto`.
  No force, -i, check-inhibitors=no ni acceso directo a sysfs. Se respetan
  inhibidores; otras sesiones pueden impedir una acción normal.
- Polkitd es un servicio estándar adicional de autorización, no una optimización
  de CPU. Dependencia/origen en [dependencies.md](../docs/dependencies.md).

Pruebas sin acciones reales:

```sh
~/dotfiles-i3-2310m/scripts/power-menu --dry-run 'Power off'  # sin ventanas ni comandos reales
~/dotfiles-i3-2310m/scripts/power-menu --preview             # menú y confirmación, sin acciones
# En terminal de la sesión física activa, no SSH:
~/dotfiles-i3-2310m/scripts/power-action.sh --dry-run poweroff
~/dotfiles-i3-2310m/scripts/power-action.sh --dry-run reboot
~/dotfiles-i3-2310m/scripts/power-action.sh --dry-run suspend # tampoco bloquea la pantalla
```

`tools/verify-power-session.sh` comprueba esos dry-runs y toma un inhibidor block
temporal de 8 s. No ejecutarlo mientras se intenta apagar/suspender. Las pruebas
de autorización, preview y block pasaron; no equivalen a una prueba física de
apagado/reanudación. Suspensión por tapa/inactividad es un tema independiente.

## Maintenance

Editar las fuentes y verificar enlaces, contenidos y permisos del manifiesto.
Para revertir, restaurar el archivo correspondiente de un backup privado y
actualizar la fuente; no desactivar protecciones para recuperar una acción.

[Barra](../docs/status-bar.md) · [Recuperación](../docs/restore-guide.md) ·
[Rofi dmenu](https://manpages.debian.org/trixie/rofi/rofi-dmenu.5.en.html) ·
[systemctl v257](https://www.freedesktop.org/software/systemd/man/257/systemctl.html)
