# Verification status

## Scope

`config/manifest.json` contiene **39 destinos administrados**. Todas las
fuentes existen en el árbol; no incluye todas las preferencias ni datos privados
de aplicaciones. Los hashes se generan, no se duplican en tablas históricas.

## Local validation — 2026-11-01

- **59/59 pruebas offline**: configuración, caches, clicks, ciclo de vida de
  procesos, menús y documentación.
- Sintaxis shell validada individualmente para inicio, helpers y diagnóstico
  de energía. Fuentes/destinos del manifiesto y enlaces Markdown presentes.
- Comentarios de i3/power-menu comparados con baseline: líneas funcionales
  idénticas. TTF y avisos upstream de fuentes sin cambios.
- Revisión acotada de patrones de secretos y datos de conexión sin coincidencias
  en el contenido candidato. No constituye auditoría exhaustiva.
- No se ejecutaron acciones reales de energía/red ni consultas a modelos.

## Previous remote verification

- **37/39** destinos coincidían en SHA256, modo y propietario.
- Diferencias preservadas: mimeapps añadió un handler y modo664 frente a644;
  Codex añadió preferencias/integraciones frente a la fuente mínima (600 correcto).
- **52/52 pruebas** correctas en Debian; i3/shell parsers y dpkg --audit correctos.
- **81/81** archivos de copia secundaria coincidían por SHA256.
- Power menu probado con `--preview` y auxiliar `--dry-run` en sesión local
  activa. Inhibidor block temporal rechazó las tres acciones; sin acciones reales.
- Fullscreen comprobado con backend nativo y GUI. Arranque con tapa abierta
  corregido tras reinicio/encendido; Wi-Fi en frío continúa pendiente.

## Pending deployment

Sincronización secundaria pendiente; SSH no disponible en la comprobación.
No hay una nueva validación de igualdad remota para esta revisión.

Revisar/respaldar antes de sincronizar:
- Guías, licencia y avisos de terceros.
- `scripts/README.md`, también instalado en `~/scripts/README.md`.
- Comentarios de `config/i3-config` y `scripts/power-menu`.
- Redacción equivalente de `config/codex-agents.md`.

No se cambiaron opciones funcionales, intervalos, paquetes o servicios.
Conservar las dos divergencias de aplicaciones y cualquier cambio remoto nuevo.

## Verification commands

Desde la raíz:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -q
python3 tools/verify-mirror.py
# En la portátil, desde una copia revisada:
python3 tools/verify-mirror.py --remote
```

El verificador sólo da SHA256; comprobar propietario/modo con `stat` y el
manifiesto. Restauración limpia y pruebas físicas pendientes: [TODO.md](TODO.md).
