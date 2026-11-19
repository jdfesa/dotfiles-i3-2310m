# Local Web Stack

## Scope

Pila web opcional de desarrollo local para Debian 13, independiente del framework:
Apache con módulo PHP 8.4, Composer, MariaDB y phpMyAdmin desde los repositorios
firmados de Debian. PHP 8.4 cumple PHP >=8.3 de
[Laravel 13](https://laravel.com/framework/docs/13.x/releases). El framework y
el código de cada aplicación se instalan por proyecto, fuera de estos dotfiles.

Apache escucha únicamente en `127.0.0.1:80`, `[::1]:80` y `127.0.0.1:8080`.
Sirve `/var/www/html` en `http://127.0.0.1/` y phpMyAdmin en
`http://127.0.0.1/phpmyadmin/`; el puerto8080 redirige al nuevo acceso.
MariaDB escucha en `127.0.0.1:3306` y conserva su socket administrativo.
Ambos servicios quedan deshabilitados al arrancar. No hay autostart del panel,
PHP-FPM, FTP, contenedores ni watchers del perfil.

Apache usa prefork por compatibilidad con el módulo PHP: inicia un trabajador,
conserva entre uno y dos ociosos y admite hasta cuatro simultáneos. Son límites
para práctica individual; no constituyen una medición de consumo ni un ajuste
para publicación. Las peticiones largas pueden agotar ese cupo.

## Dependencies and sources

[packages-debian.txt](../config/laravel/packages-debian.txt) declara las
dependencias directas; APT resuelve las transitivas con `--no-install-recommends`,
sin compilación local. SQLite permite los ejercicios que lo usan por defecto;
MariaDB queda disponible para MySQL. `unzip` conserva permisos al extraer ZIP
de Composer. Composer se ejecuta como `jd`, nunca con sudo.

El panel reutiliza Python/GTK3, systemd, polkitd, Kitty y xdg-utils existentes.
`acl` permite lectura específica de los logs para jd, sin añadirlo al grupo
administrativo `adm`. No se añade agente de autorización ni daemon propio.
Node/npm y los procesos de frontend se revisan cuando un proyecto los requiera.
Proyectos, `vendor/`, caches, `.env`, claves, bases y credenciales permanecen
fuera del repositorio.

Referencias: [Debian Apache](https://packages.debian.org/trixie/apache2),
[Debian PHP module](https://packages.debian.org/trixie/libapache2-mod-php8.4),
[Apache prefork](https://httpd.apache.org/docs/2.4/mod/prefork.html),
[Debian MariaDB](https://packages.debian.org/trixie/mariadb-server),
[Debian phpMyAdmin](https://packages.debian.org/trixie/phpmyadmin),
[polkit rules](https://www.freedesktop.org/software/polkit/docs/latest/polkit.8.html).

## Installation

Desde el checkout canónico, revisar fuentes, destinos y simulación:

```sh
umask 022
python3 tools/install-laravel-stack.py
systemctl is-active apache2.service mariadb.service
```

Para una instalación nueva con servicios detenidos, autenticar sudo en la
terminal local:

```sh
sudo /usr/bin/python3 tools/install-laravel-stack.py --apply
```

Para completar el perfil anterior que servía solo phpMyAdmin con PHP CLI:

```sh
sudo /usr/bin/python3 tools/install-laravel-stack.py --complete-web-stack
```

La migración conserva las credenciales y bases existentes, reinicia MariaDB
para aplicar el log y deja Apache activo si el servidor web anterior lo estaba.
Conserva también el estado previo de MariaDB. Solo retira el servicio/router
anteriores si coinciden con sus hashes conocidos. Rechaza un Apache activo
ajeno, destinos con enlaces simbólicos o una política `policy-rc.d` previa.
No migra instalaciones XAMPP ni reemplaza datos de proyectos.

El auxiliar actualiza metadatos APT, vuelve a simular y respalda destinos y
estados en `/var/backups/bgh-laravel-<UTC>/`, root:root700, con inventarios600.
Guarda las ACL previas de logs existentes en `logs.acl`. Inhibe temporalmente
el inicio por scripts de paquetes y retira solo su propia política al terminar.
Instala archivos regulares root:root644 según
[manifest.json](../config/manifest.json), habilita PHP/rewrite y la configuración
Apache, comprueba los parsers nativos y deshabilita Apache/MariaDB y los sockets
MariaDB al arrancar. La instalación nueva verifica HTTP/SQL y deja los servicios
detenidos; la migración conserva su estado anterior.

Si `/var/www/html` no existía, su directorio pasa a jd con modo755 para guardar
proyectos; los archivos suministrados por Debian mantienen su propietario.
Se preparan `/var/log/apache2/error.log` y `/var/log/mysql/error.log` con acceso
de lectura específico para jd, más ACL por defecto en ambos directorios para
la rotación. El panel no recibe permiso de escritura ni acceso general a logs
del sistema. Se usa la rotación nativa de Debian.

En una instalación nueva se prepara el esquema inicial `laravel` y el acceso
administrativo `root`@`127.0.0.1`. La contraseña se elige localmente, sin generación
automática ni impresión, y queda en
`~/.local/state/laravel-development/database.env`, jd:jd600, directorio700.
El nombre del esquema es un ejemplo. `root`@`localhost` conserva `unix_socket`
y admite también la contraseña elegida, sin modificar cuentas Debian ni sudo.
El perfil existente conserva sus credenciales sin volver a configurarlas.

Para cambiar explícitamente el acceso, sin reinstalar ni reiniciar servicios:

```sh
sudo /usr/bin/python3 tools/install-laravel-stack.py --configure-login
```

Pide la contraseña de base de datos y confirmación. También acepta
`--password-file` desde un archivo externo privado600. Respalda credenciales,
configuración y metadatos de las cuentas root en
`/var/backups/bgh-local-db-login-<UTC>/`, root:root700; conserva los métodos de
autenticación y privilegios de localhost. No cambia otras cuentas ni datos.
El almacenamiento avanzado de preferencias de phpMyAdmin no se provisiona;
no hace falta una cuenta adicional de dbconfig-common para el uso básico.

Como jd, revisar y aplicar el enlace mediante
[User configuration links](user-config-links.md):

```sh
python3 tools/link-user-config.py --source config/laravel/bgh-laravel-services.desktop
python3 tools/link-user-config.py --source config/laravel/bgh-laravel-services.desktop \
  --apply --backup-dir "$HOME/.local/state/bgh-config-backups/laravel-$(date -u +%Y%m%dT%H%M%SZ)"
```

El destino es `~/.local/share/applications/bgh-laravel-services.desktop`;
panel y CSS se leen desde el checkout. No hace falta recargar i3.

## On-demand use

Abrir **Local Web Stack** desde Rofi o ejecutar:

```sh
./scripts/laravel-services.py
./scripts/laravel-services.py --status
```

El panel muestra Apache/PHP y MariaDB con estado real, PID y puertos configurados
cuando están activos. Consulta al abrir, después de cada acción y con **Refresh**,
sin sondeo periódico. Otra invocación recupera la ventana existente.

- **Start**, **Stop** y **Restart** controlan cada servicio por separado;
  las variantes **all** controlan ambos. Apache puede seguir sirviendo PHP
  aunque MariaDB esté detenido. phpMyAdmin depende del servidor Apache y
  requiere MariaDB para entrar a las bases.
- **Open localhost** abre el sitio; **Open phpMyAdmin**, la administración.
  Se habilitan cuando Apache está activo.
- **Logs** muestra hasta64KiB y las últimas120 líneas del log de errores elegido;
  **Refresh** vuelve a leerlo, sin seguimiento continuo.
- **Config** permite leer las fuentes públicas instaladas del perfil, sin
  editar archivos root ni mostrar contraseñas privadas.
- **Web root** abre `/var/www/html`; **Terminal** abre Kitty allí únicamente
  cuando se solicita ese botón.
- Cerrar el panel conserva los servicios. Detenerlos al terminar de trabajar.

Start/Stop/Restart usan systemd con `--no-ask-password`, sin terminal ni sudo.
La regla root de polkit autoriza exclusivamente a jd en sesión **local activa**,
solo `org.freedesktop.systemd1.manage-units`, unidades `apache2.service` y
`mariadb.service`, verbos `start`, `stop`, `restart`. No autoriza habilitar al
arrancar, modificar unidades, otras cuentas, SSH ni sesiones inactivas.
Fuera de ese contexto la acción falla y el panel muestra el error; no añade
un fallback que pida contraseña. La administración/instalación conserva sudo
autenticado.

En phpMyAdmin, entrar con `root` y la contraseña elegida localmente. Permite
crear bases para ejercicios y no admite acceso sin contraseña. Las rutas
internas `laravel` se conservan por compatibilidad; el nombre visible es
**Local Web Stack**.

## PHP and Laravel projects

Para PHP simple, crear como jd una carpeta propia dentro de `/var/www/html`,
por ejemplo `practice/index.php`, y abrir `http://127.0.0.1/practice/`.
Apache interpreta `.htaccess`, tiene rewrite habilitado y desactiva los listados
de directorios. Bloquea archivos ocultos y directorios `.git`.

Para Laravel, crear el proyecto fuera de los dotfiles:

```sh
mkdir -p "$HOME/projects"
composer create-project laravel/laravel "$HOME/projects/laravel-study" '^13.0'
cd "$HOME/projects/laravel-study"
php artisan --version
```

Copiar los valores `DB_*` del archivo privado a `.env`, conservar `APP_KEY`
y las demás opciones, proteger `.env` con modo600. Iniciar MariaDB y ejecutar:

```sh
php artisan migrate
php artisan serve --host=127.0.0.1
```

Abrir `http://127.0.0.1:8000/`; Ctrl+C detiene ese servidor. Si se configura
Apache para Laravel, el DocumentRoot debe ser exclusivamente `public/`, nunca
la raíz del proyecto; revisar ese virtual host y sus permisos por proyecto.
Los recursos frontend se preparan según sus requisitos reales.

## Verification

El inventario de versiones y procedencia está en
[Dependencies and versions](dependencies.md). El 2026-11-18 se verificaron
Apache/PHP con rewrite y PDO MySQL/SQLite, el login de phpMyAdmin y41 recursos
CSS/JS, la redirección8080, los bloqueos403 y la lectura de ambos logs como jd.
Los botones reales Start/Stop/Restart all actualizaron estados/PID sin abrir
terminales; Logs/Config abrieron sus diálogos. Las acciones no autorizadas de
reload de Apache e inicio del SSH ya activo fueron rechazadas, sin modificar
ese servicio. Comprobar parsers, bindings y servicios con:

```sh
sudo apache2ctl configtest
php --version
composer --version
php -l config/laravel/phpmyadmin.inc.php
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_laravel_services.py -q
./scripts/laravel-services.py --status
systemctl is-enabled apache2.service mariadb.service
ss -ltn
```

Validar un PHP temporal con SAPI `apache2handler`, PDO MySQL y SQLite, el login
real de phpMyAdmin y sus recursos CSS/JS, la redirección8080, y Start/Stop/Restart
desde el panel de la sesión local. Setup/configuración/bibliotecas internas de
phpMyAdmin deben responder403/404; archivos ocultos y `.git` también. No publicar
cookies, tokens ni capturas con contraseñas. Los puertos80/8080/3306 deben
escuchar solo en loopback y quedar cerrados al detener ambos servicios. El estado
de arranque esperado de ambos es `disabled`.

Las pruebas automatizadas no demuestran restauración limpia ni rendimiento
sostenido. El perfil Laravel13 fue validado además con un proyecto temporal,
requisitos Composer y una tabla de prueba; frontend queda fuera de ese alcance.

## Recovery

Detener solo Apache y MariaDB mediante el panel o con sudo autenticado:

```sh
sudo systemctl stop apache2.service mariadb.service
```

Para retirar la autorización sin contraseña, eliminar únicamente la regla
`/etc/polkit-1/rules.d/49-bgh-web-stack.rules` tras verificar su identidad;
polkit recarga sus reglas. No cambiar sudoers ni políticas globales.

Consultar `files.json` del backup privado: restaurar destinos que existían
con su modo anterior; retirar solo los nuevos tras verificar su identidad.
Deshabilitar la configuración Apache con `sudo a2disconf bgh-web-stack` antes
de retirar su archivo; revisar módulos y puertos si se conserva Apache para
otro uso. Restaurar ACL anteriores con `sudo setfacl --restore=.../logs.acl`;
en rutas nuevas sin ACL previa, retirar solo las entradas de jd del archivo
y del directorio, incluida su entrada por defecto. No borrar logs ni datos.
El estado anterior de servicios está en `services.json`. Para recuperar el
servidor PHP CLI anterior, restaurar servicio/router del backup y ejecutar
`sudo systemctl daemon-reload` antes de iniciarlo; detener antes Apache para
liberar8080. No habilitar servicios al arrancar como parte de la reversión.

No eliminar `/var/lib/mysql`, credenciales ni bases para revertir configuración.
Para revertir el login, usar `bgh-local-db-login-*`: restaurar `database.env`
jd:jd600 y el fragmento PHP root:root644; revisar los registros privados
`root-localhost.json` y `root-loopback.json` para reponer exactamente la
autenticación/privilegios anteriores, conservando `unix_socket`. Si la cuenta
TCP no existía antes, el registro estará vacío y puede retirarse esa cuenta.
No borrar bases para revertir el acceso.

El enlace del lanzador se revierte con su journal privado. Antes de desinstalar,
hacer un dump privado de las bases y revisar `apt-get -s remove` con lista
explícita; no usar purge/autoremove sin revisar dependencias/datos compartidos.
El backup de configuración no respalda bases. GitHub conserva fuentes públicas;
contraseñas y datos requieren respaldo privado separado.
