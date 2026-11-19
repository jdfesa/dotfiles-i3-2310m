# Agent instructions — Debian laptop configuration

## Scope and documentation

- GitHub es la fuente de verdad de la configuración gestionada y versionada del
  BGH A470; cada máquina mantiene una copia de trabajo, no un espejo completo del
  home o de /etc. El destino es i3-2310M/Sandy Bridge de 2011, Debian 13 amd64,
  8 GB de RAM y SSD SATA de 120 GB.
- Las guías temáticas y avisos de terceros van en docs/. Mantener README.md,
  AGENTS.md, CHANGELOG.md, TODO.md y LICENSE en la raíz; los README de componentes
  permanecen junto a sus fuentes. Salvo indicación contraria, ejecutar los ejemplos
  desde la raíz del repositorio.
- Las guías documentan el estado actual, el origen de las dependencias,
  instalación, comprobaciones y recuperación. CHANGELOG.md resume sólo qué
  cambió técnicamente, sin relatos de sesiones, despliegues ni resultados de
  pruebas. TODO.md registra pendientes. No narrar chats, publicar historiales
  personales de cuentas ni convertir las guías en diarios de diagnóstico.
- Mantener planes y guías autocontenidos: documentar tareas, comportamiento y
  requisitos de este proyecto. La investigación de implementación no forma parte
  del inventario publicado.
- Registrar las decisiones duraderas que afecten el trabajo en este archivo.
  Dejar versiones, comprobaciones y detalles de compatibilidad en las guías
  temáticas. No repetir su contenido ni mantener una lista de herramientas
  descartadas aquí.
- README.md es una entrada breve: contenido del repositorio, máquina destino y
  navegación. Mantener criterios de trabajo aquí, pendientes en TODO.md y detalles
  en sus guías. Enlazar una sola fuente en vez de duplicar estados, procedimientos
  o listas. No añadir advertencias genéricas ni salvedades defensivas al resumen;
  incluir una restricción sólo donde afecte una operación concreta.
- El bajo consumo de CPU, la estabilidad y la productividad son prioritarios.
  Preferir la herramienta compatible más ligera que resuelva la necesidad;
  consola/TUI sólo cuando aporte una ventaja real. Evitar daemons, sondeos,
  efectos y compilaciones locales grandes innecesarios. No afirmar mejoras sin
  medidas representativas. RAM/SSD son limitados; nunca debilitar la seguridad
  para optimizar. El navegador forma parte de la carga de trabajo: elegir las
  demás herramientas considerando esos límites.
- Las fuentes de configuración/escritorio van en config/, los scripts de
  ejecución en scripts/ y las herramientas manuales de desarrollo en tools/.
  Explicar los scripts y registrar rutas completas de origen, destinos reales
  y modos en config/manifest.json.
- Agrupar las fuentes nuevas bajo config/<component>/, incluidos los metadatos
  APT del proveedor en su subdirectorio apt/; no añadir archivos de aplicaciones
  sueltos directamente en config/. Mantener allí los inventarios comunes.
  Gestionar por separado la migración de fuentes heredadas sueltas mediante
  comprobaciones de referencias/manifiesto; no mezclar configuración con caches,
  plugins descargados ni estado de ejecución.
- Mantener una única fuente pública en /home/jd/dotfiles-i3-2310m y en GitHub;
  no generar copias secundarias del repositorio. La configuración de usuario
  usa enlaces simbólicos por archivo a las fuentes revisadas; los scripts se
  ejecutan desde scripts/ dentro del checkout, sin copias en ~/scripts.
  Sincronizar las fuentes versionadas mediante GitHub commit/push/pull;
  usar SSH para administración/despliegue y
  transferencias privadas necesarias en la red local. Validar principalmente en
  la portátil, donde se ejecuta la configuración. Cuenta/home actuales: jd /home/jd;
  los destinos y excepciones privadas se declaran en el manifiesto. Conservar las bases de
  recuperación privadas fuera de los árboles activos, no versiones obsoletas
  dentro; retirar material temporal superado tras comprobarlo.
- El trabajo solicitado autoriza el flujo de ramas/commits/pull requests descrito
  abajo. Integrar requiere aprobación explícita; nunca hacer merge automático.
  Crear repositorios, renombrar carpetas, cambiar visibilidad o reescribir historial
  requiere autorización explícita separada.

## Language and naming

- Redactar en español el cuerpo de la documentación, tanto el contenido actual
  como las nuevas aportaciones de TODO.md y AGENTS.md. Usar contenido íntegramente
  en inglés sólo en los archivos indicados explícitamente.
- El README.md principal de la raíz es una excepción: todo su contenido, incluido
  el cuerpo, se redacta en inglés.
- Redactar en inglés todos los títulos y subtítulos de la documentación, incluidos
  los encabezados de sección y subsección.
- Usar etiquetas de navegación y textos de enlaces a documentos en inglés, según
  el título o nombre real del destino. Si la etiqueta es un nombre de archivo,
  respetar su escritura exacta, mayúsculas y extensión. Los destinos deben coincidir
  con las rutas reales, también en sistemas que distinguen mayúsculas de minúsculas.
- Mantener exclusivamente en inglés (en_US.UTF-8) el sistema y todos los
  textos visibles de aplicaciones, menús, barra, CLI y ayudas de interfaz.
- Nombrar los repositorios y sus archivos, scripts y directorios propios en
  inglés y en kebab-case: minúsculas separadas por guiones medios, sin espacios,
  guiones bajos ni camelCase. Ejemplos: restore-guide.md, open-networks.sh y
  window-tools/.
- Nombrar en inglés y sin espacios los directorios de uso personal creados
  en la portátil, tanto manualmente como por scripts. Distinguirlos de los
  repositorios: la convención para nombres personales de varias palabras
  queda por definir, sin adoptar todavía guiones ni guiones bajos.
- Exceptuar los nombres convencionales README.md, AGENTS.md, CHANGELOG.md, TODO.md,
  LICENSE y los nombres exactos exigidos por herramientas. Conservar recursos y
  avisos de proveedores, y módulos Python test_*.py para descubrimiento estándar
  con unittest. No crear archivos ajenos a la estructura sólo por esta excepción.
- Conservar sin traducir comandos, rutas, identificadores, nombres propios y
  valores técnicos requeridos por el software. Estas reglas no implican renombrados
  masivos de archivos existentes.
- Los mensajes de commit y el contenido completo de los PR se redactan en inglés
  según Git conventions; los archivos del diff conservan sus reglas de idioma.

## Git conventions

- Antes de editar, crear una rama de trabajo desde una base revisada y actualizada;
  nunca implementar ni hacer commits directamente en main. Nombrar las ramas en
  inglés como type/description-in-kebab-case (feat/, fix/, docs/, chore/), sin
  prefijos de herramientas. Revisar primero los cambios existentes y conservar
  el trabajo en curso.
- Los enlaces activos siguen el contenido del checkout. Tras integrar un PR,
  actualizar primero la referencia local de main por fast-forward desde GitHub
  y comprobar las fuentes antes de cambiar de rama; no pasar temporalmente por
  un main antiguo ni por una rama que reponga rutas ya retiradas.
- Hacer un commit por bloque coherente y validado, preparando el índice con una
  lista explícita de archivos permitidos. Redactar asunto y cuerpo íntegramente
  en inglés con Conventional Commits: type(scope): description; el ámbito es
  opcional. No mezclar cambios ajenos ni dejar todos los commits para el final.
- Tras validar y comprobar la publicación, hacer push de la rama y preparar un
  pull request contra main para revisión. Redactar título, encabezados y cuerpo
  del PR íntegramente en inglés, con título Conventional Commits. Explicar el
  comportamiento resultante, comprobaciones y límites relevantes de restauración/
  despliegue. Preparar el PR no autoriza integrarlo.
- La autorización habitual cubre crear ramas, hacer commits y publicar ramas del
  trabajo solicitado; no volver a pedirla en cada paso. Nunca hacer push directo
  a main ni force-push. Véase docs/git-workflow.md.

## Change workflow

Trabajar en una sola tarea a la vez. Si hay una rama de trabajo o un PR
pendiente, consultar antes de abrir otra rama o PR para una tarea distinta.
Trabajar en dos o más tareas a la vez sólo con autorización explícita.

Trabajar una prioridad y un componente por vez. Revisar dependencias, procesos
residentes y sondeos para este hardware y Xorg/i3 antes de añadir tareas a TODO.md.
Validar las afirmaciones de rendimiento con medidas representativas en la portátil.

1. Inspeccionar los destinos reales y conservar los cambios existentes. Si no son
   accesibles, hacer sólo cambios locales claramente identificados; no afirmar
   que hubo despliegue ni igualdad.
2. Editar primero las fuentes locales; revisar una base sin secretos para archivos
   recién gestionados. Cada componente debe poder reproducirse tras reinstalar:
   declarar dependencias y procedencia, destinos/modos, instalación, validación y
   rollback en su guía y manifiesto. No depender de cambios manuales sin documentar
   ni de estado privado de ejecución.
3. Respaldar los destinos en privado fuera de este árbol antes del despliegue.
4. Desplegar archivos de usuario como jd; los del sistema por separado con sudo
   autorizado, propiedad de root e instalación regular, nunca enlaces al home
   escribible.
5. Validar sintaxis y comportamiento en la sesión existente. Conservar aplicaciones,
   tty2+, SSH y la salida de recuperación disable-autostart; no iniciar X desde
   SSH/root.
6. Comparar contenidos/hashes, enlaces, permisos y propietarios en la portátil;
   actualizar guías/CHANGELOG y publicar las fuentes mediante GitHub. Retirar
   copias públicas redundantes sólo después de verificar sus referencias y
   recuperar cualquier diferencia útil.
7. Los enlaces de usuario requieren destinos en la portátil, comprobación de
   conflictos por archivo, dry-run y rollback privado. No enlazar autenticación,
   caches ni archivos que mezclen preferencias con estado privado generado.

## Runtime contract

- Mantener el arranque mínimo: las aplicaciones de uso bajo demanda no se
  inician automáticamente por estar instaladas. Añadir programas, scripts o
  servicios al arranque o al inicio de sesión sólo tras revisar su necesidad,
  dependencias y coste residente, y acordarlo explícitamente. Conservar los
  componentes de sesión ya definidos; evaluar nuevas necesidades de una en una.
- El login autenticado en tty1 inicia i3; no añadir display manager, autologin,
  escritorio completo ni compositor sin aprobación explícita. Super+Space abre
  el lanzador; Super+Enter, la terminal; barra superior. Actualizar
  docs/keybindings.md y la ayuda visible al cambiar atajos.
- Print Screen y Super+Ctrl+Alt+C abren Flameshot bajo demanda en Xorg para
  seleccionar una región o todo el escritorio, previsualizar y editar.
  Sólo al aceptar se guarda en ~/Pictures/Screenshots y se copia el PNG;
  Escape deja intactos archivos y portapapeles. Sin historial, cargas en
  línea ni arranque automático. Operación en docs/screen-capture.md.
- Catppuccin Mocha con barra compacta y opaca. Texto de barra JetBrainsMono Nerd Font Mono
  Regular 10 e iconos de clima/métricas/audio/batería Propo Regular 12. Wi-Fi conserva
  BGH Status Icons 12. Bold está instalada, pero no se fuerza. Mostrar escritorios existentes.
- Kitty aplica 85 % de opacidad estática al fondo por defecto. i3 inicia
  `xcompmgr -n` para composición básica X11, sin sombras, desenfoque,
  animaciones ni shaders. Mantener opacas la barra y las decoraciones.
  Operación y recuperación en docs/kitty-setup.md.
- Los fondos versionados van en `wallpapers/`. i3 aplica la imagen instalada
  al iniciar con xwallpaper, sin daemon propio ni cambios automáticos.
  Operación y recuperación en docs/i3-setup.md.
- Tick de i3status de 10 s; tráfico por diferencias de contadores en ese ciclo.
  Sin sondeo adicional de alta frecuencia. status-clicks.py es residente y
  funciona por eventos.
- Las métricas secundarias empiezan contraídas; el chevrón redibuja la muestra
  guardada en memoria, sin consultas ni procesos adicionales. Conservar bloques
  marcados como urgentes y datos esenciales; operación en docs/status-bar.md.
- Batería del equipo: iconos de ausencia, carga con rayo, nivel en descarga,
  completa con marca y reposo con pausa; porcentaje sólo cuando es válido.
  Consumir estados nativos de i3status, sin inferir carga por estar en CA ni
  confundir baterías HID con la del equipo. Sin lector ni sondeo adicionales;
  conservar avisos nativos de nivel bajo. Operación en docs/status-bar.md.
- El reloj alterna un calendario GTK3 y CPU alterna btop en una ventana Kitty
  exclusiva. Auxiliar breve por eventos IPC, identidades exactas y lock por
  panel; no cerrar ventanas ajenas ni añadir sondeos. btop refresca cada 2 s
  sólo mientras está abierto; detalles en docs/status-panels.md.
- Brillo de pantalla: bloque de sol siempre visible y panel GTK3 bajo demanda.
  Leer la retroiluminación física del panel interno en el tick de 10 s y
  usar logind desde la sesión local: 43 % al inicio de i3 y ajustes por
  interacción después. No reaplicar al recargar i3 ni al abrir el panel.
  No escribir cero, manipular la gamma ni añadir permisos o sondeos.
  Operación en docs/status-bar.md.
- Clima: coordenadas públicas del centro de Orán, sin geolocalización automática;
  sólo icono/temperatura, refresco cada 30 min mediante servicio breve/cache,
  indicando honestamente los datos desactualizados.
- Contador APT: simulación con metadatos locales cada 6 h; sin apt update,
  upgrade ni instalación automáticos. Acciones de clic fijas por eventos,
  sin interpolación de shell.
- Bloque Wi-Fi: sólo icono de nivel, sin SSID ni calidad numérica. El clic,
  Super+N y Wi-Fi Networks en Rofi abren la misma lista en inglés y recuperan
  la instancia abierta. Conservar la autorización de NetworkManager.
- Audio USB usa ALSA/libasound existente, con perfil público de VID/PID,
  driver snd-usb-audio y control de reproducción verificado. La barra consulta
  conexión/volumen en el tick de 10 s; clic o Super+A alterna un deslizador GTK3
  bajo su bloque también mediante teclado. Anclaje desde la muestra visible en
  memoria X11 y Pango sólo bajo demanda, sin archivos de estado. No fijar puerto
  USB/hub ni número de tarjeta. Revalidar tarjeta e identidad antes de escribir; no tocar
  micrófono/captura ni cambiar volumen o mute al abrir/conectar. Sin servidores
  de audio, sondeo adicional ni servicio propio. No audio sólo si falta el
  adaptador; errores/ambigüedad muestran Audio ?. Operación en docs/audio-setup.md.
- La recuperación de reproducción tras cambiar el USB es manual con
  `refresh-helium-audio.py`: sólo el AudioService de Helium de la cuenta actual,
  con USB verificado, captura cerrada, identidad revalidada y pidfd; sin reiniciar
  el navegador ni añadir automatización de hotplug. Sin argumentos sólo revisa;
  `--apply` renueva ese proceso. Operación en docs/audio-setup.md.
- Bluetooth/Magic Trackpad 2 usa BlueZ, btusb, hid_magicmouse y libinput de Debian;
  sin gestor gráfico ni agente Bluetooth adicional. Emparejar sólo el
  dispositivo identificado, detener el escaneo y cerrar el agente temporal.
  Claves de enlace y direcciones permanecen privadas; operación en
  docs/bluetooth-setup.md.
- Gestos del Magic Trackpad 2: tres dedos a la izquierda/derecha cambian al
  escritorio siguiente/anterior existente de la misma pantalla al terminar.
  Un auxiliar de usuario espera eventos XInput 2.4 con libXi/libX11 existentes,
  limitado por HID y driver; altas/bajas por eventos, sin sondeo, acceso evdev,
  grupo input, sudo ni servicio systemd. No asignar verticales, cuatro dedos
  ni pinza; no cambiar clics, scroll o aceleración. Operación y límites de la
  captura de swipes en docs/trackpad-gestures.md.
- Indicadores Bluetooth/trackpad permanecen visibles en la barra compacta.
  Consultar BlueZ mediante libsystemd existente en el tick de 10 s; reutilizar el lector
  HID del proveedor fijado cada 5 min en un proceso breve. Cache sólo en memoria,
  sin root ni servicio/timer adicional; acceso hidraw limitado por uaccess a la
  sesión local activa y al HID exacto del Trackpad 2.
- El icono del trackpad alterna un panel GTK3 bajo el bloque, con el tema del
  calendario, para la velocidad del Magic Trackpad 2 Bluetooth en Xorg.
  Verificar HID y nodo XInput de nuevo antes de escribir; no tocar otros
  dispositivos ni el perfil de aceleración. Xorg aplica la velocidad inicial
  acordada mediante una etiqueta udev del HID Bluetooth exacto; el panel conserva
  cambios manuales durante esa conexión, sin procesos ni servicios para reaplicarlos.
- Menú de energía: Power off primero y Yes seleccionado en todas las
  confirmaciones; disponibles Escape/No/Cancel. Autorización de sesión local
  activa mediante logind/polkitd estándar, sin fallback sudo, políticas amplias
  propias ni NOPASSWD. Exigir Can*=yes, --no-ask-password y check-inhibitors=auto
  con comprobación de systemd>=257. Suspender bloquea primero. Sin acciones
  forzadas ni que ignoren inhibidores.
- Nunca probar bloqueo/logout/suspensión/reinicio/apagado reales ni interrumpir
  la red sin coordinación. Usar dry-run y comprobaciones reales de inhibidores
  desde la sesión local; SSH no es un contexto de autorización equivalente.
  El bloqueo automático por tapa/inactividad sigue pendiente.
- Conservar SIGSTOP/SIGCONT predeterminados de i3bar; las señales abarcan todo
  el grupo de procesos. Un reload puede conservar el adaptador anterior;
  reiniciar i3 preservando ventanas si hace falta.
- Helium es el navegador predeterminado. Super+Shift+B y Super+Shift+Enter lo
  abren directamente, sin resolver el navegador por XDG al pulsar el atajo.
- La entrada de usuario `helium` aplica `Adwaita:dark` a sus selectores GTK;
  i3 limita la geometría inicial de `GtkFileChooserDialog` para mantener Save y
  Cancel visibles en la pantalla interna. Sin portales ni procesos adicionales;
  operación y recuperación en docs/apps-setup.md.
- Helium usa el repositorio APT stable oficial firmado; conservar el sandbox.
  Verificar compatibilidad GPU/CPU, sin ocultar límites mediante renderizado
  permanente por software.
- Los emoji usan Noto Color Emoji de Debian como fuente de sistema y el
  fallback de Fontconfig existente; no sustituir las fuentes de texto/barra ni
  añadir reglas globales propias. Operación en docs/apps-setup.md.
- El hard block Wi-Fi sigue sin resolver; la captura final acotada está completa.
  No repetir ciclos de arranque, eventos Fn, blacklist ni trabajos de EC/firmware
  por defecto.

## Security, tools and validation

- Usar umask 022 para actualizaciones Git y fuentes públicas nuevas; Git no
  distingue 644 de 664. Verificar modos y propietarios de fuentes/destinos tras
  el checkout, especialmente en enlaces. Normalizar sólo archivos públicos
  revisados según el manifiesto; nunca aplicar chmod masivo a archivos privados
  ni directorios de autenticación.
- Verificar la identidad SSH contra known_hosts confiable o la consola física.
  Las direcciones DHCP no son permanentes; no publicar direcciones LAN específicas
  de la instalación, huellas SSH, SSID ni rutas privadas de la máquina de administración.
- Mantener sudo protegido con contraseña; no rotar contraseñas ni cambiar métodos
  de acceso sin coordinación. Nunca versionar ni publicar credenciales, claves
  privadas, perfiles nmconnection, autenticación Codex, keyrings, memorias/SQLite,
  historial RTK ni logs. El material local necesario puede quedar en private/
  ignorado, con permisos restrictivos; transferir archivos privados revisados
  entre copias por SSH, nunca GitHub. Mantener backups de destinos fuera del
  árbol de trabajo; no importar directorios completos de autenticación privada.
- Antes de cada push, probar exclusiones reales, detectar archivos ya versionados
  pero ignorados, revisar la lista explícita del índice y su contenido exacto,
  y auditar todos los commits salientes en busca de secretos. Las exclusiones
  no eliminan datos versionados ni historial; detener la publicación ante
  hallazgos sin resolver. Nunca forzar la inclusión de material privado.
- Se pueden conservar claves públicas de proveedores y configuración sin secretos
  con procedencia verificada. MIT cubre el material original; conservar licencias
  de terceros.
- Mantener mínima y aditiva la integración RTK/Engram. Recrear el plugin oficial
  fijado, no directorios ocultos completos. Sin nube ni servicios de arranque
  sin aprobación; el auxiliar oficial limitado a loopback puede ejecutarse con
  Codex. Conservar chats activos; las pruebas que envían memorias a un modelo
  requieren un alcance explícito seguro para la privacidad.
- Mantener el lanzador Codex bajo demanda separado de los paquetes oficiales
  independientes. Recuperar sólo un alias verificado de socket de ejecución
  colgante bajo el lock de arranque del proveedor; conservar servidores activos,
  credenciales y chats.
- Para autenticación Codex, confirmar la cuenta de origen prevista y el destino;
  verificar la cuenta efectiva del backend tras recargas coordinadas. El estado
  de login o la conectividad por sí solos no bastan; conservar la cache persistente
  y privada, nunca en Git ni en tareas de copia al iniciar.
- Los comandos de shell de administración empiezan con rtk; usar su passthrough
  compatible (0.43: proxy). RTK 1.1.0 de la portátil usa bypass; no mezclar versiones.
- Validar i3 con i3 -C, archivos shell con sh -n y aplicaciones gráficas con sus
  parsers más pruebas acotadas de ventanas reales. Usar Mod1 para Alt. Los cambios
  de cache/renderizado de fuentes pueden necesitar reiniciar i3, nunca logout/
  reinicio del equipo sólo para refrescar fuentes.
- Las pruebas no demuestran restauración limpia ni rendimiento sostenido de CPU.
  Mantenerlas no destructivas y guardar material generado fuera del árbol.
- Seguir el protocolo de memoria Engram; persistir decisiones duraderas y resúmenes
  fuera de la configuración publicada.

## Productivity tools

- Local Web Stack gestiona PHP/Composer/MariaDB/phpMyAdmin de Debian para
  desarrollo PHP, con servicios locales bajo demanda y un panel GTK3 que conserva
  sudo autenticado. El perfil permite root de base de datos por TCP solo en
  loopback, con la contraseña local elegida para práctica; conservar por separado
  root@localhost por socket y la autenticación del sistema. Credenciales y bases
  quedan privadas, sin generación automática de claves ni diálogos temporales.
  No añadir Apache, PHP-FPM, contenedores, Node, watchers ni autostart por
  anticipado. Operación en docs/laravel-setup.md.

- Kitty usa su barra nativa superior incluso con una pestaña, etiquetas del
  directorio activo y pestañas nuevas en ese directorio. Las terminales
  interactivas nuevas de Kitty usan Zsh con Starship; conservar Bash como
  shell de login para tty1 y SSH. No modificar los intérpretes de los scripts.
  El completado usa funciones nativas de Zsh, sin framework ni plugins
  adicionales; conservar las comprobaciones de seguridad y la cache privada.
  Conservar fuente/repintado y confirmaciones nativas; los paneles auxiliares
  usan una excepción de visibilidad por invocación. Operación en docs/kitty-setup.md.
- Usar Yazi para gestión general de archivos y Neovim estable oficial para edición.
  Instalar el archivo precompilado del proveedor, versionado y verificado con SHA256,
  bajo /opt propiedad de root; seleccionarlo mediante /usr/local/bin/nvim y las
  alternativas vi/vim/ex/view/vimdiff existentes, conservando sus flags de modo.
  Mantener el paquete Debian sólo como vía explícita de recuperación. Actualizar
  manualmente: revisar compatibilidad y hashes, validar en la portátil y registrar
  la versión comprobada; sin compilación ni descargas automáticas latest/nightly.
  APT no actualiza esta copia del proveedor. Yazi usa su repositorio APT stable
  oficial firmado, limitado a ese paquete; evitar compilación local y no instalar
  por defecto todas las integraciones opcionales/recomendadas.
- Thunar y Visual Studio Code son alternativas gráficas bajo demanda; no fijar
  asociaciones MIME ni cambiar los editores predeterminados. Thunar reutiliza GTK3
  con tema oscuro en su lanzador y en la activación D-Bus mediante su servicio
  de usuario existente; sin cambiar el tema GTK global ni añadir autostart.
  No instalar XFCE completo ni servicios opcionales por defecto.
  VS Code usa el repositorio oficial estable firmado
  limitado a `code`; mantener sandbox, sin autostart ni extensiones de oficio.
- Zathura con Poppler es el lector PDF predeterminado, con modo oscuro Mocha
  y portapapeles estándar. Helium conserva la web; Yazi conserva sus previews.
- LazyVim estable es el perfil predeterminado de Neovim. Fijar release y
  revisiones de plugins; instalar bajo demanda sin comprobador periódico de
  actualizaciones ni aprovisionamiento implícito de herramientas de lenguaje.
  Conservar el perfil previo con mini.files sólo como recuperación.
- Yazi limita los previews normales a texto/directorios y desactiva la precarga
  multimedia. Conservar su invocación de `nvim` y no cambiar las alternativas.
- Añadir módulos, servidores LSP, watchers o auxiliares multimedia sólo para un
  flujo identificado y con revisión explícita de recursos, no porque existan.
  Las API de paquetes deben corresponder a la versión instalada de Neovim.
- Habilitar LSP de Python primero si hace falta; Java y web quedan para después.
  Medir respuesta, CPU y RAM con Helium y carga real antes de ampliar el perfil.
  Operación, recuperación y dependencias en docs/lazyvim-setup.md.
