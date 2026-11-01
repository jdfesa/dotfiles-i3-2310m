# User account migration

## Reference state

Desde 2026-11-01: cuenta/grupo `jd`, home `/home/jd`, UID/GID **1000**.
La migración desde `joe` conservó datos, grupos y credenciales; no creó otra
cuenta con UID distinto. Cuenta/home temporales de administración retirados.
El manifiesto corresponde al home nuevo.

Esta es una operación de mantenimiento ya completada, **no un paso requerido**
al reinstalar Debian con la cuenta correcta.

## Procedure and limitations

1. Comprobar colisiones de cuenta/grupo/home y dependencias nominales.
2. Respaldar bases de cuentas sólo en un directorio privado root, fuera del repo.
   Preparar y verificar una vía administrativa independiente, con sudo normal.
3. Con trabajo guardado, cerrar sesiones de la cuenta a modificar y esperar cero
   procesos de su UID. No renombrar desde su única sesión administrativa.
4. Renombrar login/grupo y mover home preservando UID/GID, no duplicar datos
   para eliminar después la cuenta original.
5. Revisar prefijos administrados y enlaces absolutos; trasladar con el home
   datos privados sin reescribir chats, memorias o historiales.
6. Comprobar SSH/sudo/login físico/i3, grupos, permisos y timers antes de retirar
   el acceso temporal.

`tools/relocate-user-home.py` sólo repara rutas revisadas y cinco enlaces
Codex/timers. Inspecciona por defecto; `--apply` exige root, cuenta jd/UID1000 y
backup privado bajo `/root/bgh-a470-backups`. Escritura atómica con modos/IDs
preservados; no implementa la migración de cuentas ni un instalador general.

## Verification and recovery

Se comprobaron login físico/i3/terminal, SSH/sudo, shell/i3 parsers, timers y
propiedad numérica. Home/.ssh 700 y archivos de autorización 600. Configuración
adicional de aplicaciones conservada; la reaplicación de la reparación no produjo
cambios. No hubo reinicio de Debian/red.

Para revertir hacen falta acceso independiente, ausencia de procesos de la cuenta
y revisión de colisiones/rutas. No restaurar passwd/shadow globales a ciegas:
puede perder cambios de otras cuentas. Backups de cuentas nunca se publican.
La migración general a symlinks permanece [pendiente](repository-layout.md).
