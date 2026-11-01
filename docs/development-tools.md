# Development tools

## Selection and installation

RTK 1.1.0 y Engram 3.6.0 se instalan como binarios nativos oficiales, sin Cargo,
Go o npm. Son herramientas opcionales; no se instala un stack completo,
distribución de editor, LSP o watcher como efecto lateral.
[Inventario y dependencias](dependencies.md).

```sh
python3 tools/install-user-tools.py
~/.local/bin/rtk --version
~/.local/bin/engram version
```

Ejecutar en Linux amd64 como cuenta de sesión. El instalador fija URLs/SHA256
de [RTK](https://github.com/rtk-ai/rtk/releases/tag/v1.1.0) y
[Engram](https://github.com/Gentleman-Programming/engram/releases/tag/v3.6.0),
extrae sólo el ejecutable esperado y rechaza binarios existentes diferentes.
No usa sudo ni compila. Un checksum del mismo proveedor comprueba integridad,
no constituye una firma independiente.

## Minimal integration

| Fuente | Destino bajo el home / función |
|---|---|
| `config/codex-config.toml` | `.codex/config.toml`; TUI, MCP stdio y marketplace |
| `config/codex-agents.md` | `.codex/AGENTS.md`; restricciones CPU/seguridad |
| `config/codex-rtk.md` | `.codex/RTK.md`; instrucciones de salida |
| `config/codex-hooks.json` | `.codex/hooks.json`; hook RTK nativo |
| `config/rtk-config.toml` | `.config/rtk/config.toml`; telemetría desactivada |

Modo 600, propiedad de la cuenta. Respaldar/combinar cambios existentes; no
sobrescribir la configuración ampliada de Codex con la fuente mínima.
El plugin de proveedor se recrea, no se copia como script propio.

Para reconstruir el marketplace fijado, antes del setup:

```sh
export PATH="$HOME/.local/bin:$PATH"
codex plugin marketplace add Gentleman-Programming/engram --ref v3.6.0
engram setup codex
```

Plugin comprobado: **0.1.5**, tag `v3.6.0`, commit
`98912f811c90428e83a6aac99fa439bedb4b268f`. Registrar primero el marketplace:
si el cache está ausente, setup sin ese paso puede materializar `main`.
Si ya hay otra fuente/ref, revisar antes de corregir; no eliminar otros plugins.

Setup registra MCP por ruta absoluta y recrea el protocolo/plugin.
No usar `model_instructions_file` ni `experimental_compact_prompt_file` como
integración aditiva: reemplazan instrucciones base.

## Processes and background overhead

- RTK: hook nativo que envuelve comandos compatibles; sin daemon propio.
  En **1.1.0**, salida cruda: `rtk bypass <comando>`. Otras versiones pueden
  usar otro subcomando; no copiar instrucciones entre hosts sin comprobar.
- Engram: MCP stdio bajo demanda y helper HTTP oficial de hooks en
  **127.0.0.1:7437**, no accesible por LAN. Puede permanecer después de cerrar
  una ventana; no se promete coste cero.
- No se instala servicio de boot, timer, cloud sync o indexador para estas
  herramientas. No abrir el helper a otras interfaces.
- Cerrar/reabrir sólo Codex cuando corresponda cargar cambios; no reiniciar i3
  o Debian ni terminar backends con tareas activas.

RTK no concede permisos adicionales: se conservan sandbox/aprobaciones y no se
crean reglas de confianza generales para comandos envueltos.

## Verification and private data

Versiones/binarios, hook RTK sintético y MCP Engram con SQLite temporal aislada
fueron comprobados. `engram doctor --json` pasó 10/10 en el almacén nuevo.
Estas pruebas no acreditan el funcionamiento de todos los hooks con memorias
reales ni son benchmarks de carga de desarrollo.

```sh
rtk init --global --codex --show
codex mcp get engram
engram doctor --json
```

No publicar resultados sin revisión. `~/.engram/` contiene memorias/sesiones;
los directorios de RTK pueden contener estadísticas y salidas crudas.
Mantenerlos privados y excluidos, igual que `~/.codex/auth.json`. Una prueba que
envíe memorias a un modelo requiere un alcance y aprobación específicos.
