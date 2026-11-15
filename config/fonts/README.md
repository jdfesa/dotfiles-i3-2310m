# JetBrains Mono Nerd Fonts

Mono Regular/Bold y Propo Regular, instaladas para la cuenta de sesión;
sin colección completa ni daemon de fuentes.

- Origen: [Nerd Fonts v3.5.1 / JetBrains Mono / Ligatures](https://github.com/ryanoasis/nerd-fonts/tree/v3.5.1/patched-fonts/JetBrainsMono/Ligatures).
- JetBrains Mono base: 2.304; familia larga verificada `JetBrainsMono Nerd Font Mono` (`JetBrainsMono NFM` también figura en los metadatos).
- Los tres TTF provienen del tag oficial por HTTPS, sin modificar el archivo del proveedor.
- `OFL.txt`: licencia de JetBrains Mono. `UPSTREAM.md`: procedencia y licencias de los conjuntos de iconos integrados.
- Kitty desactiva ligaduras para que los comandos mantengan su representación literal. No se instalaron cursivas separadas.
- La fuente Wi-Fi original `bgh-status-icons.ttf` se conserva como complemento de 2 KB, explícito en Pango; los demás iconos provienen de Nerd Fonts.

SHA-256 observado en esta descarga (integridad del espejo, no firma independiente):

```text
f2a5ea6cfab397445ffab00c0370927b66d61e560a05db5db271b42006381c1a  JetBrainsMonoNerdFontMono-Regular.ttf
bfcf9a917276ffc058867d87cbc8a5b2f1ab0f4b710e9170dc02763ccb80bd4b  JetBrainsMonoNerdFontMono-Bold.ttf
8a2803de76ad18ed82f465dfd17130032c34c031b263179d3047a547c7caa460  jetbrains-mono-nerd-font-propo-regular.ttf
```

## Proportional icons

`JetBrainsMono Nerd Font Propo` Regular conserva la proporción de los iconos
anchos en Pango. Se usa a tamaño 12 para clima, métricas y audio; el texto
conserva Mono 10 y Wi-Fi su fuente específica. No cambia Rofi ni Kitty.

- [Official Propo asset](https://raw.githubusercontent.com/ryanoasis/nerd-fonts/v3.5.1/patched-fonts/JetBrainsMono/Ligatures/JetBrainsMonoNerdFontPropo-Regular.ttf).
- Archivo sin modificar, 2 571 412 bytes (aproximadamente 2,45 MiB), guardado
  con nombre kebab-case. Añadido y contrastado con el tag el 2026-11-15.
- `OFL.txt` y `UPSTREAM.md` coinciden byte por byte con los avisos de ese tag.
- Destino regular, propietario `jd:jd`, modo 644, declarado en
  [Manifest](../manifest.json). Instalación y recuperación en
  [Status bar](../../docs/status-bar.md#installation-and-recovery).
