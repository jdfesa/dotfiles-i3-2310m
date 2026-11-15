# Changelog

Cambios de configuración y comprobaciones relevantes. El estado vigente está
en las guías; versiones de referencia en [dependencies.md](docs/dependencies.md).
No representa una reproducción byte a byte del sistema ni un benchmark.

## 2026-11-15

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

### Trackpad gestures

- Añadidos deslizamientos de tres dedos: izquierda al siguiente escritorio
  existente de la pantalla enfocada, derecha al anterior, al terminar el gesto.
  Auxiliar XInput 2.4 con bibliotecas existentes, selección por HID/driver y
  altas/bajas por eventos; sin paquetes nuevos, sondeo, permisos evdev ni servicio.
  Captura sólo swipes del Magic Trackpad 2; pinzas, clics, scroll y velocidad
  conservados. Instalación, pruebas y recuperación en
  [Trackpad gestures](docs/trackpad-gestures.md).
- Desplegados auxiliar, inicio i3 y ayuda con respaldo privado y comentarios
  locales conservados. Cambios reales de escritorio y controles habituales
  comprobados; 160 pruebas offline (una omitida), parser i3 y ciclo de inicio/
  parada correctos. Muestra breve de reposo y límites en la guía.

### Status bar and trackpad

- Retiradas las etiquetas CPU y RAM de la barra; se conservan los pictogramas,
  los valores y el clic del bloque CPU para btop.
- El clic en el trackpad alterna un panel GTK3 de velocidad para el Magic
  Trackpad 2 Bluetooth bajo el bloque, con el tema del calendario. Enter aplica
  y cierra; Escape o el segundo clic cierran sin aplicar. Validado el cambio y
  retorno al valor inicial en Xorg mediante xinput, sin cambiar el perfil ni
  agregar sondeo o servicios. El ajuste no
  se reaplica tras reconectar.

### Graphical tools

- Instalado Thunar sin recomendaciones de Xfce. Lanzador Rofi con Adwaita
  oscuro sólo para Thunar, comprobado en una ventana Xorg/i3; Yazi conserva
  su función en terminal. Sin cambio global de GTK ni nuevas asociaciones
  configuradas.
- Instalado Visual Studio Code estable bajo demanda desde el origen firmado de
  Microsoft, con pin limitado a `code`. CLI y archivo de prueba en Xorg/i3
  comprobados sin cambiar sandbox, editor predeterminado, extensiones o arranque.
  Instalación y recuperación
  en [Editor and file management](docs/editor-and-files.md#graphical-tools).

### Bluetooth

- Detectados CSR USB y Magic Trackpad 2; completados emparejamiento, confianza
  y conexión con BlueZ existente, sin instalar paquetes ni cambiar servicios.
  Verificados controlador nativo/libinput en Xorg y movimiento, clic izquierdo/
  derecho y scroll sin cable. Agente temporal cerrado, escaneo detenido y
  emparejamiento nuevo desactivado; guía de instalación/recuperación en
  [Bluetooth and Magic Trackpad 2](docs/bluetooth-setup.md), sin publicar claves
  ni identificadores privados.
- Añadidos iconos permanentes de adaptador Bluetooth y batería del trackpad.
  Lectura reutilizada de magic-trackpad-battery fijado, MIT; acceso hidraw por
  sesión local activa mediante regla limitada al hardware. BlueZ por libsystemd
  en el tick existente y batería en auxiliar breve cada 5 min, sin daemon/timer
  adicional. Cache en memoria, estados desconocidos/desactualizados y urgencia
  de batería baja; retirada USB real y porcentaje 99 % comprobados.

### Status panels

- Clic en el reloj abre/cierra calendario GTK3 con navegación de meses y Today;
  CPU abre/cierra btop en Kitty exclusivo, con refresco inicial de 2 s.
  Paneles flotantes bajo el bloque, acotados al monitor, por IPC y locks breves.
  Sin sondeo adicional ni cambios al tick/SIGSTOP/SIGCONT de i3bar.
- Declarados auxiliares, CSS y dependencias; GTK3 existente reutilizado con
  bindings de Debian. Verificados clics reales de barra, tres ciclos por panel,
  callbacks GTK, límites/identidades y cierre de btop sin procesos residuales.
  Despliegue con respaldo privado y diferencias locales conservadas; instalación,
  rollback y alcance de la muestra de coste en [Status panels](docs/status-panels.md).

### Kitty

- Añadida barra nativa superior con el nombre del directorio, visible con una
  pestaña. Ctrl+Shift+T abre otra en la carpeta activa; Ctrl+Shift+Q cierra la
  seleccionada. Ayuda y guía de atajos actualizadas; fuente 11 y repintado 20
  conservados, con colores Mocha en las pestañas.
- Paneles Wi-Fi/audio/APT/energía usan un override fijo de visibilidad para
  mantener su presentación compacta. Parser, bindings efectivos, plantillas
  y acciones nativas comprobados con Bash en una ventana aislada. Despliegue
  de seis archivos de usuario con respaldo privado y ajuste local preservado;
  instalación, comprobaciones y rollback en [Kitty setup](docs/kitty-setup.md).

### Status bar

- Incorporada Propo Regular de Nerd Fonts v3.5.1 como único TTF adicional,
  verificado por SHA256 y avisos oficiales conservados. Iconos de clima,
  métricas y audio a tamaño 12; texto Mono 10 y Wi-Fi BGH 12 conservados.
  Clima con sol/luna/nube sólidos, área de audio 24 y separación posterior 4.
  Verificados fontconfig, glifos y renderizado compacto/expandido sin recortes;
  instalación y recuperación actualizadas en [Status bar](docs/status-bar.md).
- Añadido chevrón para expandir/contraer tráfico, RAM, CPU, temperatura y disco.
  Inicio compacto; datos esenciales y bloques con urgencia explícita visibles.
  Redibujo de la última muestra en memoria, sin nuevos procesos, dependencias,
  sondeos ni estado persistente; tick de 10 s y SIGSTOP/SIGCONT conservados.
- Comprobados ambos estados en i3bar mediante clics X11 y tres ciclos de pausa/
  reanudación del grupo productor. Despliegue de adaptador/ayuda como jd con
  respaldo privado, contenidos y modos contrastados, conservando las ventanas.
  Pruebas de estado y ciclo de vida ampliadas; instalación y rollback en
  [Status bar](docs/status-bar.md).

### Documentation

- Fijado español para el cuerpo de la documentación, incluidos AGENTS.md y
  TODO.md; README principal, encabezados, navegación, nombres, interfaz y ayuda
  en inglés. Commits y PR íntegramente en inglés; identificadores técnicos intactos.
- Traducido el cuerpo de AGENTS.md conservando los contratos operativos y de
  seguridad; ajustadas las etiquetas documentales de TODO y las comprobaciones
  existentes que dependían del texto inglés.

### Planning

- Ampliado TODO con tareas de flujo cotidiano, sesión i3/Xorg y herramientas
  opcionales para el BGH. Conservados los pendientes anteriores.
- Documentado trabajo por prioridad/componente con revisión de dependencias,
  procesos y sondeos, y validación del rendimiento mediante mediciones locales.
  Sin instalaciones, despliegues ni cambios de la sesión.
- Establecido flujo habitual por ramas, commits modulares Conventional Commits
  y PR en inglés para revisión; integración sólo tras aprobación explícita.
  Actualizada la guía Git para evitar publicación directa en main y exigir
  fuentes/manifiesto, dependencias, instalación, validación y rollback reproducibles.

## 2026-11-02

### Productivity

- Actualizado Neovim a 0.12.6 estable oficial mediante archivo x86_64 con SHA256
  verificado, sin compilar ni cambiar Lua, MINI o Yazi. Prefijo versionado root
  en /opt; nvim y alternativas vi/vim/ex/view/vimdiff seleccionan la nueva copia,
  conservando modos y Debian como recuperación. Mantenimiento manual, no por APT;
  procedimiento y rollback en [Neovim installation](docs/neovim-installation.md).
- Zed descartado para la HD 3000: Vulkan sólo expone el renderizador CPU llvmpipe.
  Sin instalación, cambios de drivers o fallback forzado; criterio en AGENTS.md.
- Instalados Neovim Debian 0.10.4-8 y Yazi/Ya 26.9.1 desde APT oficial stable
  firmado, limitado al paquete yazi. Once paquetes nuevos, 18.3 MB de descarga
  y 69.6 MB de disco; sin recomendaciones, upgrades, compilación o servicios.
- Base Lua propia separada en opciones/atajos/autocomandos/MINI, colores Mocha
  nativos y sólo mini.files v0.18.0 fijado a commit y hashes. Sin proveedores de
  iconos, LSP ni descargas al inicio; preview desactivado y borrado a su papelera.
- Yazi abre texto con Neovim, conserva previews de texto/directorios y desactiva
  precargas/media. Configuración por herramienta bajo config/nvim y config/yazi;
  metadatos APT bajo config/yazi/apt. Organización heredada pendiente separada.
- Seis enlaces de usuario con dry-run, detección de conflictos y rollback
  privado; tres instalaciones APT regulares root:root644. 45/51 destinos
  coincidentes y seis diferencias anteriores preservadas.
- Añadidas regresiones de instalación/configuración, rollback, snapshot y
  TUI con fixtures aislados; arranque de la configuración instalada validado.
  [Guía de instalación, operación y recuperación](docs/editor-and-files.md).
  Uso visual local, rendimiento representativo y restauración limpia pendientes.
- Flujo versionado mediante GitHub y snapshot secundario generado desde el commit
  limpio; auxiliar con backup externo y comprobación exacta retira copias obsoletas
  y metadatos, sin acumular versiones paralelas. Estado de validación en la guía.
- Corregido modo664 heredado del checkout en las seis fuentes enlazadas: modo644
  verificado. Documentadas máscara022 y normalización acotada; Git no versiona
  esos bits. Añadida regresión que rechaza escritura de grupo en fuentes.
- Decisiones duraderas de herramientas, base Lua, extensiones, fuentes y permisos
  explicitadas en AGENTS.md; regresión documental separada del inventario de versiones.

### Development

- Añadido lanzador Codex bajo demanda, modo755, para recuperar el alias obsoleto
  de un socket temporal. Validación bajo lock, sockets activos preservados y
  paquetes oficiales separados; instalación y recuperación en
  [Codex CLI](docs/codex-setup.md).
- 12 regresiones del lanzador correctas en ambos sistemas. Documentadas la
  persistencia privada de autenticación y la verificación de cuenta efectiva
  tras recargar el backend, sin incorporar credenciales al proyecto.
- Documentada identidad pública Git con correo noreply, comprobación de autoría,
  recuperación y flujo manual commit/push/pull mediante GitHub. Autenticación y
  despliegue separados; sin incluir credenciales ni rutas de conexión.
- Identidad global de autor y committer verificada en Debian como cuenta de
  sesión; archivo Git privado modo600. HTTPS autenticado mediante gh y depósito
  Login cifrado; helper oficial, push desde Debian y pull desde otra copia
  comprobados. Desbloqueo tras próximo login físico todavía pendiente.
- Añadidos hooks opcionales PAM/Xsession y servicio sólo secrets como archivos
  root:root644, incluidos en el manifiesto. Deshabilitado el agente SSH extra de
  gcr4; conservado OpenSSH. Backups privados y checks de parser/servicio correctos.
- 66/66 pruebas offline correctas; 36/42 destinos coinciden completamente y
  se conservan las seis diferencias previas de configuración/documentación.
- Control obligatorio antes de cada push: exclusiones reales, archivos ya
  seguidos, allowlist/contenido del índice y commits salientes. Añadidas
  regresiones de publicación y exclusiones de depósitos privados.

## 2026-11-01

### Documentation

- Guías temáticas y avisos de terceros trasladados a `docs/`; enlaces e
  inventario actualizados y árbol resumido en README. Regresión de estructura
  añadida: 60/60 pruebas locales.
- Reorganizadas guías como objetivo, instalación, operación, validación y
  recuperación; eliminadas narración, datos de conexión locales y referencias
  temporales ambiguas.
- Centralizado inventario de dependencias y documentado el ciclo de vida de
  scripts/servicios. README de presentación/navegación para el hardware objetivo;
  criterios de trabajo en AGENTS.md y pendientes en TODO.md.
- README principal en inglés; encabezados de guías en inglés y contenido en
  español. Nombres propios multi-palabra en kebab-case, con excepciones de
  herramientas, proveedores y módulos de pruebas Python.
- Añadida licencia MIT para código/documentación propios; componentes externos
  conservan sus licencias. Restauración automática y symlinks siguen pendientes.
- Añadidas siete regresiones de documentación: portada, estilo técnico, datos
  de entorno, enlaces, inventario, licencias y nomenclatura. 59/59 tests
  locales correctos; la última ejecución Debian anterior tenía 52/52.
- Esta revisión documental no modifica opciones funcionales de la sesión;
  sincronización y estado de verificación en `docs/mirror-status.md`.

### Changed

- Cuenta/grupo/home `joe`→`jd` conservando UID/GID 1000 y grupos. Reparados
  cinco enlaces absolutos Codex/timers y prefijos de configuración administrada;
  preferencias de aplicaciones preservadas. Recuperación: `docs/user-migration.md`.
- Power menu: Power off primero, Yes preseleccionado en todas las confirmaciones.
  Acciones como cuenta local mediante logind/Polkit, sin sudo ni contraseña;
  se conservan inhibidores, `--no-ask-password` y guardia systemd >=257.
- Añadido `polkitd 126-2` desde Debian sin recomendaciones ni reglas locales.
  Comprobaciones de capacidad y dry-run correctas en sesión física; un inhibidor
  block temporal rechazó apagar/reiniciar/suspender. Sin acciones reales.
- `--preview` recorre menú y confirmación sin ejecutar acciones.

### Fixed

- Suspensión inicial con tapa abierta: drop-in GRUB añade
  `button.lid_init_state=open` conservando opciones existentes. Validaciones
  shell/GRUB y pruebas de reinicio/encendido correctas; eventos posteriores de
  tapa aún pendientes.
- Barra al salir de fullscreen: retiradas señales USR1/USR2 personalizadas.
  i3bar señaliza el grupo completo y podía terminar el shell launcher; se usan
  SIGSTOP/SIGCONT predeterminados. Regresión de procesos y ciclos nativos/GUI
  correctos, sin cambiar estilo o intervalos.

### Known limitations

- Wi-Fi en frío requiere Fn+F11 integrado. Captura temporal identificó
  soft unblocked/hard blocked; retirada después del diagnóstico. Captura filtrada
  de teclado/radio no proporcionó un método simple de activación por script.
- Divergencias mimeapps/Codex preservadas; no sobrescritas para forzar el espejo.

## 2026-10-29

### Added

- Codex CLI 0.165.0 standalone; ejecución, acceso al modelo y sandbox de sólo
  lectura comprobados. Sin Node/npm ni servicio de arranque.
- RTK 1.1.0 y Engram 3.6.0 oficiales; plugin 0.1.5 fijado a v3.6.0.
  Hook RTK nativo, telemetría desactivada y helper Engram sólo loopback.
- Git/curl/jq desde Debian. Sin compilación de toolchains ni importación de
  memorias, sesiones o directorios privados completos.

## 2026-10-12

### Added

- Sesión mínima Xorg/i3 tras login físico tty1, recuperación tty2/SSH y
  `disable-autostart`. Sin display manager, autologin ni compositor.
- NetworkManager como único gestor de interfaces físicas y DNS; loopback en
  ifupdown. Eliminado conflicto dhcpcd/resolv.conf al retirar Ethernet.
- Kitty/Rofi de Debian y Helium desde su APT oficial firmado; GPU acelerada y
  ventanas reales comprobadas, sandbox conservado.
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
