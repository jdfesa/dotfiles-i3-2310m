#!/bin/sh
# Run from the active physical session, never requests a real power action.
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
[ -t 0 ] && [ -t 1 ] || { echo 'Run in a local terminal (TTY required).' >&2; exit 2; }
helper=$HOME/scripts/power-action.sh
work=$(mktemp -d)
inhibitor=
cleanup() {
    if [ -n "$inhibitor" ]; then kill "$inhibitor" 2>/dev/null || true; wait "$inhibitor" 2>/dev/null || true; fi
    rm -rf "$work"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM

printf 'Session: %s\n' "${XDG_SESSION_ID:-unknown}"
loginctl show-session "${XDG_SESSION_ID:-self}" -p Active -p Remote -p Seat
for action in poweroff reboot suspend; do
    "$helper" --dry-run "$action"
    printf 'Authorized dry-run passed: %s\n' "$action"
done

# Bounded test inhibitor, not a power action; removed on completion or failure.
systemd-inhibit --what=shutdown:sleep --mode=block --who=Power-menu-verification \
    --why='Temporary safe dry-run verification' sh -c 'touch "$1"; sleep 8' sh "$work/ready" &
inhibitor=$!
attempt=0
while [ ! -f "$work/ready" ]; do
    attempt=$((attempt + 1))
    [ "$attempt" -lt 30 ] || { echo 'Test inhibitor not acquired.' >&2; exit 1; }
    sleep 0.1
done
for action in poweroff reboot suspend; do
    if systemctl --dry-run --no-ask-password --check-inhibitors=auto "$action"; then
        echo "ERROR: dry-run did not respect test inhibitor: $action" >&2
        exit 1
    fi
    printf 'Inhibited dry-run rejected: %s\n' "$action"
done
wait "$inhibitor"
inhibitor=
for action in poweroff reboot suspend; do
    "$helper" --dry-run "$action"
    printf 'Post-inhibitor dry-run passed: %s\n' "$action"
done
echo 'PASS: authorization and inhibitor checks only; no real power/lock action.'
