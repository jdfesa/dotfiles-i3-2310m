# Laravel development

## Scope

Perfil opcional de desarrollo local para Debian 13: PHP 8.4 CLI, Composer,
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
[manifest.json](../config/manifest.json). No se enlazan archivos del sistema
a un home escribible. Se crean el esquema `laravel` y la cuenta
`laravel`@`127.0.0.1`, con permisos solo sobre ese esquema. La contraseña
aleatoria se guarda exclusivamente en
`~/.local/state/laravel-development/database.env`, jd:jd600, dentro de un
directorio700. No se imprime ni pasa por argumentos o historial. No se
modifican credenciales existentes ni la autenticación de root.

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

Abrir **Laravel Services** desde Rofi o ejecutar:

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

En phpMyAdmin, usar la cuenta `laravel` y la contraseña del archivo privado.
No usar root ni permitir contraseñas vacías. Para otros proyectos, crear un
esquema y cuenta específicos mediante `sudo mariadb`, sin ampliar la cuenta
de estudio a permisos globales.

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
creación de cuenta/base, conservar `database.env` y revisar el estado mediante
`sudo mariadb` antes de repetir; el instalador no reemplaza cuentas existentes.

El enlace de Rofi se revierte con el journal del auxiliar de enlaces. Antes
de desinstalar paquetes, hacer un dump privado de las bases que interesen y
revisar la simulación `apt-get -s remove` sobre la lista explícita. Evitar
purge/autoremove sin revisar los datos y dependencias compartidas. El backup
de configuración no es un respaldo de las bases. Las fuentes públicas se
recuperan desde GitHub; contraseñas y datos necesitan respaldo privado separado.
