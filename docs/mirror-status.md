# Verification status

## Current laptop state — 2026-11-16

- Un único checkout conserva las fuentes públicas. El manifiesto declara 73
  entradas:37 enlaces de usuario,20 archivos usados desde el checkout,15 archivos
  regulares de sistema y 1 base pública para estado privado. Contenidos, destinos,
  propietarios y modos públicos comprobados con el verificador nativo.
- i3, barra y gestos usan los scripts del repositorio. Panel de calendario real,
  trama de estado con audio USB y dry-run de energía verificados; las ventanas
  preexistentes y el compositor se conservan. No se probaron acciones reales
  de bloqueo, energía ni cortes de red.
- Se conservan el fondo, la apariencia 85% de Kitty y las asociaciones MIME
  existentes. [Kitty setup](kitty-setup.md), [Wallpaper](i3-setup.md#wallpaper)
  y [Desktop applications](apps-setup.md).
- Thunar mantiene el tema oscuro del lanzador y del servicio de usuario.
  [Thunar](editor-and-files.md#thunar).
- Neovim oficial con LazyVim y Yazi, GeneralPlus ALSA y Magic Trackpad 2 siguen
  disponibles. Versiones y comprobaciones de hardware en sus guías:
  [Dependencies](dependencies.md), [LazyVim setup](lazyvim-setup.md),
  [USB audio](audio-setup.md) y [Bluetooth and Magic Trackpad 2](bluetooth-setup.md).
- 212 pruebas pasan con 1 omitida. La batería cubre enlaces, diferencias revisadas,
  rollback, exclusiones privadas y rutas de ejecución. La restauración limpia,
  el rendimiento sostenido y los casos físicos de energía/batería pendientes
  se mantienen en [TODO.md](../TODO.md).
- El keyring conserva la autenticación Git. El desbloqueo tras un nuevo login
  físico sigue pendiente de comprobación coordinada.

## Source and deployment

GitHub es la fuente de verdad y sincroniza el único checkout local mediante
commit/push/pull. SSH administra/despliega y transfiere únicamente el material
privado necesario. La portátil es el destino principal de validación.

Los destinos públicos de usuario se enlazan al checkout y los scripts se
invocan desde él. Las excepciones privadas y la instalación regular root se
describen en [User configuration links](user-config-links.md).

## Verification commands

Desde el checkout de la portátil:

```sh
PYTHONDONTWRITEBYTECODE=1 \
NVIM_TEST_MINI_FILES="$HOME/.local/share/nvim/site/pack/vendor/start/mini.files" \
  python3 -m unittest discover -s tests -q
python3 tools/install-mini-files.py --check
python3 tools/link-user-config.py
python3 tools/verify-mirror.py --remote --check
dpkg --audit
```

El verificador comprueba los destinos públicos y omite el estado privado
marcado como overlay en el manifiesto. Pendientes concretos en [TODO](../TODO.md); cambios técnicos
en [Changelog](../CHANGELOG.md), sin acumular snapshots de verificaciones anteriores.
