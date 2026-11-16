# Git workflow

## Scope

GitHub es la fuente de verdad de lo versionado y el puente entre máquinas; cada
una mantiene su copia de trabajo. La sincronización es manual mediante
commit/push/pull, sin servicios ni polling. SSH administra/despliega en la
portátil y transfiere material privado necesario por la red local, no sustituye
ese puente con copias paralelas de fuentes públicas. La validación principal
se realiza en la portátil. Git 2.47.3 comprobado en Debian 13.

## Author identity

Como cuenta de sesión, sin sudo. Revisar los valores existentes y respaldar
en privado la configuración global antes de cambiarla:

```sh
git config --show-origin --get user.name
git config --show-origin --get user.email
git config --global user.name "Jose David"
git config --global user.email "92765822+jdfesa@users.noreply.github.com"
```

`--global` aplica a los repositorios de esa cuenta; una identidad local puede
sobrescribirla. Para otro proyecto con identidad distinta, configurar las mismas
claves sin `--global` desde su raíz.

El nombre y el correo noreply son metadatos públicos de autoría, no credenciales
de acceso. Se documentan estas dos claves; no se copia el archivo global completo,
que puede contener preferencias o autenticación privadas.

Comprobar la identidad efectiva desde este repositorio:

```sh
git config --show-origin --get user.name
git config --show-origin --get user.email
git var GIT_AUTHOR_IDENT
git var GIT_COMMITTER_IDENT
```

## Authentication

`origin` usa HTTPS con el helper oficial de GitHub CLI. El token se conserva en
el depósito cifrado **Login**, protegido con la contraseña de la cuenta.
PAM lo desbloquea al entrar por consola; Xsession inicializa sólo `secrets`.
No se guarda esa contraseña en scripts ni se usa un keyring de clave vacía.

Paquetes de Debian y versiones en [Dependencies](dependencies.md):

```sh
sudo apt-get install --no-install-recommends \
  gh gnome-keyring libpam-gnome-keyring libsecret-tools
```

Antes de tocar PAM, revisar el login existente y respaldarlo privadamente fuera
del árbol, con una vía SSH/tty alternativa disponible. Instalar las fuentes
revisadas como archivos regulares root:root, nunca enlaces al home:

```sh
sudo install -o root -g root -m 644 config/login-keyring.pam /etc/pam.d/login-keyring
sudo install -d -o root -g root -m 755 /etc/systemd/user/gnome-keyring-daemon.service.d
sudo install -o root -g root -m 644 config/keyring-secrets-only.conf \
  /etc/systemd/user/gnome-keyring-daemon.service.d/10-secrets-only.conf
sudo install -o root -g root -m 644 config/xsession-keyring.sh \
  /etc/X11/Xsession.d/95keyring-secrets
```

En `/etc/pam.d/login`, añadir una sola vez `auth include login-keyring`
justo después de `@include common-auth`, y `session include login-keyring`
justo después de `@include common-session`. El fragmento sólo usa módulos
`optional`: no sustituye la autenticación existente. Debian mantiene aparte
el hook opcional de `common-password` para actualizar la clave del depósito.

`gcr4`, dependencia de los diálogos, habilita otro agente SSH. Deshabilitar
su activación global y conservar el agente OpenSSH que ya inicia Xsession:

```sh
sudo systemctl --global disable gcr-ssh-agent.service gcr-ssh-agent.socket
systemctl --user daemon-reload
```

El hook Xsession ejecuta `--start --components=secrets` sin bloquear el inicio
de X si falla el almacén. No lanzar agentes adicionales ni ejecutar repetidamente
`gnome-keyring-daemon --unlock` sobre un servicio ya activo.

En una sesión anterior a la instalación puede aparecer una petición inicial
para crear/desbloquear **Login**: usar la misma contraseña de Debian, no una
vacía. Coordinar la próxima entrada física para comprobar el desbloqueo PAM;
no cerrar la sesión ni reiniciar sólo para aplicar esta configuración.

Como cuenta de sesión, autorizar GitHub CLI una vez en el navegador:

```sh
gh auth login --hostname github.com --git-protocol https --web
gh auth status --hostname github.com
```

El estado debe indicar **keyring**. Si no hay almacén disponible, `gh` puede
guardar el token en texto plano: detenerse y corregirlo antes de continuar.
No usar almacenamiento inseguro ni copiar tokens entre máquinas.
Después de confirmar el backend cifrado:

```sh
gh auth setup-git --hostname github.com
git push --dry-run origin HEAD
```

Ejecutar el dry-run desde una rama de trabajo. Un push real de esa rama con un
cambio revisado verifica el flujo completo; el dry-run no actualiza refs remotas.
La sesión web y la identidad de autor por sí solas no autentican Git.

`~/.config/gh/` conserva metadatos y `~/.local/share/keyrings/` el almacén privado;
no se publican ni se importan directorios de autenticación completos. Los
archivos locales ignorados necesarios se transfieren por SSH según una lista
revisada; GitHub sólo sincroniza lo versionado. `.gitignore` no cifra archivos
ni elimina secretos ya seguidos o presentes en el historial.

## Branches, commits and pull requests

Cada bloque de trabajo empieza en una rama propia, con base revisada y
actualizada desde GitHub. Los cambios solicitados autorizan crear la rama,
hacer commits y publicarla para preparar el PR; integrar en `main` requiere
aprobación explícita. No trabajar, hacer commits ni push directamente en `main`.

Usar nombres en inglés `type/description-in-kebab-case`, por ejemplo
`feat/kitty-tabs`, `fix/network-panel` o `docs/refine-readme`; sin prefijos de
herramientas. Revisar primero el estado: preservar cambios pendientes sin
descartarlos, ocultarlos automáticamente ni cambiar de rama sobre archivos
enlazados activos sin evaluar su efecto. Con el checkout limpio y seguro:

```sh
umask 022
git status --short --branch
git switch main
git pull --ff-only
git switch -c docs/refine-readme
```

Si ya hay una rama de trabajo para el mismo bloque, continuar en ella tras
revisar su estado/base; no crear ramas paralelas para la misma tarea.

Git versiona el bit ejecutable, no la diferencia entre 644 y 664. Usar máscara
022 al crear/actualizar fuentes públicas y comprobar modos después del checkout;
las fuentes enlazadas deben conservar los modos del manifiesto. Procedimiento
de normalización acotado en [User links](editor-and-files.md#user-links).

Hacer un commit por cada bloque coherente y validado, sin mezclar cambios ajenos
ni acumular todos los commits para el final. Asunto y cuerpo en inglés con
Conventional Commits: `type(scope): description`, con scope opcional.
Ejemplo para un cambio únicamente en README, después de validar y completar
[Publication checks](#publication-checks) sobre la lista exacta:

```sh
git diff --check
git diff -- README.md
git add -- README.md
git commit -m "docs: refine README punctuation"
git push -u origin docs/refine-readme
```

Preparar el PR contra `main`, con título Conventional Commits y contenido
íntegramente en inglés. Describir el problema, resultado, validación y límites
relevantes de instalación/restauración. Para un cuerpo multilínea, preparar un
archivo temporal fuera del repositorio y usar `--body-file`:

```sh
gh pr create --base main --head docs/refine-readme \
  --title "docs: refine README punctuation" --body-file /tmp/dotfiles-pr-body.md
```

El PR queda para aprobación o rechazo; crearlo no autoriza merge. Si el cambio
aún no está listo para revisión, añadir `--draft`. No hacer force-push ni
reescribir historial. Si hay divergencia o rechazo, revisar la causa preservando
el trabajo. Tras la integración aprobada, actualizar la copia de la otra máquina
con `git pull --ff-only` desde `main` y con el checkout revisado.

## Reproducibility and deployment

Cada componente debe poder reinstalarse desde las fuentes versionadas y su guía:
dependencias directas y procedencia, versiones verificadas, destinos/modos del
manifiesto, instalación, comprobaciones y recuperación. No depender de pasos
manuales sin documentar ni versionar caches, credenciales o estado privado.
La restauración limpia sigue siendo una validación pendiente independiente.

El checkout de la portátil es la única fuente pública local. Publicar sus cambios
en GitHub; no exportar otro árbol de configuración ni conservar guías paralelas.
Los respaldos privados temporales sirven para deshacer un despliegue, no para
recuperar un disco perdido. Los datos sensibles necesitan un respaldo privado
independiente si se requiere esa recuperación; nunca se publican en GitHub.

Git sincroniza las fuentes, no sustituye su [despliegue validado](restore-guide.md).
La migración general de enlaces sigue pendiente; Neovim/Yazi usan ya el
[despliegue acotado](editor-and-files.md). Los archivos de sistema se instalan
por separado. Un pull puede cambiar directamente un archivo enlazado; revisar
los cambios antes y recargar sólo la aplicación afectada, no la sesión completa.

## Publication checks

Antes de cada commit/push, comprobar con fixtures sintéticos que las rutas privadas
están ignoradas y revisar una lista explícita de fuentes públicas. Añadir sólo
esas rutas, nunca usar force-add para archivos privados. Con el índice preparado:

```sh
git ls-files -ci --exclude-standard
git diff --cached --name-status
git diff --cached --check
git diff --cached
```

La primera orden no debe listar rutas. Revisar contenido y tipos de archivo,
no sólo nombres o patrones: un token puede estar en un archivo aparentemente
normal. Ejecutar los tests también sobre una exportación limpia del candidato.
Después de cada commit y antes del push de la rama, actualizar referencias y
revisar todo lo que saldría:

```sh
git fetch origin
git log --oneline origin/main..HEAD
git diff --stat origin/main..HEAD
```

Confirmar que la rama actual es la de trabajo y que el rango contiene sólo el
bloque previsto. La rama remota y el PR deben contener el mismo HEAD validado.

Auditar los blobs y mensajes de todos los commits salientes, no sólo el último
árbol: eliminar un secreto en un commit posterior no lo retira del historial.
Detener el push ante cualquier hallazgo sin resolver. Las exclusiones y búsquedas
de patrones son controles complementarios, no una garantía absoluta.

## Recovery

Restaurar sólo los valores previos de `user.name` y `user.email`. Si no existían,
retirarlos con `git config --global --unset-all user.name` y
`git config --global --unset-all user.email`. No reemplazar todo el archivo global
si contiene cambios posteriores o autenticación.

Para retirar esta integración, eliminar primero los dos includes de
`/etc/pam.d/login` y restaurar sólo los archivos afectados desde el backup
revisado. No eliminar un fragmento PAM todavía incluido ni reemplazar toda la
pila con una copia antigua. Perder el keyring exige autorizar GitHub otra vez;
no se recuperan tokens desde este repositorio.

## References

- [GitHub CLI secure credential storage](https://cli.github.com/manual/gh_auth_login).
- [Git identity and configuration scope](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup).
- [GitHub commit email and noreply](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address?platform=linux).
