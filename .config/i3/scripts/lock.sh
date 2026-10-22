#!/usr/bin/env bash
# Screen locker for i3 replicating Hyprlock aesthetics
set -euo pipefail

LOCK_IMG="/tmp/i3lock_blurred.png"
current_wall="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"

# Prepare blurred lock wallpaper if wallpaper exists
if [ -f "$current_wall" ]; then
    wall_path=$(cat "$current_wall" 2>/dev/null || echo "")
    if [ -f "$wall_path" ] && [ ! -f "$LOCK_IMG" ]; then
        convert "$wall_path" -filter Gaussian -resize 50% -define filter:sigma=2.5 -resize 200% "$LOCK_IMG" 2>/dev/null || true
    fi
fi

if command -v i3lock-color >/dev/null 2>&1; then
    if [ -f "$LOCK_IMG" ]; then
        i3lock-color -i "$LOCK_IMG" --clock --indicator --ring-color=89b4fa --keyhl-color=a6e3a1 --time-color=cdd6f4 --date-color=cdd6f4
    else
        i3lock-color --blur 5 --clock --indicator --ring-color=89b4fa --keyhl-color=a6e3a1 --time-color=cdd6f4 --date-color=cdd6f4
    fi
elif [ -f "$LOCK_IMG" ]; then
    i3lock -i "$LOCK_IMG"
else
    i3lock -c 1e1e2e
fi
