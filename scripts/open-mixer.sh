#!/bin/sh
set -eu
export LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
if [ ! -d /sys/class/sound ] || ! grep -q '\[.*\]' /proc/asound/cards 2>/dev/null; then
    exec kitty --class BGH-Mixer --title 'Audio mixer' --hold -e printf '%s\n' 'No audio device detected.' 'Check firmware/BIOS audio settings; no volume percentage is available.'
fi
exec kitty --class BGH-Mixer --title 'Audio mixer' -e alsamixer
