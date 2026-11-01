# Technical TODO

## Publication and reproducibility

- [ ] Probar restauración completa sobre una instalación limpia.
- [ ] Preparar instalador de archivos de usuario con dry-run, conflictos, backup
  privado y rollback; migrar a symlinks sólo después de validar.
- [ ] Revisar diferencias preservadas de `mimeapps.list` y Codex sin importar
  credenciales, rutas efímeras o preferencias privadas.
- [ ] Sincronizar la revisión documental y los comentarios pendientes con la
  portátil cuando SSH esté disponible; verificar antes posibles cambios remotos.

## Hardware and session

- [ ] Wi-Fi al encender: hard block; procedimiento actual **Fn + F11 integrado**.
  Diagnóstico acotado finalizado sin vía simple de activación automática.
  No repetir ciclos ni ingeniería inversa sin nuevo alcance.
- [ ] Probar recuperación física por Ethernet.
- [ ] Validar cierre/reapertura de tapa y bloqueo previo a suspensión automática.
- [ ] Verificar adaptador de audio externo, tarjeta/mixer y reproducción.
- [ ] Revisar brillo y pila RTC.
- [ ] Coordinar prueba física de apagar/reiniciar/suspender/reanudar; dry-run no
  equivale a comprobar esas acciones.

## Productivity and resources

- [ ] Seleccionar editor, herramientas TUI y stacks según proyectos concretos.
- [ ] Medir carga de CPU, memoria y respuesta con tareas representativas antes
  de incorporar LSP, watchers, contenedores u otros servicios.
- [ ] Comparar alternativas cuando exista un problema medido; no asumir que una
  CLI o un terminal diferente es automáticamente más ligero.

Corregidos: suspensión inicial con tapa abierta, barra después de fullscreen y
rutas de cuenta `joe`→`jd`. Detalles técnicos en [CHANGELOG.md](CHANGELOG.md).
