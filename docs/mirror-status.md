# Verification status

## Scope

`config/manifest.json` contiene **42 destinos administrados**. Todas las
fuentes existen en el árbol; no incluye todas las preferencias ni datos privados
de aplicaciones. Los hashes se generan, no se duplican en tablas históricas.

## Git authentication — 2026-11-02

- 66/66 pruebas offline correctas y diff sin errores de whitespace.
- 36/42 destinos coinciden en contenido, modo y propietario; seis diferencias
  previas preservadas, sin importar preferencias privadas de aplicaciones.
- Identidad noreply efectiva y helper HTTPS de gh verificados en Debian.
- Token guardado en keyring; sin token en texto plano en la configuración gh.
- Escritura/lectura sintética cifrada comprobada y elemento de prueba retirado.
- Tres nuevas fuentes de sistema coinciden en contenido, modo644 y root:root;
  directorio de drop-in755. Parser PAM, shell y comando efectivo sólo secrets
  correctos; agente SSH adicional inactivo y OpenSSH conservado.
- Commit/push real desde la portátil y pull fast-forward desde otra copia
  correctos. No se cerró sesión ni se reinició para estas comprobaciones.
- Desbloqueo automático tras nueva entrada física pendiente de coordinación;
  no se infiere del parser o de la sesión ya desbloqueada.

## Local validation — 2026-11-01

- **60/60 pruebas offline**: configuración, caches, clicks, ciclo de vida de
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

Sincronización secundaria pendiente desde la última comprobación sin SSH.
No se desplegó esta reorganización ni se verificó igualdad remota.

Revisar/respaldar antes de sincronizar:
- Guías, licencia y avisos de terceros.
- Nueva estructura `docs/` y enlaces; retirar guías antiguas de la copia
  secundaria sólo tras verificar/resguardar cualquier diferencia.
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
manifiesto. Restauración limpia y pruebas físicas pendientes: [TODO.md](../TODO.md).
