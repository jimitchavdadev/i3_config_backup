#!/usr/bin/env bash
# Keyboard layout switcher for X11 / i3
set -euo pipefail

LAYOUTS="us\nus intl\ngb\nde\nfr\nes\nit\nru\nja"
CURRENT=$(setxkbmap -query | grep layout | awk '{print $2}')

if [[ "${1:-}" == "switch" ]]; then
    # Toggle between us and us intl, or cycle
    if [ "$CURRENT" = "us" ]; then
        setxkbmap "us(intl)" 2>/dev/null || setxkbmap "us"
        notify-send -i "$HOME/.config/swaync/images/ja.png" "Keyboard" "Switched to US (intl)"
    else
        setxkbmap "us"
        notify-send -i "$HOME/.config/swaync/images/ja.png" "Keyboard" "Switched to US"
    fi
    exit 0
fi

pkill -x rofi 2>/dev/null || true
CHOICE=$(echo -e "$LAYOUTS" | rofi -dmenu -i -p "Keyboard Layout" -select "$CURRENT" 2>/dev/null || true)

if [ -n "$CHOICE" ]; then
    setxkbmap "$CHOICE"
    notify-send -i "$HOME/.config/swaync/images/ja.png" "Keyboard" "Layout set to: $CHOICE"
fi
