#!/bin/sh
# Shared by Super+N and the Wi-Fi icon. No saved/embedded passwords.
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
runtime="${XDG_RUNTIME_DIR:-$HOME/.cache/i3}"
mkdir -p "$runtime"
# Avoid duplicate dialogs after rapid clicks; keep the lock while Kitty runs.
exec flock -n "$runtime/bgh-network-menu.lock" \
    kitty --class BGH-Networks --title 'Wi-Fi networks' -e nmtui-connect
