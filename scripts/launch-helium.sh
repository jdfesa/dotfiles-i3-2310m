#!/bin/sh
# Apply the native GTK dialog theme before the browser process starts.
export GTK_THEME=Adwaita:dark
exec /usr/bin/helium "$@"
