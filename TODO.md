# Technical TODO

## Dotfiles adaptation plan

Comparación de fuentes realizada el 2026-11-15 con la copia local de
`dotfiles-i5-5257u` en la carpeta `github`, revisión `a85e710` (MacBookPro12,1,
Debian 13, Sway). Las rutas `Reference:` siguientes pertenecen a ese repositorio;
los enlaces apuntan a este proyecto. No se comprobó su despliegue en la MacBook
ni su funcionamiento en el BGH. Este inventario no instala ni activa candidatos.

### Working method

1. Trabajar una prioridad y un componente por vez; revisar primero fuentes y
   destinos reales del BGH, conservando las diferencias existentes.
2. Elegir la función útil, adaptar a Xorg/i3 y revisar dependencias directas,
   procesos residentes, frecuencia de consultas y coste al abrir/usar/cerrar.
   Preferir reutilizar lo instalado; simular paquetes antes de instalar.
3. Editar fuentes locales por componente y actualizar manifiesto, guía y ayuda.
   Desplegar con backup privado externo, dry-run y rollback; archivos de sistema
   regulares root, sin enlaces al home.
4. Validar sintaxis y comportamiento por separado en el BGH, preservando ventanas,
   tty de recuperación y SSH. Coordinar pruebas de bloqueo, energía y red.
5. Medir CPU, memoria y respuesta con la misma carga y navegador abierto antes
   de atribuir mejoras. Las mediciones de la MacBook no se extrapolan.
6. Usar rama de trabajo por bloque y commits modulares Conventional Commits en
   inglés. Cerrar cada tarea con resultado, límites y recuperación en su guía/
   CHANGELOG; marcarla aquí. Tras revisar la publicación, preparar PR para
   aprobación antes de integrar. Aplicar [AGENTS.md](AGENTS.md) y
   [Git workflow](docs/git-workflow.md); la autorización habitual cubre rama,
   commits y PR del trabajo solicitado.

### Shared baseline

Ya existen Kitty opaco/Mocha, atajos principales, scratchpad, menús de red y
energía, autorización de sesión y caches de clima/APT con tick de barra de 10 s.
Conservarlos como base; comparar diferencias puntuales, sin reemplazar el perfil.
Yazi ya está instalado; Neovim/mini.files es la solución local para edición.

### Priority 0 — Baseline and prerequisites

- [ ] Registrar la línea base de CPU, memoria y respuesta descrita en
  [Productivity and resources](#productivity-and-resources), con navegación,
  terminal, edición y archivos representativos; repetirla por cambio relevante.
- [ ] Revisar diferencias entre fuentes y destinos antes del primer despliegue,
  usando `config/manifest.json` y `tools/verify-mirror.py`. La agrupación de
  fuentes y ampliación de enlaces siguen en
  [Publication and reproducibility](#publication-and-reproducibility).
- [ ] Identificar necesidades reales de distribución de teclado y controles de
  brillo; comprobar dispositivos/permisos sin alterar la sesión. Los gestos
  quedan fuera del alcance; no se ha verificado soporte multidedo del touchpad.

### Priority 1 — Everyday workflow

- [ ] **Navegador XDG:** adaptar Super+Shift+B, hoy fijado a Helium, para resolver
  el navegador predeterminado. Decidir antes qué hacer con Super+Shift+Enter;
  actualizar [i3 config](config/i3-config), ayuda y [Keybindings](docs/keybindings.md).
  Reference: `scripts/sway-tools.sh` (`browser`), `docs/keybindings.md`.
- [ ] **Pestañas de Kitty:** evaluar Ctrl+Shift+T en la carpeta actual y título
  con el nombre del directorio. Conservar tamaño de fuente, opacidad y ajustes
  locales de repintado; no importar Zsh ni forzar una barra con una sola pestaña.
  Reference: `config/kitty/kitty.conf`; local: [Kitty config](config/kitty.conf).
- [ ] **Panel de redes:** comparar apertura única con foco de la ventana ya
  abierta, acceso desde el lanzador y mensajes de fallo/cancelación. Revisar el
  protocolo de salida del hijo de Kitty y si hace falta escaneo al abrir;
  sin nuevos sondeos ni recuperación de drivers de la MacBook.
  Reference: `scripts/open-networks.sh`, `config/network/mbp-networks.desktop`;
  local: [Network helper](scripts/open-networks.sh).
- [ ] **Validación del repositorio:** evaluar las comprobaciones de estructura,
  enlaces documentales, exclusiones reales e historial de
  `tools/check-repository.py`, reutilizando las pruebas locales y
  [Publication checks](docs/git-workflow.md#publication-checks). Ejecución manual,
  sin watchers ni sustituir la revisión del índice/commits salientes.

### Priority 2 — i3 and Xorg adaptations

- [ ] **Barra contraíble:** estudiar sólo la vista compacta/expandida sobre
  [Status adapter](scripts/status-clicks.py), manteniendo datos esenciales y
  bloques urgentes. Redibujar la muestra en memoria, conservar tick de 10 s y
  SIGSTOP/SIGCONT; ocultar métricas no demuestra menor consumo de CPU.
  Reference: `scripts/status-adapter.py` (`StatusView`), `docs/status-bar.md`.
- [ ] **Monitor bajo demanda:** evaluar clic en CPU para abrir/cerrar únicamente
  su terminal identificada. Comparar las herramientas disponibles antes de
  añadir btop; medir también mientras el monitor esté abierto.
  Reference: `scripts/sway-tools.sh` (`resource-monitor`).
- [ ] **Calendario:** comparar una consulta sencilla en terminal con reutilizar
  `scripts/calendar-popup.py` y `config/calendar/calendar.css` (GTK3).
  Si se elige ventana, adaptar reglas/identidad a X11 y finalizar al cerrar;
  no trasladar `sway-panel-anchor.py` ni agregar un proceso permanente.
- [ ] **Batería:** verificar primero los datos reales del BGH y el bloque nativo
  i3status. Evaluar presentación de estados y detalles a demanda sin confundir
  carga con salud, sin inventar porcentajes ni introducir UPower sólo para
  copiar el backend de Apple. Reference: `scripts/battery-details-popup.py`,
  `scripts/status-adapter.py` (`format_battery`).
- [ ] **Brillo:** completar la comprobación de hardware de
  [Hardware and session](#hardware-and-session) antes de añadir teclas o rueda.
  Empezar por acciones puntuales; evaluar el deslizador GTK sólo si aporta utilidad.
  No copiar `intel_backlight`, teclas F1/F2 ni nivel inicial de la MacBook a ciegas.
  Reference: `scripts/screen-brightness-popup.py`, `scripts/sway-tools.sh`.
- [ ] **Selector de teclado:** sólo si se necesitan varias distribuciones,
  diseñar equivalente XKB para Xorg. No copiar US/ES como preferencia ni usar
  eventos de entrada de Sway; reflejar estado real por eventos, sin polling.
  Reference: `config/sway/config`, `scripts/status-adapter.py` (`KeyboardLayout`).
- [ ] **Capturas:** evaluar selección al portapapeles con herramientas X11 bajo
  demanda, sin archivos persistentes automáticos ni gestor de historial.
  Reference: `scripts/sway-tools.sh` (`screenshot`: grim/slurp/wl-copy en Wayland).
- [ ] **Bloqueo e inactividad:** diseñar equivalente X11 de
  `config/swayidle/config`, conservando i3lock, inhibidores y logind. Revisar
  si hacen falta avisos y su servicio X11 antes de añadirlo; Mako no se copia.
  Completar con pruebas locales coordinadas el pendiente de tapa/suspensión de
  [Hardware and session](#hardware-and-session), sin apagar por tapa automáticamente.

### Priority 3 — Optional tools after measurement

- [ ] **Shell:** evaluar qué aportan historial/completado de `config/zsh/zshrc`
  frente a la shell actual. No cambiar la shell de la cuenta por defecto;
  conservar inicio autenticado de i3 en tty1, SSH y recuperación, aunque cambien
  los archivos de login. Historial y caches privados, fuera del repositorio.
- [ ] **Prompt:** evaluar por separado el prompt nativo y Starship mínimo;
  medir arranque y repintado en repositorios representativos. No copiar `$all`
  ni módulos Git/lenguajes sin necesidad: los timeouts por comando no limitan
  el coste total del prompt. Reference: `config/starship/starship.toml`,
  `docs/starship-setup.md`; no extrapolar sus mediciones del i5 al i3.
- [ ] **PDF:** evaluar Zathura bajo demanda para lectura, colores y copia de
  texto/enlaces. Mantener previews de Yazi limitados a texto/directorios y
  precargas desactivadas; imágenes/PDF previews requieren una revisión de
  recursos separada. No copiar dimensiones HiDPI ni `swaymsg` del opener.
  Reference: `config/zathura/zathurarc`, `config/yazi/yazi.toml`.
- [ ] **Desarrollo:** seleccionar Node/PHP/Composer u otros entornos sólo para
  proyectos concretos, como perfiles opcionales sin autostart. Comparar sus
  dependencias antes de adoptar XAMPP completo. Reference: `docs/optional-profiles.md`,
  `tools/restore-profile.py`; mantener Neovim y la selección local de Yazi.

### Excluded and deferred

- **Sesión Wayland:** Sway, Fuzzel, Foot, Mako, swaylock/swayidle,
  grim/slurp/wl-clipboard y portales Wayland no se incorporan como reemplazos
  directos. Se conserva i3/Xorg, Rofi, Kitty e inicio tty1 sin display manager.
- **Hardware Apple:** gestos de tres/cuatro dedos, retroiluminación del teclado,
  firmware/recuperación Broadcom, escala 2 y políticas del SSD USB no se trasladan.
  No instalar un daemon de gestos para intentar emularlos.
- **Perfiles ajenos al alcance:** LightDM/XFCE, hotspot, reglas SSH y apagado
  automático por tapa/RTC requieren una necesidad y alcance propios. No importar
  manifiestos, lista de paquetes, políticas de energía ni estado privado en bloque.
- **Zed:** permanece descartado por falta de Vulkan de hardware en Intel HD 3000,
  según [AGENTS.md](AGENTS.md); sin renderizado CPU como solución alternativa.
- **Ideas aún pendientes en la referencia:** selector de ventanas, marcadores y
  overview/woverview no son funciones verificadas para importar; reconsiderar
  equivalentes bajo demanda sólo ante una necesidad concreta de i3.

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
