#!/usr/bin/env bash
# Auto-change wallpaper every interval (default 30 mins)
INTERVAL="${1:-1800}"
sDIR="$HOME/.config/i3/scripts"

while true; do
    sleep "$INTERVAL"
    "$sDIR/wallpaper_random.sh" || true
done
