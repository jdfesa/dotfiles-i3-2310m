# Changelog

Cambios técnicos de la configuración. El estado vigente está en las guías y
las versiones en [Dependencies and versions](docs/dependencies.md).

## 2026-11-16

### Configuration sources

- Retirado el generador de la copia secundaria: el checkout y GitHub conservan
  las fuentes públicas, sin exportar otro árbol de configuración.


### Thunar dark theme

- La activación D-Bus de Thunar desde el navegador aplica `Adwaita:dark`
  mediante un drop-in del servicio de usuario existente. Se conserva el
  lanzador oscuro, sin cambiar el tema GTK global ni las asociaciones MIME.
  [Thunar](docs/editor-and-files.md#thunar).

### USB audio adapter

- El perfil de audio pasa al GeneralPlus `1b3f:2008` con `Speaker`, índice0,
  sustituyendo al USB `8086:0808`. Se conserva el controlador ALSA existente,
  con rango de volumen nativo, sin dependencias ni sondeos nuevos.
  [USB audio](docs/audio-setup.md).
- Añadido `refresh-helium-audio.py` para recuperar la reproducción tras cambiar
  el USB con Helium abierto: revisión sin señales por defecto y renovación
  explícita sólo de AudioService mediante pidfd, USB/identidad revalidados y
  captura cerrada. Sin cerrar pestañas ni añadir automatización de hotplug.

### Desktop wallpaper

- Fondo Pixel Car versionado en `wallpapers/` y aplicado al inicio de i3 con
  xwallpaper, sin daemon. [Wallpaper](docs/i3-setup.md#wallpaper).

### LazyVim

- LazyVim estable pasa a ser el perfil predeterminado de Neovim 0.12; usa el
  catálogo base de plugins fijado y Tree-sitter, sin extras ni instalación
  automática de servidores de lenguaje. Se conservan Yazi, alternativas y
  recuperación del perfil anterior. [LazyVim setup](docs/lazyvim-setup.md).

### Screen brightness

- Añadido el indicador de brillo del panel interno y un deslizador GTK3
  anclado a la barra. Usa los pasos físicos de la retroiluminación ACPI mediante
  logind y el tick de barra existente. [Screen brightness](docs/status-bar.md#screen-brightness).
- El inicio de una sesión i3 fija el brillo del panel interno en 43 %; no se
  reaplica al recargar o reiniciar i3 dentro de la sesión.

### Network panel

- Reabrir el panel de redes enfoca la instancia existente. El lanzador Rofi
  ofrece **Wi-Fi Networks** sin cambiar el clic de la barra ni Super+N.
- Una salida anormal de `nmtui-connect` muestra el estado en Kitty hasta
  pulsar Enter; una salida normal cierra el panel.
  [Network panel](docs/wifi-setup.md#network-panel).

### PDF reader

- Zathura con Poppler es el lector predeterminado para PDF. Usa Mocha en
  interfaz y páginas, sin alternar el recolor con Ctrl+R.
- La selección de texto y la copia de enlaces usan el portapapeles estándar.
  Helium conserva las asociaciones web; Yazi mantiene sus vistas previas.
  [PDF reader](docs/pdf-reader.md).

### Browser emoji

- Instalado únicamente Noto Color Emoji desde Debian estable. Se reutiliza el
  fallback de Fontconfig; no cambian las fuentes de texto ni de barra ni se
  añaden servicios. Instalación y reversión en
  [Browser emoji](docs/apps-setup.md#browser-emoji).

## 2026-11-15

### Battery icons

- Sustituida la leyenda No battery por una batería tachada. Estados nativos
  separados para carga con rayo, descarga/nivel, completa con marca, reposo
  con pausa y desconocido con interrogación; porcentaje sólo si es válido.
  Iconos de la fuente existente, sin procesos, dependencias o sondeos nuevos.
- Conservados el umbral, las urgencias nativas y el tick de 10 s.
  [Battery icons](docs/status-bar.md#battery-icons).

### USB audio volume

- Sustituida la detección de audio sólo al arrancar y el mixer fijo Master por
  lectura ALSA de Speaker del USB identificado, en el tick existente de 10 s.
  Icono y porcentaje reales; ausencia y error diferenciados, sin procesos por
  muestra ni servidores de audio nuevos.
- Clic en audio o Super+A alterna un deslizador GTK3 bajo el bloque, con el tema
  del calendario. Volumen de salida y mute explícitos, sin cambiar micrófono,
  captura o ganancia automática. Identidad/driver y generación de tarjeta
  revalidados antes de escribir; apertura/conexión sin escrituras. Procedimiento
  y recuperación en [USB audio](docs/audio-setup.md).
- Super+A sitúa el panel bajo el mismo bloque de audio que el clic, desde la
  muestra visible guardada en memoria X11 y medición Pango bajo demanda. Sin
  sondeo, archivos de estado ni carga de GTK/Pango en el productor de barra.
  El perfil USB permite cambiar de puerto/hub sin fijar el índice de tarjeta.

### Trackpad gestures

- Añadidos deslizamientos de tres dedos: izquierda al siguiente escritorio
  existente de la pantalla enfocada, derecha al anterior, al terminar el gesto.
  Auxiliar XInput 2.4 con bibliotecas existentes, selección por HID/driver y
  altas/bajas por eventos; sin paquetes nuevos, sondeo, permisos evdev ni servicio.
  Captura sólo swipes del Magic Trackpad 2; pinzas, clics, scroll y velocidad
  conservados. Instalación, pruebas y recuperación en
  [Trackpad gestures](docs/trackpad-gestures.md).

### Status bar and trackpad

- Retiradas las etiquetas CPU y RAM de la barra; se conservan los pictogramas,
  los valores y el clic del bloque CPU para btop.
- El clic en el trackpad alterna un panel GTK3 de velocidad para el Magic
  Trackpad 2 Bluetooth bajo el bloque, con el tema del calendario. Enter aplica
  y cierra; Escape o el segundo clic cierran sin aplicar. El ajuste no cambia
  el perfil de aceleración ni se reaplica tras reconectar.

### Graphical tools

- Añadido Thunar sin recomendaciones de Xfce y con un lanzador de tema Adwaita
  oscuro. No cambia el tema GTK global ni las asociaciones MIME.
- Añadido Visual Studio Code estable bajo demanda desde el repositorio firmado
  de Microsoft, limitado a `code`, sin autostart ni cambio de editor
  predeterminado. [Editor and file management](docs/editor-and-files.md#graphical-tools).

### Bluetooth

- Configurado Magic Trackpad 2 por Bluetooth con BlueZ y libinput existentes
  en Xorg. [Bluetooth and Magic Trackpad 2](docs/bluetooth-setup.md).
- Añadidos iconos permanentes de adaptador Bluetooth y batería del trackpad.
  Lectura reutilizada de magic-trackpad-battery fijado, MIT; acceso hidraw por
  sesión local activa mediante regla limitada al hardware. BlueZ por libsystemd
  en el tick existente y batería en auxiliar breve cada 5 min, sin daemon/timer
  adicional. Caché en memoria, estados desconocidos/desactualizados y urgencia
  de batería baja.

### Status panels

- Clic en el reloj abre/cierra calendario GTK3 con navegación de meses y Today;
  CPU abre/cierra btop en Kitty exclusivo, con refresco inicial de 2 s.
  Paneles flotantes bajo el bloque, acotados al monitor, por IPC y locks breves.
  Sin sondeo adicional ni cambios al tick/SIGSTOP/SIGCONT de i3bar.
- Añadidos los auxiliares y el CSS del calendario, con GTK3 de Debian.
  [Status panels](docs/status-panels.md).

### Kitty

- Añadida barra nativa superior con el nombre del directorio, visible con una
  pestaña. Ctrl+Shift+T abre otra en la carpeta activa; Ctrl+Shift+Q cierra la
  seleccionada. Ayuda y guía de atajos actualizadas; fuente 11 y repintado 20
  conservados, con colores Mocha en las pestañas.
- Los paneles Wi-Fi/audio/APT/energía mantienen la presentación compacta con
  un override de visibilidad. [Kitty setup](docs/kitty-setup.md).

### Status bar

- Añadida Propo Regular para iconos de clima, métricas y audio a tamaño 12.
  Se conservan texto Mono 10 y Wi-Fi BGH 12. Clima con sol/luna/nube sólidos,
  área de audio 24 y separación posterior 4. [Status bar](docs/status-bar.md).
- Añadido chevrón para expandir/contraer tráfico, RAM, CPU, temperatura y disco.
  Inicio compacto; datos esenciales y bloques con urgencia explícita visibles.
  Redibujo de la última muestra en memoria, sin nuevos procesos, dependencias,
  sondeos ni estado persistente; tick de 10 s y SIGSTOP/SIGCONT conservados.

### Documentation

- Fijado español para el cuerpo de la documentación, incluidos AGENTS.md y
  TODO.md; README principal, encabezados, navegación, nombres, interfaz y ayuda
  en inglés. Commits y PR íntegramente en inglés; identificadores técnicos intactos.

## 2026-11-02

### Productivity

- Actualizado Neovim a 0.12.6 estable oficial mediante archivo x86_64 con SHA256
  verificado, sin compilar ni cambiar Lua, MINI o Yazi. Prefijo versionado root
  en /opt; nvim y alternativas vi/vim/ex/view/vimdiff seleccionan la nueva copia,
  conservando modos y Debian como recuperación. Mantenimiento manual, no por APT;
  procedimiento y rollback en [Neovim installation](docs/neovim-installation.md).
- Instalado Neovim de Debian y añadido Yazi/Ya desde su repositorio APT stable
  firmado, limitado a `yazi`. Sin recomendaciones ni servicios de inicio.
- Base Lua propia separada en opciones/atajos/autocomandos/MINI, colores Mocha
  nativos y sólo mini.files v0.18.0 fijado a commit y hashes. Sin proveedores de
  iconos, LSP ni descargas al inicio; preview desactivado y borrado a su papelera.
- Yazi abre texto con Neovim, conserva previews de texto/directorios y desactiva
  precargas/media. Configuración por herramienta bajo config/nvim y config/yazi;
  metadatos APT bajo config/yazi/apt.
- Añadidos seis enlaces de usuario con dry-run, detección de conflictos y
  rollback; los tres archivos de APT se instalan como archivos regulares
  root:root, modo 644. [Editor and file management](docs/editor-and-files.md).
- Añadido un auxiliar para generar el snapshot secundario desde el commit;
  retira archivos obsoletos, respalda cambios y comprueba contenidos y modos.
- Corregido de 664 a 644 el modo de las seis fuentes enlazadas.

### Development

- Añadido lanzador Codex bajo demanda, modo755, para recuperar el alias obsoleto
  de un socket temporal. Validación bajo lock, sockets activos preservados y
  paquetes oficiales separados; instalación y recuperación en
  [Codex CLI](docs/codex-setup.md).
- Git usa el helper de gh para HTTPS y el depósito Login cifrado, con correo
  noreply para autoría. [Git workflow](docs/git-workflow.md).
- Añadidos hooks opcionales PAM/Xsession y servicio sólo secrets como archivos
  root:root644, incluidos en el manifiesto. Deshabilitado el agente SSH extra de
  gcr4; conservado OpenSSH.
- Añadidas comprobaciones de exclusiones de archivos privados y de publicación.

## 2026-11-01

### Documentation

- Trasladadas las guías temáticas y los avisos de terceros a `docs/`.
  Las guías separan instalación, operación, comprobación y recuperación.
- Centralizado inventario de dependencias y documentado el ciclo de vida de
  scripts/servicios. README de presentación/navegación para el hardware objetivo;
  criterios de trabajo en AGENTS.md y pendientes en TODO.md.
- README principal en inglés; encabezados de guías en inglés y contenido en
  español. Nombres propios multi-palabra en kebab-case, con excepciones de
  herramientas, proveedores y módulos de pruebas Python.
- Añadida licencia MIT para código y documentación propios; los componentes
  externos conservan sus licencias.
- Añadidas pruebas de estructura documental, enlaces, inventario y licencias.

### Changed

- Cuenta/grupo/home `joe`→`jd` conservando UID/GID 1000 y grupos. Reparados
  cinco enlaces absolutos Codex/timers y prefijos de configuración administrada;
  preferencias de aplicaciones preservadas. Recuperación: `docs/user-migration.md`.
- Power menu: Power off primero, Yes preseleccionado en todas las confirmaciones.
  Acciones como cuenta local mediante logind/Polkit, sin sudo ni contraseña;
  se conservan inhibidores, `--no-ask-password` y guardia systemd >=257.
- Añadido `polkitd` desde Debian sin recomendaciones ni reglas locales.
  `--preview` recorre menú y confirmación sin ejecutar acciones.

### Fixed

- Suspensión inicial con tapa abierta: drop-in GRUB añade
  `button.lid_init_state=open` conservando las demás opciones.
- Barra al salir de fullscreen: retiradas señales USR1/USR2 personalizadas.
  i3bar señaliza el grupo completo y podía terminar el shell launcher; se usan
  SIGSTOP/SIGCONT predeterminados, sin cambiar estilo o intervalos.

## 2026-10-29

### Added

- Añadido Codex CLI 0.165.0 standalone, sin Node/npm ni servicio de arranque.
- RTK 1.1.0 y Engram 3.6.0 oficiales; plugin 0.1.5 fijado a v3.6.0.
  Hook RTK nativo, telemetría desactivada y helper Engram sólo loopback.
- Añadidos Git, curl y jq desde Debian.

## 2026-10-12

### Added

- Sesión mínima Xorg/i3 tras login físico tty1, recuperación tty2/SSH y
  `disable-autostart`. Sin display manager, autologin ni compositor.
- NetworkManager como único gestor de interfaces físicas y DNS; loopback en
  ifupdown. Eliminado conflicto dhcpcd/resolv.conf al retirar Ethernet.
- Añadidos Kitty y Rofi desde Debian, y Helium desde su repositorio APT firmado
  con sandbox activo.
- JetBrains Mono Nerd Font Mono Regular/Bold, barra Mocha superior Regular 10.
  Refresco nativo 10 s, clima cacheado 30 min y contador APT local 6 h.
- Helpers bajo demanda para redes/audio/paquetes/energía, con ayuda inglesa.

### Fixed

- Iconos tras instalar fuentes: fc-cache y reinicio de i3bar conservando ventanas.
- Modificador Alt expresado como `Mod1`; el parser por sí solo no detectaba el
  fallo del binding en ejecución.
- Flujo histórico sudo del menú: `check-inhibitors=auto` en systemd >=257 evitó
  confundir la propia tty1 con otra cuenta, manteniendo inhibidores block.
  Sustituido por autorización local sin sudo el 2026-11-01.
