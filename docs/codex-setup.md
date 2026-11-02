# Codex CLI

## Scope

Standalone oficial Linux x64 musl, compatible con i3-2310M sin AVX2; sin
Node/npm ni compilación local. El lanzador del proyecto requiere Python 3.
El backend se inicia bajo demanda, sin servicio de arranque.
Versión verificada: [dependencies.md](dependencies.md).

Referencias oficiales: [CLI](https://learn.chatgpt.com/docs/codex/cli) y
[autenticación](https://learn.chatgpt.com/docs/auth).

## Installation

Como cuenta de sesión, desde la raíz del proyecto:

```sh
umask 077
work=$(mktemp -d)
wget --https-only -q -T 30 -O "$work/install.sh" https://chatgpt.com/codex/install.sh
sh -n "$work/install.sh"
# Revisar el instalador y los metadatos de la publicación antes de ejecutarlo.
PATH="$HOME/.local/bin:$PATH" CODEX_NON_INTERACTIVE=1 \
  sh "$work/install.sh" --release 0.165.0
```

SHA256 de la publicación comprobada; no sustituyen una firma independiente:

| Elemento | SHA256 |
|---|---|
| Instalador | `95d14ccaba915e52a3f0cc590638ca5ac510086ff6a23dc9ac9f77e957403a93` |
| Paquete x86_64 Linux musl | `e97c4463d7f146692a955d7b0e1c8cf48f97cd4d616cd45c5dcab2e8d9743316` |
| Binario | `c06a67fd8ac76508dc78bd99ce20c9f317b8d568beda59485f3f4134df9962d5` |

Instalar el lanzador sin escribir a través del enlace creado por el proveedor:

```sh
umask 022
mkdir -p "$HOME/setup-backups"
backup=$(mktemp -d "$HOME/setup-backups/codex-launch.XXXXXX")
cp -P "$HOME/.local/bin/codex" "$backup/codex"
staging=$(mktemp "$HOME/.local/bin/.codex-launch.XXXXXX")
install -m 755 scripts/codex-launch.py "$staging"
mv -T "$staging" "$HOME/.local/bin/codex"
```

## Files and configuration

- `~/.local/bin/codex`: lanzador del proyecto, modo 755.
- `~/.codex/packages/standalone/current/`: paquete oficial de la CLI.
- `~/.codex/packages/app-server-daemon/`: backend administrado por Codex.
- `config/codex-config.toml`: base mínima; revisar diferencias antes de restaurar.

Destinos y modos en [manifest.json](../config/manifest.json); integración
RTK/Engram en [development-tools.md](development-tools.md). `config/profile`
añade `~/.local/bin` al login; no volver a ejecutar `.profile` para actualizar
PATH, porque puede iniciar X.

## Authentication

`codex login` completa el flujo oficial. Con almacenamiento de archivo, la
sesión persiste en `~/.codex/auth.json`: directorio 700, archivo 600 y propietario
de la cuenta. Credenciales y backups privados quedan fuera de Git.

Verificar la cuenta esperada en el backend efectivo; `codex login status` sólo
confirma el método de autenticación. Para importar una sesión propia, seguir la
guía oficial: confirmar origen/destino, transferir sólo la caché necesaria por
SSH verificado y respaldar el destino. Una sustitución requiere recarga
coordinada del backend si mantiene otra sesión en memoria. No copiar todo
`~/.codex` ni automatizar transferencias de credenciales en cada inicio.

## Recovery

En 0.165.0, un alias de socket persistente con destino perdido en `/tmp` puede
provocar `File exists (os error 17)` al arrancar el backend.
`scripts/codex-launch.py` recupera sólo el alias obsoleto bajo el lock de arranque,
validando propietario, directorios y destino. Conserva sockets activos y ejecuta
el binario oficial mediante `exec`, sin modificar autenticación ni paquetes.

Una actualización oficial puede reemplazar el lanzador: revisar si sigue siendo
necesario y reinstalarlo. Para revertir, restaurar el enlace respaldado mediante
rename, sin sobrescribir el binario. `codex --no-daemon` permite diagnosticar sin
el servidor compartido.

## Verification

```sh
codex --version
codex login status
codex doctor --summary
codex sandbox --permission-profile :read-only -- true
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_codex_launcher.py -q
```

La API `account/read` con `refreshToken=false` permite comprobar la cuenta
efectiva sin forzar una renovación. Validación tras reinicio: [TODO.md](../TODO.md).
