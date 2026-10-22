#!/usr/bin/env bash
# Dynamic blur switcher for Picom
set -euo pipefail

PICOM_CONF="$HOME/.config/picom/picom.conf"
notif="$HOME/.config/swaync/images"

if grep -q 'blur-method = "none";' "$PICOM_CONF" 2>/dev/null; then
    sed -i 's/blur-method = "none";/blur-method = "dual_kawase";/' "$PICOM_CONF"
    killall -q picom || true
    sleep 0.2
    picom -b &
    notify-send -u low -i "$notif/ja.png" "Picom Blur" "Enabled (Dual Kawase)"
else
    sed -i 's/blur-method = "dual_kawase";/blur-method = "none";/' "$PICOM_CONF"
    killall -q picom || true
    sleep 0.2
    picom -b &
    notify-send -u low -i "$notif/note.png" "Picom Blur" "Disabled"
fi
