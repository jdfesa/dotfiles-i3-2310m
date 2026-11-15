# Magic Trackpad battery reader provenance

Fuente: [mmarfil/magic-trackpad-battery](https://github.com/mmarfil/magic-trackpad-battery),
commit `09e72af43a803575ae537b161e6504e1f8130d76`, 2026-11-02; licencia MIT
conservada en [LICENSE](LICENSE).

| Archivo original | SHA256 |
|---|---|
| `magic-trackpad-battery` | `8cae4c35cefdb45439a40ba67a382d251975cd88c6344e802532bac62325714d` |
| `LICENSE` | `b93452a9677590d612fec93c243ae5eefb2966e83b20a5911c670fdf9423bbed` |

Ambos se conservan sin modificaciones. La integración importa sólo
`read_battery(fd)`; no ejecuta `main`, notificaciones, escritura de JSON ni el
bucle residente del proveedor. Descubrimiento local por HID exacto `004c:0265`,
independiente del nombre personalizado del dispositivo.

La regla [72-bgh-magic-trackpad.rules](../72-bgh-magic-trackpad.rules) deriva de
`72-magic-trackpad.rules` del mismo commit (SHA256 original
`2fd487cb4876ffaee57c69267ae88c314926a9860996e05fafc418503e45b6cc`). Se limita
al Trackpad 2 Bluetooth Lightning, al vendor Apple y a `hidraw`; conserva acceso
por sesión local activa mediante `uaccess`, sin permisos globales.

No se instalan el servicio, el timer de reconexión ni el módulo Waybar del
proveedor. Operación en [Bluetooth and Magic Trackpad 2](../../../docs/bluetooth-setup.md).
