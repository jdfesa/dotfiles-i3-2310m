# Repository layout

## Sources and destinations

GitHub conserva la fuente de verdad de este árbol de configuración
administrada del BGH A470; cada máquina mantiene una copia de trabajo.
No es una copia completa del home ni de `/etc`.

| Ruta | Responsabilidad |
|---|---|
| `README.md` | Objetivo, hardware y acceso a las guías |
| `AGENTS.md` | Criterios de trabajo y convenciones |
| `CHANGELOG.md` / `TODO.md` | Cambios técnicos / trabajo pendiente |
| `LICENSE` | Licencia del material propio |
| `docs/` | Guías temáticas, dependencias y avisos de terceros |
| `config/` | Configuración y manifiesto de destinos/modos |
| `scripts/` | Ejecutables usados por i3, desktop entries o timers |
| `tools/` | Utilidades manuales; no se instalan en el arranque |
| `tests/` | Regresiones con fixtures y acciones simuladas |
| `tmp/` | Material descartable ignorado; no documentación duradera |

`config/manifest.json` contiene fuentes relativas a esta raíz y destinos reales.
Los scripts se instalan en `/home/jd/scripts/`. `/home/jd/setup-guide` es una
snapshot secundario del commit vigente: no se edita ni se utiliza automáticamente
como fuente runtime. No conservar guías antiguas a su lado.
Los ejemplos y rutas de fuentes parten de la raíz del repositorio, salvo
indicación contraria. Los README de componentes permanecen junto a sus fuentes.

## Changes

1. Inspeccionar el destino y conservar cualquier cambio existente.
2. Editar la fuente local y respaldar el destino en un directorio privado externo.
3. Instalar con propietario/modo del manifiesto; sudo sólo para archivos de sistema.
4. Validar sintaxis y comportamiento sin interrumpir aplicaciones o acceso remoto.
5. Validar en la portátil, comparar hashes y registrar sólo el estado técnico vigente.
6. Sincronizar fuentes mediante GitHub y regenerar el snapshot secundario.

Para sincronizar cambios entre máquinas mediante commit/push/pull, seguir
[Git workflow](git-workflow.md).

No guardar logs, secretos, historiales o memorias en el árbol.

## Secondary snapshot

Desde el checkout limpio de la portátil actualizado mediante GitHub:

```sh
git pull --ff-only
python3 tools/sync-secondary.py                     # revisar cambios y retiros
backup="$HOME/.local/state/bgh-config-backups/secondary-$(date -u +%Y%m%dT%H%M%SZ)"
python3 tools/sync-secondary.py --apply --backup-dir "$backup"
python3 tools/sync-secondary.py --check
```

El auxiliar exporta sólo archivos del commit, nunca archivos privados ignorados
ni `.git`. Reemplaza copias públicas desactualizadas y retira guías antiguas ya
movidas a `docs/`, el nombre anterior del generador de iconos y metadatos/cache
generados. Un archivo extra desconocido o enlace exige revisión privada previa;
no se publica ni se elimina a ciegas.

Antes de escribir guarda el estado afectado en un directorio700 externo con
journal600. La comparación final exige contenidos, modos y conjunto exacto de
archivos del commit. No crea otra copia de trabajo ni almacena estados anteriores
en el snapshot. Conservar un baseline revisado de recuperación; retirar respaldos
temporales superados sólo después de verificarlo. Sin cambios no genera backups.

## Symbolic links

Neovim/Yazi usan seis enlaces por archivo con fuentes residentes, dry-run,
conflictos y rollback privado. Procedimiento único en
[Editor and file management](editor-and-files.md). Los componentes anteriores
siguen como copias; revisar sus divergencias antes de ampliar la migración.

Agrupar fuentes nuevas bajo `config/<component>/`, incluso metadatos APT en
su subcarpeta `apt/`; inventarios comunes permanecen en `config/`. No mezclar
estado, caches o paquetes descargados. Reorganización heredada en [TODO](../TODO.md).

La configuración privilegiada se instala por separado, root:root; nunca enlazar
`/etc` a un repositorio escribible por la cuenta de sesión.
