# Codex CLI

## Scope

Herramienta opcional, independiente de i3. Baseline comprobada:
**Codex CLI 0.165.0**, standalone Linux x64 musl, en i3-2310M sin AVX2.
No requiere Node/npm ni compilación local. El backend interactivo es administrado
por Codex; este proyecto no instala un servicio de arranque.

Referencias oficiales: [CLI](https://learn.chatgpt.com/docs/codex/cli) y
[autenticación](https://learn.chatgpt.com/docs/auth).

## Reviewed installation

Como cuenta de sesión, no root:

```sh
umask 077
work=$(mktemp -d)
wget --https-only -q -T 30 -O "$work/install.sh" https://chatgpt.com/codex/install.sh
sh -n "$work/install.sh"
# Revisar el script descargado antes de ejecutarlo.
PATH="$HOME/.local/bin:$PATH" CODEX_NON_INTERACTIVE=1 \
  sh "$work/install.sh" --release 0.165.0
"$HOME/.local/bin/codex" --version
```

La versión es una referencia probada, no una recomendación de mantener software
obsoleto. Revisar instalador y metadatos de la publicación antes de actualizar.
Un instalador futuro puede cambiar aunque conserve URL.

Integridad registrada para esta publicación, no firma independiente:

| Elemento | SHA256 |
|---|---|
| Instalador revisado | `95d14ccaba915e52a3f0cc590638ca5ac510086ff6a23dc9ac9f77e957403a93` |
| Paquete x86_64 Linux musl | `e97c4463d7f146692a955d7b0e1c8cf48f97cd4d616cd45c5dcab2e8d9743316` |
| Binario instalado | `c06a67fd8ac76508dc78bd99ce20c9f317b8d568beda59485f3f4134df9962d5` |

## Paths and configuration

- `~/.local/bin/codex`: enlace creado por el instalador.
- `~/.codex/packages/standalone/`: releases y selección `current`.
- `~/.codex/packages/app-server-daemon/`: backend local de la interfaz.
- `config/codex-config.toml`: configuración mínima, no todas las preferencias
  runtime. Revisar diferencias antes de restaurar.
- RTK/Engram: [development-tools.md](development-tools.md).

Los binarios de proveedor se reinstalan; no están en el manifiesto.
`config/profile` añade `~/.local/bin` al login. Para una terminal existente,
usar la ruta completa o `export PATH="$HOME/.local/bin:$PATH"`; no volver a
ejecutar `.profile` indiscriminadamente porque puede iniciar X.

## Authentication and verification

Usar `codex login` y completar el flujo oficial; `codex login status` comprueba
el método local, no acceso efectivo al modelo. No copiar todo `~/.codex` de otra
máquina ni introducir sesiones, tokens o memorias en el proyecto.

En almacenamiento de archivo, `~/.codex/auth.json` es privado: directorio 700,
archivo 600, propiedad de la cuenta. Si se pierde la sesión, autenticar de nuevo;
no se restaura desde dotfiles ni se desactiva MFA como alternativa.

Pruebas ya realizadas en la plataforma de referencia:

- Versión/ayuda y consulta sintética mínima en directorio temporal vacío.
- Sandbox `:read-only`: ejecución permitida y escritura de prueba rechazada.
- CLI y backend de la interfaz con la misma versión.

En 0.165.0 la forma comprobada del diagnóstico es
`codex sandbox --permission-profile :read-only -- <comando>`.
Una prueba de conexión/sandbox no es una medición de CPU ni prueba completa
de experiencia interactiva. Cualquier prueba nueva debe limitar sus datos y
preservar los procesos/chats en uso.
