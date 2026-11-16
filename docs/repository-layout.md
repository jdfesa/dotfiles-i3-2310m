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
| `wallpapers/` | Fondos versionados; condiciones en [Third-party notices](third-party-notices.md) |
| `tmp/` | Material descartable ignorado; no documentación duradera |

`config/manifest.json` contiene fuentes relativas a esta raíz y destinos reales.
El único checkout público reside en `/home/jd/dotfiles-i3-2310m`. Los scripts
se ejecutan directamente desde su carpeta `scripts/`; las rutas de aplicaciones
apuntan a las fuentes mediante enlaces simbólicos por archivo.
Los ejemplos y rutas de fuentes parten de la raíz del repositorio, salvo
indicación contraria. Los README de componentes permanecen junto a sus fuentes.

## Changes

1. Inspeccionar el destino y conservar cualquier cambio existente.
2. Editar la fuente local y respaldar el destino en un directorio privado externo.
3. Instalar con propietario/modo del manifiesto; sudo sólo para archivos de sistema.
4. Validar sintaxis y comportamiento sin interrumpir aplicaciones o acceso remoto.
5. Validar en la portátil, comparar hashes y registrar sólo el estado técnico vigente.
6. Publicar las fuentes mediante GitHub y retirar copias públicas redundantes
   después de reconciliar diferencias y verificar las referencias activas.

Para sincronizar cambios entre máquinas mediante commit/push/pull, seguir
[Git workflow](git-workflow.md).

No guardar logs, secretos, historiales o memorias en el árbol.

## Symbolic links

La configuración pública de usuario usa enlaces por archivo al checkout
residente, con dry-run, comprobación de conflictos y rollback privado. Los
scripts no se copian a otro directorio. Autenticación, historiales y estado
generado permanecen privados; un archivo que mezcle esos datos no se enlaza
al repositorio. Procedimiento en [User configuration links](user-config-links.md).

Agrupar fuentes nuevas bajo `config/<component>/`, incluso metadatos APT en
su subcarpeta `apt/`; inventarios comunes permanecen en `config/`. No mezclar
estado, caches o paquetes descargados. Reorganización heredada en [TODO](../TODO.md).

La configuración privilegiada se instala por separado, root:root; nunca enlazar
`/etc` a un repositorio escribible por la cuenta de sesión.
