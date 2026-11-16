#!/bin/sh
# Shared by Super+N, the Wi-Fi icon, and the desktop launcher.
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8

# Kitty's exit status does not report the child status. Keep an abnormal
# nmtui exit visible in this terminal; don't leave a shell or log behind.
if [ "$#" -ne 0 ]; then
    [ "$#" -eq 1 ] && [ "$1" = --in-terminal ] || exit 64
    if nmtui-connect; then
        exit 0
    else
        status=$?
    fi
    [ "$status" -ne 130 ] || exit 0
    printf '\nWi-Fi panel exited unexpectedly (status %s).\n' "$status" >&2
    if [ -t 0 ] && [ -t 2 ]; then
        printf 'Press Enter to close.\n' >&2
        IFS= read -r ignored || :
    fi
    exit "$status"
fi

umask 077
runtime="${XDG_RUNTIME_DIR:-$HOME/.cache/i3}"
mkdir -p "$runtime"
exec 9>"$runtime/bgh-network-menu.lock"
if flock -n -E 75 9; then
    # Hold the lock in this launcher while Kitty runs, not in its descendants.
    kitty --class BGH-Networks --name BGH-Networks --title 'Wi-Fi networks' \
        --override=tab_bar_min_tabs=2 -e "$0" --in-terminal 9>&-
else
    status=$?
    [ "$status" -eq 75 ] || exit "$status"
    # A rapid repeat during startup may precede the window. In that case
    # the first request still opens it; never retry or spawn a second Kitty.
    i3-msg -q '[class="^BGH-Networks$" instance="^BGH-Networks$" title="^Wi-Fi networks$"] focus' 9>&- || :
fi
