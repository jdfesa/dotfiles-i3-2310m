# Changelog

Cambios de configuración y comprobaciones relevantes. El estado vigente está
en las guías; versiones de referencia en [dependencies.md](docs/dependencies.md).
No representa una reproducción byte a byte del sistema ni un benchmark.

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
