# Repository layout

## Sources and destinations

Este árbol es la fuente de verdad de la configuración administrada del BGH A470,
no una copia completa del home ni de `/etc`.

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
copia secundaria revisada: no se utiliza automáticamente como fuente runtime.
Los ejemplos y rutas de fuentes parten de la raíz del repositorio, salvo
indicación contraria. Los README de componentes permanecen junto a sus fuentes.

## Changes

1. Inspeccionar el destino y conservar cualquier cambio existente.
2. Editar la fuente local y respaldar el destino en un directorio privado externo.
3. Instalar con propietario/modo del manifiesto; sudo sólo para archivos de sistema.
4. Validar sintaxis y comportamiento sin interrumpir aplicaciones o acceso remoto.
5. Comparar hashes, registrar el resultado técnico y sincronizar la copia secundaria.

No guardar logs, secretos, historiales o memorias en el árbol.

## Symbolic links — pending

La instalación actual usa copias. Una migración futura necesita fuentes
residentes en la portátil, enlaces por archivo, dry-run, detección de conflictos
y rollback; debe conservar archivos no administrados. Revisar antes las
divergencias de mimeapps/Codex.

La configuración privilegiada se instala por separado, root:root; nunca enlazar
`/etc` a un repositorio escribible por la cuenta de sesión.
