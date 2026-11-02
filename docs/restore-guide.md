# Restore and recovery

## Scope

Restauración manual de configuración administrada, no del sistema completo.
Revisar [dependencias](dependencies.md), [manifiesto](../config/README.md) y
[estado verificado](mirror-status.md). La restauración completa en una instalación
limpia todavía no está probada.

Ejecutar los ejemplos desde la raíz del repositorio, no desde `docs/`.

No se recuperan desde aquí contraseñas, perfiles Wi-Fi con PSK, claves SSH,
sesiones Codex, memorias Engram, historiales o bases de datos personales.

## Preparation

1. Instalar Debian mínimo, configurar cuenta y acceso local; la referencia es
   `jd`/`/home/jd`. Adaptar rutas si difieren, sin ejecutar cambios de cuenta
   implícitos.
2. Verificar hardware, firmware, interfaces y sensores. Mantener tty2 y una vía
   SSH de confianza; no aceptar cambios de clave de host sin contraste físico.
3. Revisar los destinos existentes y guardar backups privados **fuera del árbol**,
   con propietario correcto y acceso restringido. Respaldos de cuentas/sistema
   sólo accesibles por root.
4. Instalar paquetes siguiendo `dependencies.md` y las guías correspondientes.
   No importar directorios ocultos completos.
5. Leer las diferencias de mimeapps/Codex antes de restaurar sus fuentes mínimas;
   no reemplazar preferencias adicionales sin revisión.

La identidad y autenticación Git se reconstruyen por separado siguiendo
[Git workflow](git-workflow.md); los tokens y el keyring no se restauran desde GitHub.

## Staged deployment

Los campos `source` del manifiesto son relativos a la raíz; `destination` es
la ruta real y `mode` el permiso Unix expresado en decimal.

- Como cuenta de sesión: configuración i3/Rofi/Kitty, fuentes, desktop entries y
  scripts en `~/scripts/` (755). Ejemplo para **un destino ya revisado/respaldado**:

  ```sh
  install -D -m 755 scripts/power-menu "$HOME/scripts/power-menu"
  ```

- `config/profile` es un modelo completo; combinar con personalizaciones de
  `.profile` y no duplicar el fragmento de inicio. `.xinitrc` usa Xsession.
- Archivos de sistema: instalación separada con sudo, root:root. Nunca symlinks
  de `/etc` a fuentes modificables desde el home.
- Red: aplicar sólo con acceso alternativo; seguir `wifi-setup.md`.
- Helium: convertir clave pública ASCII a keyring binario y verificar fingerprint,
  no comparar hashes entre formatos. Seguir `apps-setup.md`.
- Fuentes: copiar TTF/licencias, ejecutar fc-cache y comprobar el render real.
- Polkitd: necesario para el menú de energía local sin contraseña. No crear reglas
  NOPASSWD ni políticas de autorización generales.
- GRUB: instalar el drop-in sólo en hardware afectado, regenerar/validar GRUB;
  no instalar la unidad Wi-Fi diagnóstica de referencia.

Después de copiar unidades de usuario:

```sh
systemctl --user daemon-reload
systemctl --user enable --now weather-refresh.timer packages-refresh.timer
```

Los enlaces de timers/binarios creados por sus instaladores no equivalen a una
migración general de dotfiles a symlinks. Esa migración sigue pendiente.

## Verification

```sh
i3 -C -c ~/.config/i3/config
sh -n ~/.profile
sh -n ~/.xinitrc
~/scripts/status-clicks.py --run-once
~/scripts/power-menu --preview
systemctl --user status weather-refresh.timer packages-refresh.timer --no-pager
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
```

Ejecutar tests desde una copia del proyecto; los comandos anteriores son para
Debian. `tools/verify-mirror.py` compara **SHA256**, no permisos/propietarios:
comprobar estos últimos aparte con `stat` contra el manifiesto.
Verificar ventanas, atajos y datos reales; no inferir funcionamiento GUI de un
parser correcto. Coordinar cualquier prueba física de energía, red o tapa.

## Recovery

- Inicio gráfico: `touch ~/.config/i3/disable-autostart` desde tty2/SSH; corregir,
  validar y retirar sólo ese marcador. Nunca startx por SSH o como root.
- Configuración: restaurar el backup del archivo afectado, no todo el home;
  validar y recargar i3. Registrar también la reversión en la fuente local.
- Fuentes/barra: fc-cache y `i3-msg restart` conservando ventanas si hace falta.
- GRUB/tapa: [boot-troubleshooting.md](boot-troubleshooting.md).
- Cambio de cuenta: [user-migration.md](user-migration.md).
- Codex/Engram: reinstalar desde orígenes oficiales y autenticar por separado;
  no reconstruir credenciales o memorias a partir de este repositorio.
