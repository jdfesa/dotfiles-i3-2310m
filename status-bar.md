# Status bar

## Appearance

i3bar superior, opaca y compacta, Catppuccin Mocha; **JetBrainsMono Nerd Font
Mono Regular 10**. Sin blur/compositor. Sólo workspaces existentes, manteniendo
los diez accesibles por teclado. Textos en inglés, hora 24 h y temperaturas °C.

| Bloque | Dato / acción |
|---|---|
| Clima | Icono de condición + temperatura; sin ciudad |
| ↑ / ↓ | Tráfico `wlp2s0` por diferencia de contadores; K=KiB/s, M=MiB/s |
| RAM / CPU | Uso RAM según MemAvailable / uso CPU agregado |
| Temperatura | Sensor CPU coretemp/x86_pkg_temp; no temperatura exterior |
| Disco | Espacio disponible de `/`; G=GiB |
| Paquetes | Candidatos APT locales; click o Super+U abre lista |
| Audio | Nivel/mute si existe mixer; si no, `No audio`; click/Super+A |
| Wi-Fi | Sólo icono por calidad, sin SSID/cifra; click/Super+N |
| Batería | Estado real; `No battery` si no existe dispositivo |
| Reloj | Fecha en inglés y hora local |

Falta de audio/batería no se representa como 0%. Tarjeta/mixer externos y
reproducción siguen pendientes. Redes se abre con `nmtui-connect` en Kitty;
mantiene la autorización normal de NetworkManager.

## Scheduled work and events

1. `status-bar.sh` selecciona sensor/audio al iniciar y ejecuta i3status.
2. i3status obtiene datos cada **10 s**, sin shell por indicador.
3. `status-clicks.py` es un adaptador Python **residente**. Espera eventos con
   selectores, formatea indicadores y lee dos contadores sysfs de tráfico en el
   tick existente; no consulta Internet ni nmcli cada tick.
4. Los clicks sólo abren helpers fijos; no interpolan SSID o datos arbitrarios
   como comandos.
5. Sin ALSA, se genera una variante temporal en `~/.cache/i3/`; no se altera la
   fuente ni se repiten consultas a un mixer ausente.

## Caches

- Clima: Open-Meteo HTTPS, centro público configurable de Orán en
  `config/weather.json`, sin geolocalización. Timer **30 min** con desfase;
  timeout de petición 20 s y servicio 30 s, validación y escritura atómica.
  Cache fallida de hasta 3 h se marca `~`; vencida/ausente, `--°C`.
- Paquetes: cada **6 h**, `LC_ALL=C apt-get --simulate upgrade` sobre índices
  existentes. No apt update, descargas, instalaciones ni sudo. Fallo: `?`.
  `0` sólo significa cero candidatos en los índices disponibles.
- Ambos refrescos son oneshot `Nice=10`, `NoNewPrivileges=yes`, umask 0077.
  No son clientes Python residentes.

Después de actualizar manualmente los índices:

```sh
systemctl --user start packages-refresh.service
```

La lista Super+U también es de sólo lectura. Fuentes y ciclo de vida:
[scripts/README.md](scripts/README.md).

## Troubleshooting

- Muestra acotada: `~/scripts/status-clicks.py --run-once`.
- Error tras fullscreen: conservar SIGSTOP/SIGCONT del protocolo; i3bar señaliza
  todo el grupo. No anunciar USR1/USR2 ni desactivar la pausa con stop_signal=0.
- Si un reload conserva el adaptador antiguo, `i3-msg restart` renueva i3bar
  manteniendo ventanas.
- Cajas en lugar de iconos: `fc-match`, `fc-cache ~/.local/share/fonts` y renovar
  i3bar; no instalar colecciones de fuentes adicionales como primer paso.
- `tools/capture-bar.py` captura sólo la franja superior; imágenes/logs fuera
  del repositorio.
- Pruebas: `tests/test_status_lifecycle.py` cubre el grupo shell/adaptador/backend.
  También pasaron ciclos con i3status nativo y fullscreen gráfico.

Muestras cortas de CPU/RSS no constituyen un benchmark ni justifican prometer
un consumo fijo. Mantener los intervalos y medir tareas representativas.

Referencias: [i3status](https://i3wm.org/docs/i3status.html),
[protocolo i3bar](https://i3wm.org/docs/i3bar-protocol.html),
[Open-Meteo](https://open-meteo.com/en/docs).
