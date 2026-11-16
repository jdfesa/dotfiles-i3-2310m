# Technical TODO

## Priority 1 — Desktop workflow

- [x] Conservar Helium como navegador predeterminado y abrirlo directamente
  con Super+Shift+B o Super+Shift+Enter. [Keybindings](docs/keybindings.md).
- [x] Instalar Noto Color Emoji de Debian y verificar emoji a color en Helium
  sin cambiar las fuentes de texto/barra. [Browser emoji](docs/apps-setup.md#browser-emoji).
- [x] Añadir pestañas de Kitty en el directorio actual con Ctrl+Shift+T/Q y
  título de directorio; fuente y repintado conservados.
  [Kitty setup](docs/kitty-setup.md).
- [ ] Mejorar el panel de redes: enfocar la instancia abierta, acceso desde el
  lanzador y distinguir cancelación de fallos del proceso hijo de Kitty.
  Mantener NetworkManager y consultas sólo bajo demanda.
- [ ] Reunir las comprobaciones de estructura, enlaces documentales, exclusiones
  e historial en una validación manual, reutilizando pruebas existentes y
  [Publication checks](docs/git-workflow.md#publication-checks).

## Priority 2 — Session and status bar

- [x] Añadir métricas contraíbles con redibujo desde memoria, datos esenciales,
  urgencias explícitas, tick de 10 s y SIGSTOP/SIGCONT conservados.
  [Status bar](docs/status-bar.md#collapsible-metrics).
- [x] Abrir/cerrar btop identificado al pulsar CPU, bajo demanda y con una
  muestra acotada de coste. [Status panels](docs/status-panels.md).
- [x] Consultar un calendario GTK3 al pulsar el reloj, reutilizando la biblioteca
  existente y con sus bindings declarados. [Status panels](docs/status-panels.md).
- [ ] Con la batería instalada, comprobar nivel, carga, descarga, reposo y
  completa reales. Los [Battery icons](docs/status-bar.md#battery-icons) se
  validaron con datos simulados; evaluar detalles bajo demanda sólo si hacen
  falta, distinguiendo carga, salud y ausencia sin más consultas periódicas.
- [ ] Tras verificar hardware y permisos, añadir controles puntuales de brillo;
  evaluar un deslizador sólo si aporta utilidad frente a teclas o rueda.
- [ ] Si hacen falta varias distribuciones, añadir selector XKB para Xorg
  que refleje el estado real por eventos, sin polling.
- [ ] Añadir captura de región al portapapeles con herramientas X11 bajo demanda,
  sin archivos persistentes automáticos ni historial del portapapeles.
- [ ] Implementar bloqueo por inactividad y previo a suspensión con i3lock,
  respetando logind e inhibidores. Revisar dependencias de avisos y coordinar
  las pruebas de [Hardware and session](#hardware-and-session).

## Priority 3 — Optional productivity tools

- [ ] Evaluar mejoras concretas de historial y completado antes de cambiar shell;
  conservar inicio autenticado de i3 en tty1, SSH y recuperación.
  Historial y caches privados fuera del repositorio.
- [ ] Comparar prompt nativo con Starship mínimo; medir arranque y repintado
  en proyectos representativos antes de añadir módulos Git o de lenguajes.
- [x] Añadir Zathura bajo demanda con modo oscuro y copia de texto/enlaces,
  sin cambiar las vistas previas de Yazi. [PDF reader](docs/pdf-reader.md).
- [ ] Definir perfiles de desarrollo según proyectos concretos, con dependencias
  directas, instalación y recuperación documentadas, sin autostart de servicios.

## Publication and reproducibility

- [ ] Verificar arranque de Codex y conservación de la cuenta tras un reinicio
  local coordinado. [Codex CLI](docs/codex-setup.md).
- [ ] Comprobar desbloqueo del keyring tras el próximo login físico coordinado;
  autenticación HTTPS/push ya verificados. [Git workflow](docs/git-workflow.md).

- [ ] Probar restauración completa sobre una instalación limpia.
- [ ] Ampliar la migración de enlaces a componentes anteriores tras revisar
  diferencias; el auxiliar con dry-run/backup/rollback sólo gestiona los seis
  archivos nuevos de [Editor and file management](docs/editor-and-files.md).
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
- [x] Verificar adaptador USB, salida Speaker, reproducción y volumen/mute;
  conexión en otros puertos y hub. [USB audio](docs/audio-setup.md).
- [ ] Revisar brillo y pila RTC.
- [ ] Coordinar prueba física de apagar/reiniciar/suspender/reanudar; dry-run no
  equivale a comprobar esas acciones.

## Productivity and resources

- [x] Instalar Neovim/Yazi y base Lua modular con sólo mini.files.
  [Editor and file management](docs/editor-and-files.md).
- [ ] Seleccionar herramientas/stacks adicionales según proyectos concretos.
- [ ] Comprobar comodidad visual y uso diario de Neovim/Yazi en la terminal local.
- [ ] Medir carga de CPU, memoria y respuesta con tareas representativas antes
  de incorporar LSP, watchers, contenedores u otros servicios.
- [ ] Comparar alternativas cuando exista un problema medido; no asumir que una
  CLI o un terminal diferente es automáticamente más ligero.

Corregidos: suspensión inicial con tapa abierta, barra después de fullscreen y
rutas de cuenta `joe`→`jd`. Detalles técnicos en [CHANGELOG.md](CHANGELOG.md).
