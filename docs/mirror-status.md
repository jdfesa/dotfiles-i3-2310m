# Verification status

## Current laptop state — 2026-11-02

- Neovim Debian, Yazi APT stable firmado y sólo mini.files fijado instalados.
  [Versiones](dependencies.md) y [operación/recuperación](editor-and-files.md).
- El manifiesto contiene **51 destinos**: **45 coinciden** en contenido, modo y
  propietario. Los seis enlaces nuevos apuntan al checkout residente; los tres
  archivos APT nuevos son regulares root:root644. Dry-run repetido sin cambios;
  dpkg --audit vacío.
- Se mantienen preferencias de mimeapps/Codex fuera del baseline público mínimo.
  Las otras diferencias existentes son comentarios/documentación de i3,
  power-menu y README de scripts. No se reemplazan preferencias para forzar hashes.
- La batería cubre configuración, instalación, rollback, snapshot secundario,
  arranque Yazi en pseudoterminal y operaciones mini.files en fixtures aislados.
  La ejecución con el módulo instalado se realiza en Debian; el host de
  administración omite esa prueba si no tiene el módulo.
- Arranque con la configuración Neovim instalada real correcto; escritura
  conserva enlaces sintéticos. No se usaron documentos personales ni se
  reiniciaron i3, sesión, red, audio o energía.
- Autenticación Git HTTPS mediante gh/keyring cifrado verificada; desbloqueo
  tras nueva entrada física sigue pendiente de coordinación.
- Comodidad visual local, carga representativa con navegador y restauración
  limpia pendientes; no se infieren de estas pruebas.

## Source and secondary snapshot

GitHub es la fuente de verdad y sincroniza los checkouts mediante commit/push/pull.
SSH administra/despliega y transfiere únicamente el material privado necesario.
La portátil es el destino principal de validación.

La copia secundaria se regenera del commit limpio: mismos archivos, contenidos y
modos, sin guías antiguas ni caches/metadatos de transferencia. No se mantiene como
otro árbol editable ni se conservan divergencias históricas. Procedimiento y
baseline privado externo en [Repository layout](repository-layout.md#secondary-snapshot).

## Verification commands

Desde el checkout de la portátil:

```sh
PYTHONDONTWRITEBYTECODE=1 \
NVIM_TEST_MINI_FILES="$HOME/.local/share/nvim/site/pack/vendor/start/mini.files" \
  python3 -m unittest discover -s tests -q
python3 tools/install-mini-files.py --check
python3 tools/link-user-config.py
python3 tools/verify-mirror.py --remote
python3 tools/sync-secondary.py --check
dpkg --audit
```

El verificador de destinos sólo da SHA256; comprobar también propietario/modo
según el manifiesto. Pendientes concretos en [TODO](../TODO.md); cambios técnicos
en [Changelog](../CHANGELOG.md), sin acumular snapshots de verificaciones anteriores.
