# Development and diagnostic tools

Estas utilidades se ejecutan manualmente desde una copia del proyecto; no se
enlazan a i3 ni se habilitan en el arranque. No confundirlas con `scripts/`.

| Fuente | Función / precaución |
|---|---|
| `tools/verify-mirror.py` | Imprime SHA256 de fuentes; `--remote` lee destinos del manifiesto. No comprueba propietario/modo |
| `tools/verify-power-session.sh` | Terminal física: autorización y systemctl sólo --dry-run, con inhibidor block temporal 8 s; sin lock/energía real |
| `tools/install-user-tools.py` | Instala RTK/Engram oficiales fijados, Linux amd64 sin root; no reemplaza binarios distintos |
| `tools/build-status-icons.py` | Genera cinco glifos Wi-Fi originales con fontTools; sólo entorno de desarrollo |
| `tools/capture-bar.py` | X11: PPM de los 32 píxeles superiores en stdout; guardar captura fuera del árbol |
| `tools/probe-wifi-keys.py` | Captura acotada y filtrada Fn/F11/radio; requiere coordinación y acceso explícito a dispositivos; sin inyección |
| `tools/relocate-user-home.py` | Mantenimiento específico joe→jd; inspección por defecto, allowlist y `--apply` protegido. No crea/renombra cuentas |

Python usa biblioteca estándar salvo el generador de fuentes.
`requirements-font-build.txt` fija fontTools para ese generador; no se instala
como dependencia de la barra.

La unidad `config/wifi-boot-state.service` es sólo referencia de un diagnóstico
retirado y está fuera del manifiesto. No reinstalarla como solución Wi-Fi.

## Offline verification

Desde la raíz:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
python3 tools/verify-mirror.py
```

En un host de administración con RTK, usar el passthrough de su versión
(por ejemplo `rtk proxy python3 ...`); en la RTK 1.1.0 de la portátil es
`rtk bypass`. No sustituir subcomandos sin comprobar la versión.

Las pruebas de energía usan comandos simulados; las de clima/paquetes incluyen
fallos sintéticos esperados. Los tests no prueban un formateo/restauración completo.
Mantener descargas, registros, imágenes y resultados privados fuera del proyecto.
