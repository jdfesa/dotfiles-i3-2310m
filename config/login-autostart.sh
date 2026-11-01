# BGH A470: start i3 on local tty1 login.
# Do not start X over SSH, on recovery consoles, or inside a graphical session.
# Keep the shell if startx fails, so errors can be read and repaired.
if [ -z "${DISPLAY:-}" ] &&
   [ -z "${SSH_CONNECTION:-}" ] &&
   [ "$(tty 2>/dev/null)" = "/dev/tty1" ] &&
   [ ! -e "$HOME/.config/i3/disable-autostart" ]; then
    startx
fi
