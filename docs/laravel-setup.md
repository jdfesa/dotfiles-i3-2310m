# Local Web Stack

## Scope

Pila web opcional de desarrollo local para Debian 13, independiente del framework: PHP 8.4 CLI, Composer,
MariaDB y phpMyAdmin desde los repositorios firmados de Debian. PHP 8.4
cumple el requisito de PHP >=8.3 de [Laravel 13](https://laravel.com/framework/docs/13.x/releases).
La versión del framework se elige por proyecto; no se instala globalmente ni
se incorpora código de aplicaciones a estos dotfiles.

phpMyAdmin usa el servidor de desarrollo de PHP en `127.0.0.1:8080`, como
`www-data`, con un solo proceso y sin Apache ni PHP-FPM. Su uso es local e
individual; una petición larga puede bloquear las demás. No sirve para
publicación ni acceso desde otras máquinas. El router propio limita los
entrypoints y recursos públicos, porque este servidor no interpreta `.htaccess`.

MariaDB escucha solo en `127.0.0.1:3306`, conserva el socket administrativo
de Debian y no se habilita al arrancar. Tampoco hay autostart del panel,
timer, contenedor, servidor FTP ni watcher del perfil.

## Dependencies and sources

[packages-debian.txt](../config/laravel/packages-debian.txt) declara las
dependencias directas. Las bibliotecas transitivas las resuelve APT, sin
compilación local y con `--no-install-recommends`. SQLite permite ejecutar
los proyectos iniciales y pruebas que lo usan por defecto; MariaDB queda
disponible para los ejercicios de MySQL. `python3-gi`, GTK3, Kitty, systemd,
sudo y xdg-utils reutilizan componentes de la sesión existente.

`unzip` conserva permisos al extraer los paquetes ZIP descargados por Composer.
Composer se ejecuta como `jd`, nunca con sudo. Proyectos, `vendor/`, caches,
claves de aplicaciones, `.env`, bases y credenciales permanecen fuera del
repositorio. Node/npm y los procesos de frontend se revisan cuando el proyecto
los requiera; este perfil no los instala por anticipado.

Referencias: [Debian PHP CLI](https://packages.debian.org/trixie/php8.4-cli),
[Debian MariaDB](https://packages.debian.org/trixie/mariadb-server),
[Debian phpMyAdmin](https://packages.debian.org/trixie/phpmyadmin),
[PHP development server](https://www.php.net/manual/en/features.commandline.webserver.php),
[phpMyAdmin installation](https://docs.phpmyadmin.net/en/latest/setup.html).

## Installation

Desde el checkout canónico, revisar primero fuentes, destinos, servicios
existentes y la simulación:

```sh
umask 022
python3 tools/install-laravel-stack.py
systemctl is-active mariadb.service laravel-phpmyadmin.service
```

El instalador detiene la operación si hay servicios activos, destinos con
enlaces simbólicos o una política `policy-rc.d` previa pendiente de revisión.
No reemplaza una instalación XAMPP ni migra datos existentes.

En una terminal local, autenticar sudo y aplicar el bloque revisado:

```sh
sudo /usr/bin/python3 tools/install-laravel-stack.py --apply
```

El auxiliar actualiza los metadatos APT, vuelve a simular y usa los paquetes
oficiales disponibles. Antes de instalar archivos, guarda el estado anterior
de los destinos en `/var/backups/bgh-laravel-<UTC>/`, root:root700, con
inventario600. Inhibe temporalmente el inicio de servicios por scripts de
paquetes y retira solo su propia política al terminar. Desactiva el arranque
automático de MariaDB y cualquier socket suministrado por el paquete.

La configuración se instala como archivos regulares root:root644 según
[manifest.json](../config/manifest.json). Se prepara el esquema inicial `laravel`
y el acceso administrativo `root`@`127.0.0.1` para crear y gestionar bases de
práctica desde phpMyAdmin. El nombre del esquema es solo un ejemplo; la pila
sirve también para otros proyectos PHP. La contraseña se elige en la terminal,
sin generación automática, y se conserva únicamente en
`~/.local/state/laravel-development/database.env`, jd:jd600, en directorio700.
No se guarda en las fuentes ni se imprime. El acceso administrativo nativo
`root`@`localhost` conserva el método `unix_socket` y admite también la
contraseña local elegida, sin cambiar la cuenta root de Debian ni sudo.

Para cambiar explícitamente el acceso de una instalación existente, sin
reinstalar paquetes ni reiniciar servicios:

```sh
sudo /usr/bin/python3 tools/install-laravel-stack.py --configure-login
```

Esta operación pide la contraseña de base de datos elegida y su confirmación;
no cambia la contraseña de la cuenta Debian. La contraseña también se puede
leer con `--password-file` desde un archivo externo privado600. Antes del
cambio, guarda las credenciales/configuración anteriores y los metadatos de
las cuentas root en `/var/backups/bgh-local-db-login-<UTC>/`, root:root700.
Configura la contraseña en las identidades root locales, conserva los métodos
nativos de autenticación por socket y los privilegios existentes de localhost,
y comprueba ambos accesos. Otras cuentas y los datos se conservan.

El instalador arranca los servicios para comprobar el acceso HTTP y vuelve
a detenerlos. La configuración de dbconfig-common se omite: no hace falta
otra base ni cuenta de control para las funciones básicas de phpMyAdmin.
Sus funciones avanzadas de almacenamiento de preferencias no están provisionadas.

Como `jd`, revisar y aplicar únicamente el enlace de este componente mediante
[User configuration links](user-config-links.md):

```sh
python3 tools/link-user-config.py --source config/laravel/bgh-laravel-services.desktop
python3 tools/link-user-config.py --source config/laravel/bgh-laravel-services.desktop \
  --apply --backup-dir "$HOME/.local/state/bgh-config-backups/laravel-$(date -u +%Y%m%dT%H%M%SZ)"
```

El nuevo destino es únicamente
`~/.local/share/applications/bgh-laravel-services.desktop`; el panel y su CSS
se leen directamente desde el checkout. No hace falta recargar i3.

## On-demand use

Abrir **Local Web Stack** desde Rofi o ejecutar:

```sh
./scripts/laravel-services.py
./scripts/laravel-services.py --status
```

El panel muestra el estado al abrir y después de cada acción. **Refresh**
actualiza cambios hechos desde otra terminal, sin consultas periódicas.
Los botones Start/Stop abren una terminal Kitty para sudo autenticado;
cancelar no se interpreta como éxito. El panel y el navegador siguen como
`jd`. Otra invocación recupera la ventana existente.

- Start de phpMyAdmin también inicia MariaDB si hace falta.
- Stop de phpMyAdmin deja MariaDB disponible para el proyecto.
- Stop de MariaDB detiene también phpMyAdmin por su dependencia de systemd.
- **Open phpMyAdmin** abre `http://127.0.0.1:8080/` en el navegador habitual.
- Cerrar el panel conserva el estado elegido de los servicios. Detenerlos
  con sus botones al terminar de trabajar.

En phpMyAdmin, usar `root` con la contraseña local elegida. Permite crear
otras bases para los ejercicios desde la propia interfaz. El acceso TCP se
limita a `127.0.0.1`; se mantiene deshabilitado el acceso sin contraseña.
La administración del sistema sigue usando sudo autenticado. Las rutas
internas que conservan el nombre `laravel` mantienen la compatibilidad del
perfil instalado; el título de la aplicación es **Local Web Stack**.

## Laravel projects

Como `jd`, fuera de los dotfiles:

```sh
mkdir -p "$HOME/projects"
composer create-project laravel/laravel "$HOME/projects/laravel-study" '^13.0'
cd "$HOME/projects/laravel-study"
php artisan --version
```

Para usar MariaDB, copiar los valores `DB_*` del archivo privado a `.env`,
conservando `APP_KEY` y las demás opciones del proyecto; proteger `.env`
con modo600. Iniciar MariaDB desde el panel y ejecutar:

```sh
php artisan migrate
php artisan serve --host=127.0.0.1
```

Usar `http://127.0.0.1:8000/` para la aplicación y Ctrl+C para detener su
servidor. Las compilaciones de recursos frontend se preparan por separado
según los requisitos reales del proyecto; no son necesarias para verificar
el intérprete, Composer y el acceso a MariaDB.

## Verification

Comprobado el 2026-11-18 con PHP 8.4.27, Composer 2.8.8, MariaDB 11.8.6 y
el paquete Debian phpMyAdmin 5.2.2. El inventario completo de versiones y
procedencia está en [Dependencies and versions](dependencies.md).
Un proyecto temporal con Laravel Framework 13.43.0 pasó los requisitos de
plataforma de Composer, respondió HTTP200 y creó/insertó/leyó una tabla de
verificación en MariaDB; se retiraron solo esa tabla y su servidor temporal.
También se comprobaron la ventana GTK3, el inicio desde el panel, el login
de phpMyAdmin con la cuenta de desarrollo, sus 39 recursos CSS/JS y el bloqueo
HTTP404 de setup/configuración/bibliotecas internas. Los archivos desplegados
coinciden con el manifiesto en contenido, propietario, modo y enlaces.
No se compilaron recursos frontend ni se midió rendimiento sostenido.

```sh
php --version
composer --version
php -m
php -l config/laravel/phpmyadmin.inc.php
php -l config/laravel/phpmyadmin-router.php
systemd-analyze verify config/laravel/phpmyadmin.service
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_laravel_services.py -q
./scripts/laravel-services.py --status
systemctl is-enabled mariadb.service laravel-phpmyadmin.service
ss -ltn
```

Comprobar también el login de phpMyAdmin, una consulta desde Laravel y
Start/Stop desde el panel real. Cuando los servicios están activos, los
puertos3306/8080 deben escuchar solo en loopback; detenidos, deben quedar
cerrados. El estado esperado de habilitación es `disabled` para MariaDB y
`static` para phpMyAdmin. No publicar respuestas HTTP con cookies/tokens ni
capturas que muestren contraseñas. Las pruebas simuladas no demuestran
rendimiento sostenido ni una restauración limpia.

## Recovery

Detener únicamente este perfil:

```sh
sudo systemctl stop laravel-phpmyadmin.service mariadb.service
```

Para revertir fuentes de sistema, consultar `files.json` del backup privado:
restaurar solo los destinos que existían, con su modo anterior; retirar solo
los archivos nuevos del perfil después de comprobar su identidad. Ejecutar
`sudo systemctl daemon-reload`. No eliminar `/var/lib/mysql`, el archivo de
credenciales ni bases de proyectos para revertir configuración. Si falló la
configuración del acceso, conservar `database.env` y revisar el estado mediante
`sudo mariadb` antes de repetir. Para revertir un cambio de login, usar el backup
`bgh-local-db-login-*`: restaurar `database.env` como jd:jd600 y el fragmento PHP
como root:root644. Si `root-loopback.json` está vacío, la cuenta TCP no existía
antes del cambio y puede retirarse con `DROP USER 'root'@'127.0.0.1';`; si contiene
una cuenta previa, revisar y reponer su autenticación/privilegios del backup.
Para restaurar exactamente la autenticación anterior de localhost, revisar el
registro privado `root-localhost.json`; conservar su método `unix_socket`.
No borrar bases para revertir este acceso.

El enlace de Rofi se revierte con el journal del auxiliar de enlaces. Antes
de desinstalar paquetes, hacer un dump privado de las bases que interesen y
revisar la simulación `apt-get -s remove` sobre la lista explícita. Evitar
purge/autoremove sin revisar los datos y dependencias compartidas. El backup
de configuración no es un respaldo de las bases. Las fuentes públicas se
recuperan desde GitHub; contraseñas y datos necesitan respaldo privado separado.
