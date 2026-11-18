# Screen capture

## Usage

Pulsar **Print Screen** o **Super+P**. Arrastrar para capturar una
región o hacer clic sobre una ventana. **Escape** cancela sin reemplazar el
portapapeles. Al completar la selección, pegar el PNG en una aplicación
compatible con imágenes. No se guarda automáticamente ningún archivo ni hay
edición integrada.

## Dependencies and installation

Instalar [maim](https://manpages.debian.org/trixie/maim/maim.1.en.html) y
[xclip](https://manpages.debian.org/trixie/xclip/xclip.1.en.html) desde
Debian estable; versiones en [Dependencies](dependencies.md).

```sh
sudo apt-get install --no-install-recommends maim xclip
```

i3 ejecuta `/home/jd/dotfiles-i3-2310m/scripts/capture-screenshot.py` en el
checkout (modo 755), según el [manifest.json](../config/manifest.json). Los
atajos y la ayuda usan los enlaces de [User configuration links](user-config-links.md).
El selector usa X11 sin aceleración OpenGL; no hay autostart ni historial.
Tras copiar, xclip mantiene sólo la selección actual hasta que otro proceso
toma el portapapeles; no consulta nada periódicamente.

## Verification and recovery

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p test_screenshot_capture.py
i3 -C -c "$HOME/.config/i3/config"
i3-msg reload
```

En la sesión local, abrir el selector con ambos atajos, cancelar con Escape
y comprobar que se conserva el portapapeles. Probar después una selección de
contenido de prueba y pegar el PNG. La copia sustituye el portapapeles sólo
cuando la selección termina con éxito.

Para revertir, volver a una versión revisada sin los dos atajos y recargar i3;
no hace falta reiniciar sesión. Si ya no se usan, revisar antes de retirar los
paquetes con `apt-get -s remove maim xclip`.
