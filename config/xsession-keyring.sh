# Optional secrets initialization for Debian Xsession; never block X startup.
if [ -n "${XDG_RUNTIME_DIR:-}" ] && [ -x /usr/bin/gnome-keyring-daemon ]; then
    /usr/bin/gnome-keyring-daemon --start --components=secrets \
        --control-directory="$XDG_RUNTIME_DIR/keyring" >/dev/null 2>&1 || :
fi
