# User configuration links

## Source of truth

El único checkout de configuración pública es
`/home/jd/dotfiles-i3-2310m`, sincronizado con GitHub. Las rutas que exigen las
aplicaciones contienen enlaces simbólicos por archivo hacia este checkout.
Los scripts se ejecutan desde `scripts/` dentro del repositorio; no necesitan
otra carpeta con copias de sus fuentes. Las dependencias instaladas, caches y
datos privados no son fuentes de configuración del proyecto.

Los destinos y modos se declaran en [manifest.json](../config/manifest.json):

- `deployment=symlink`: enlace de usuario a una fuente pública revisada.
- `deployment=in-place`: script o documentación ejecutado/leído en el checkout.
- `deployment=private-overlay`: base pública para un archivo que también guarda
  estado privado; conservar y combinar ese estado local, sin enlazarlo a Git.
- Sin `deployment`: archivo de sistema instalado regular, root:root, mediante
  sudo autenticado. Nunca enlazar `/etc` a un home modificable sin sudo.

`~/.codex/config.toml` mezcla preferencias con rutas de proyectos, confianza,
hashes de hooks y datos generados del runtime. Su base pública se conserva en
`config/codex-config.toml`; el archivo efectivo es privado y no se enlaza.
Credenciales, keyrings, memorias e historiales tampoco se enlazan ni versionan.

## Installation

Clonar o actualizar las fuentes desde GitHub en la ruta indicada; la guía de
[Git workflow](git-workflow.md) separa autoría y autenticación. Instalar las
dependencias según [Dependencies](dependencies.md). No mover el checkout una
vez activo: los enlaces y lanzadores usan su ruta estable.

Revisar cada destino y reconciliar diferencias públicas antes del despliegue.
Una diferencia no se descarta para hacer coincidir hashes. Revisar también las
fuentes antes de normalizar sus modos: 644 para configuración pública y 755
para ejecutables, salvo los modos más restrictivos declarados en el manifiesto.

Como `jd`, desde la raíz:

```sh
umask 022
python3 tools/link-user-config.py
backup="$HOME/.local/state/bgh-config-backups/links-$(date -u +%Y%m%dT%H%M%SZ)"
python3 tools/link-user-config.py --apply --backup-dir "$backup"
python3 tools/link-user-config.py
```

El primer comando sólo prepara el plan. El auxiliar rechaza archivos distintos,
enlaces inesperados, padres enlazados y fuentes con propietario/modo incorrecto.
Sólo sustituye copias regulares idénticas o crea destinos ausentes. Antes de
reemplazar guarda copias y un journal en un directorio nuevo y privado700,
externo al checkout. Los archivos privados quedan600. El resultado esperado
en la segunda revisión es `unchanged` para todos los enlaces.

Instalar la configuración de sistema por separado según su guía. Después de
cambiar las unidades de usuario, ejecutar `systemctl --user daemon-reload`.
Validar la configuración i3 antes de recargarla; renovar sus auxiliares sólo
cuando corresponda y conservar todas las ventanas. No ejecutar `.profile` ni
iniciar X desde SSH para aplicar enlaces.

## Validation

```sh
python3 tools/link-user-config.py
python3 tools/verify-mirror.py --remote --check
i3 -C -c "$HOME/.config/i3/config"
sh -n "$HOME/.profile" "$HOME/.xinitrc"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

Los enlaces tienen el modo del sistema para symlinks; comprobar el modo y
propietario de la fuente, no intentar aplicar chmod al enlace. Comprobar también
la aplicación afectada y sus rutas reales. Un parser correcto no prueba una
restauración completa ni rendimiento sostenido.

## Maintenance and recovery

Editar la fuente versionada. Un cambio de rama o un pull puede modificar
inmediatamente la configuración enlazada: revisar el diff antes y recargar
sólo lo necesario. No retirar una fuente mientras conserve destinos activos.
Si una aplicación reemplaza su enlace por un archivo nuevo, revisar y recuperar
el cambio útil antes de volver a enlazar.

Para revertir una migración sin tocar las fuentes ni archivos ajenos:

```sh
python3 tools/link-user-config.py --rollback "$backup/journal.json"
```

El auxiliar verifica los hashes y el destino del enlace antes de restaurar.
Para revertir contenido ya publicado, usar el flujo de ramas y PR habitual;
no reescribir `main` ni reemplazar el checkout completo.

Los respaldos temporales permiten deshacer un despliegue y pueden contener
estado privado. No se publican ni forman otra fuente editable; retirar los
obsoletos después de verificar la configuración y conservar sólo el material
privado necesario. GitHub permite recuperar las fuentes públicas tras perder
el disco; los datos sensibles requieren su propio respaldo privado si se
necesita esa protección.
