#!/usr/bin/env bash
# Touchpad toggle script for X11 / i3
set -euo pipefail

notif="$HOME/.config/swaync/images/ja.png"

# Detect touchpad ID from xinput
touchpad_id=$(xinput list 2>/dev/null | grep -i "touchpad" | grep -o 'id=[0-9]*' | cut -d= -f2 | head -n1 || echo "")

if [ -z "$touchpad_id" ]; then
    notify-send -u low "Touchpad" "No touchpad detected"
    exit 1
fi

status=$(xinput list-props "$touchpad_id" | grep "Device Enabled" | awk '{print $4}')

if [ "$status" = "1" ]; then
    xinput disable "$touchpad_id"
    notify-send -u low -i "$notif" "Touchpad" "Disabled"
else
    xinput enable "$touchpad_id"
    notify-send -u low -i "$notif" "Touchpad" "Enabled"
fi
