# Technical TODO

## Publication and reproducibility

- [ ] Verificar arranque de Codex y conservación de la cuenta tras un reinicio
  local coordinado. [Codex CLI](docs/codex-setup.md).
- [ ] Comprobar desbloqueo del keyring tras el próximo login físico coordinado;
  autenticación HTTPS/push ya verificados. [Git workflow](docs/git-workflow.md).

- [ ] Probar restauración completa sobre una instalación limpia.
- [ ] Ampliar la migración de enlaces a componentes anteriores tras revisar
  diferencias; el auxiliar con dry-run/backup/rollback sólo gestiona los seis
  archivos nuevos de [editor/files](docs/editor-and-files.md).
- [ ] Agrupar fuentes heredadas sueltas de `config/` por componente; actualizar
  referencias/manifiesto y probar sin cambiar destinos a ciegas. Las nuevas
  herramientas ya usan carpetas propias.
- [ ] Revisar diferencias preservadas de `mimeapps.list` y Codex sin importar
  credenciales, rutas efímeras o preferencias privadas.

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

- [x] Instalar Neovim/Yazi y base Lua modular con sólo mini.files.
  [Estado y operación](docs/editor-and-files.md).
- [ ] Seleccionar herramientas/stacks adicionales según proyectos concretos.
- [ ] Comprobar comodidad visual y uso diario de Neovim/Yazi en la terminal local.
- [ ] Medir carga de CPU, memoria y respuesta con tareas representativas antes
  de incorporar LSP, watchers, contenedores u otros servicios.
- [ ] Comparar alternativas cuando exista un problema medido; no asumir que una
  CLI o un terminal diferente es automáticamente más ligero.

Corregidos: suspensión inicial con tapa abierta, barra después de fullscreen y
rutas de cuenta `joe`→`jd`. Detalles técnicos en [CHANGELOG.md](CHANGELOG.md).
