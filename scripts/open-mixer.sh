#!/bin/sh
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
exec "$HOME/scripts/status-panel.py" audio
