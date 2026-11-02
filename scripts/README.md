# Runtime scripts

Fuentes ejecutadas por i3, el lanzador o timers. Se instalan en
`/home/jd/scripts/`, modo 755; este README se instala 644. Excepción:
`scripts/codex-launch.py` se instala en `~/.local/bin/codex`, modo 755.
El [manifiesto](../config/manifest.json) define rutas completas y permisos.

| Fuente relativa al proyecto | Uso / ciclo de vida |
|---|---|
| `scripts/codex-launch.py` | Ejecuta el standalone oficial; recupera sólo su alias de socket obsoleto bajo lock; bajo demanda |
| `scripts/power-menu` | Rofi de energía, Super+Shift+P o entrada Power; bajo demanda |
| `scripts/power-action.sh` | Auxiliar logind/Polkit en Kitty tras confirmar; bajo demanda |
| `scripts/status-bar.sh` | Selecciona sensor/audio y ejecuta i3status al iniciar barra |
| `scripts/status-clicks.py` | Adaptador residente de i3bar; clicks, iconos y tráfico |
| `scripts/open-networks.sh` | nmtui-connect en Kitty flotante; click/Super+N |
| `scripts/open-mixer.sh` | Panel ALSA si hay dispositivo; click/Super+A |
| `scripts/open-updates.sh` | Lista APT local de sólo lectura; click/Super+U |
| `scripts/update-weather.py` | Oneshot del timer de clima; cache cada 30 min |
| `scripts/update-packages.py` | Oneshot del timer APT; simulación local cada 6 h |

`status-bar.sh` no mantiene un shell adicional tras exec. El adaptador Python
sí es residente; los menús y refrescos no tienen bucles permanentes.

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
~/scripts/power-menu --dry-run 'Power off'  # sin ventanas ni comandos reales
~/scripts/power-menu --preview             # menú y confirmación, sin acciones
# En terminal de la sesión física activa, no SSH:
~/scripts/power-action.sh --dry-run poweroff
~/scripts/power-action.sh --dry-run reboot
~/scripts/power-action.sh --dry-run suspend # tampoco bloquea la pantalla
```

`tools/verify-power-session.sh` comprueba esos dry-runs y toma un inhibidor block
temporal de 8 s. No ejecutarlo mientras se intenta apagar/suspender. Las pruebas
de autorización, preview y block pasaron; no equivalen a una prueba física de
apagado/reanudación. Suspensión por tapa/inactividad es un tema independiente.

## Maintenance

Editar fuentes, respaldar destinos, instalar y comparar contenidos/permisos.
Para revertir, restaurar el archivo correspondiente de un backup privado y
actualizar la fuente; no desactivar protecciones para recuperar una acción.

[Barra](../docs/status-bar.md) · [Recuperación](../docs/restore-guide.md) ·
[Rofi dmenu](https://manpages.debian.org/trixie/rofi/rofi-dmenu.5.en.html) ·
[systemctl v257](https://www.freedesktop.org/software/systemd/man/257/systemctl.html)
