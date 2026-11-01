# Keyboard shortcuts

Configuración i3 adaptada a los atajos principales de Omarchy, no una instalación de Omarchy/Hyprland. `Super` es la tecla Windows. El lanzador es Rofi, no Walker; sólo se ejecuta al abrirlo.

La configuración está en `config/i3-config` y la ayuda en
`config/keybindings-help.txt`. Mantener ambas junto con esta tabla.

## Applications

| Atajo | Acción |
|---|---|
| Super + Enter | Kitty |
| Super + Espacio | Rofi: buscar aplicación; escribir Power abre menú de energía |
| Super + Shift + P | Menú de energía; Power off primero, Yes preseleccionado |
| Super + D | Alias del lanzador |
| Super + N | Lista Wi-Fi con `nmtui-connect` en Kitty flotante; red activa marcada, flechas/Tab/Enter/Esc |
| Super + A | Mezclador de audio; hoy muestra ausencia de adaptador externo |
| Super + U | Lista de actualizaciones disponibles según caché local APT, sólo lectura |
| Super + Shift + Enter o B | Helium |
| Super + K | Ayuda de atajos, filtrable con teclado; Esc cierra |
| Super + W o Q | Cerrar ventana |
| Super + Shift + Q | Alias anterior para cerrar ventana |

## Windows and workspaces

| Atajo | Acción |
|---|---|
| Super + flechas | Cambiar foco |
| Super + Shift + flechas | Mover ventana |
| Super + 1…9, 0 | Escritorios 1…10 |
| Super + Shift + número | Enviar ventana a ese escritorio, sin seguirla |
| Super + F | Pantalla completa |
| Super + T | Alternar flotante/mosaico |
| Super + Shift + Espacio | Alias anterior de flotante |
| Super + J | Alternar división horizontal/vertical de i3 |
| Super + L | Ciclar división, pestañas y apilado |
| Super + E | Alias para alternar división |
| Super + B / V | División horizontal / vertical para la próxima ventana |
| Super + Ctrl + W / S | Pestañas / apilado |
| Super + Tab | Cambiar foco entre capa flotante y mosaico |
| Super + S | Mostrar/ocultar scratchpad |
| Super + Alt + S | Enviar ventana al scratchpad; Super + S la recupera |
| Super + R | Modo tamaño; flechas o H/J/K/L ajustan; Enter/Esc termina |

La navegación usa flechas; J/K/L quedan reservadas para división, ayuda y layouts. Super+Tab cambia de capa y Super+Espacio abre el lanzador. La barra se ubica arriba.

Click izquierdo en Wi-Fi, audio o contador de paquetes abre el mismo panel que Super + N, A o U. No hay acción automática de actualización; cambiar a una red nueva podría requerir autorización administrativa. La lista de redes no es un medidor de distancia: el icono refleja calidad de enlace.

## Session and applications

| Atajo | Acción |
|---|---|
| Super + Ctrl + L | Bloquear; contraseña y Enter desbloquea |
| Super + Shift + C | Recargar i3 |
| Super + Shift + R | Reiniciar i3 conservando ventanas |
| Super + Shift + E | Salir: Y confirma; N/Esc cancela |
| Ctrl + Shift + C / V | Copiar/pegar en Kitty |
| Ctrl + L | Direcciones en Helium |
| Ctrl + T / W | Abrir/cerrar pestaña del navegador |
| Ctrl + Tab / Ctrl + Shift + Tab | Siguiente/anterior pestaña del navegador |

No se implementaron el menú de administración, portapapeles universal, fondos, temas o layouts propios de Hyprland. Los atajos i3 adicionales se explicitan aquí; no se promete una copia exacta de todas las funciones de Omarchy.

## Sources and maintenance

- Fuente ejecutable: `config/i3-config`.
- Ayuda visible con Super + K: `config/keybindings-help.txt`; actualizarla junto con esta guía.
- Referencia de preferencias: [Omarchy applications bindings](https://github.com/omacom/omarchy/blob/quattro/default/hypr/bindings/applications.lua), [Omarchy window bindings](https://github.com/omacom/omarchy/blob/quattro/default/hypr/bindings/tiling.lua).

## Power menu

Entrada **Power menu** dentro del lanzador. Power off aparece primero y todas las confirmaciones tienen Yes preseleccionado (Enter confirma); Escape/No/Cancel cancelan. Guardar trabajo antes de elegir. Apagar/reiniciar/suspender usan logind/Polkit desde la sesión local activa, sin sudo ni contraseña; si no están autorizados o hay un inhibidor, se cancelan sin forzar. Suspend bloquea con i3lock antes de suspender. Cerrar sesión sólo sale de i3. Detalles y recuperación en `scripts/README.md`.
