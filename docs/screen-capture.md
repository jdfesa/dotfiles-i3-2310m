# Screen capture

## Usage

Pulsar **Print Screen** o **Super+Ctrl+Alt+C**. Arrastrar para seleccionar una
región o pulsar **Ctrl+A** para seleccionar todo el escritorio. La selección
se ve antes de guardar y se puede anotar con flechas, rectángulos o texto.

Pulsar **Accept** (el botón con la marca de verificación) o **Enter** para
guardar, con o sin anotaciones. La captura se guarda como PNG fechado en
`~/Pictures/Screenshots` y se copia al portapapeles. La carpeta se crea si
no existe al guardar la primera captura. **Escape** cancela sin guardar
ni reemplazar el portapapeles.

## Dependencies and installation

Instalar [Flameshot](https://packages.debian.org/trixie/flameshot) y
[xclip](https://manpages.debian.org/trixie/xclip/xclip.1.en.html) desde
Debian estable; versiones en [Dependencies](dependencies.md).

```sh
sudo apt-get install --no-install-recommends flameshot xclip
```

i3 ejecuta `/home/jd/dotfiles-i3-2310m/scripts/capture-screenshot.py` en el
checkout (modo 755), según el [manifest.json](../config/manifest.json). Los
atajos y la ayuda usan los enlaces de [User configuration links](user-config-links.md).
El script abre `flameshot gui --raw` en X11 sólo al pulsar el atajo. No
solicita servicios de captura ni carga en línea. Recibe el PNG al aceptar, lo
guarda con modo 600 y sin sobrescribir capturas previas. Tras copiar, xclip
mantiene sólo la selección actual hasta que otro proceso toma el
portapapeles; no hay historial ni sondeo.

## Verification and recovery

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_screenshot_capture.py
i3 -C -c "$HOME/.config/i3/config"
i3-msg reload
```

En la sesión local, abrir el selector con ambos atajos y cancelar con Escape;
no debe aparecer un archivo ni cambiar el portapapeles. Con contenido de
prueba, comprobar selección de región y escritorio, anotar una captura
y aceptar. Abrir el PNG en `~/Pictures/Screenshots` y probar a pegarlo.

Para revertir, volver a una versión revisada sin los dos atajos y recargar i3;
no hace falta reiniciar sesión. Si ya no se usan, revisar antes de retirar los
paquetes con `apt-get -s remove flameshot xclip`. Las capturas previamente
guardadas permanecen en la carpeta.
