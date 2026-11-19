# Technical TODO

## Priority 1 — Desktop workflow

- [x] Conservar Helium como navegador predeterminado y abrirlo directamente
  con Super+Shift+B o Super+Shift+Enter. [Keybindings](docs/keybindings.md).
- [x] Instalar Noto Color Emoji de Debian y verificar emoji a color en Helium
  sin cambiar las fuentes de texto/barra. [Browser emoji](docs/apps-setup.md#browser-emoji).
- [x] Añadir pestañas de Kitty en el directorio actual con Ctrl+Shift+T/Q y
  título de directorio; fuente y repintado conservados.
  [Kitty setup](docs/kitty-setup.md).
- [x] Recuperar el panel de redes abierto, añadirlo a Rofi y mostrar fallos
  del programa hijo sin confundirlos con una salida normal.
  [Network panel](docs/wifi-setup.md#network-panel).
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
- [x] Capturar región o escritorio en X11, con vista previa, edición opcional
  y guardado más copia sólo al aceptar. [Screen capture](docs/screen-capture.md).
- [ ] Implementar bloqueo por inactividad y previo a suspensión con i3lock,
  respetando logind e inhibidores. Revisar dependencias de avisos y coordinar
  las pruebas de [Hardware and session](#hardware-and-session).

## Priority 3 — Optional productivity tools

- [x] Habilitar completado nativo de Zsh con Tab y menú, sin plugins ni
  procesos adicionales. [Native completion](docs/kitty-setup.md#native-completion).
- [ ] Evaluar mejoras concretas de historial en Zsh sólo si hacen falta;
  conservar Bash para el inicio de i3 en tty1, SSH y recuperación.
  Historial y caches privados fuera del repositorio.
- [ ] Evaluar alias de shell para acciones repetidas identificadas; explicar
  su expansión, comprobar dependencias y no reemplazar comandos habituales
  ni añadir herramientas sin una utilidad concreta.
- [ ] Comparar arranque y redibujado del prompt nativo con el perfil Starship
  de Kitty en proyectos representativos, antes de ampliar sus módulos.
- [x] Usar Zathura como lector PDF predeterminado, con modo oscuro y copia de
  texto/enlaces. [PDF reader](docs/pdf-reader.md).
- [ ] Definir perfiles de desarrollo según proyectos concretos, con dependencias
  directas, instalación y recuperación documentadas, sin autostart de servicios.
- [x] Instalar el perfil nativo PHP 8.4/Composer/MariaDB/phpMyAdmin compatible
  con Laravel 13, con cuenta por esquema y servicios locales bajo demanda.
  [Laravel development](docs/laravel-setup.md).

## Publication and reproducibility

- [ ] Verificar arranque de Codex y conservación de la cuenta tras un reinicio
  local coordinado. [Codex CLI](docs/codex-setup.md).
- [ ] Comprobar desbloqueo del keyring tras el próximo login físico coordinado;
  autenticación HTTPS/push ya verificados. [Git workflow](docs/git-workflow.md).

- [ ] Probar restauración completa sobre una instalación limpia.
- [x] Unificar fuentes públicas y enlaces de usuario, retirar la copia secundaria
  y ejecutar scripts desde el repositorio.
  [User configuration links](docs/user-config-links.md).
- [ ] Agrupar fuentes heredadas sueltas de `config/` por componente; actualizar
  referencias/manifiesto y probar sin cambiar destinos a ciegas. Las nuevas
  herramientas ya usan carpetas propias.
- [x] Reconciliar las asociaciones MIME públicas y separar la base de Codex de
  su estado privado generado, sin importar credenciales ni rutas efímeras.

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
- [ ] Comprobar comodidad visual y uso diario de LazyVim/Yazi en Kitty y medir
  arranque, CPU y RAM en un proyecto real con una o dos pestañas de Helium.
- [ ] Si hace falta LSP, probar primero Python con un proyecto concreto; Java
  y web después, de uno en uno. No instalar runtimes ni auxiliares por anticipado.
- [ ] Comparar alternativas cuando exista un problema medido; no asumir que una
  CLI o un terminal diferente es automáticamente más ligero.

Corregidos: suspensión inicial con tapa abierta, barra después de fullscreen y
rutas de cuenta `joe`→`jd`. Detalles técnicos en [CHANGELOG.md](CHANGELOG.md).
