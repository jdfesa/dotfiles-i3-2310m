#!/bin/sh
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
# Read-only list. No sudo, network refresh or installation.
exec kitty --class BGH-Updates --title 'Available package updates (local APT cache)' --hold -e apt list --upgradable
