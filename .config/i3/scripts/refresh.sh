#!/usr/bin/env bash
# Refresh script for i3 environment
set -euo pipefail

# Reload wallpaper if .fehbg exists
if [ -f "$HOME/.fehbg" ]; then
    bash "$HOME/.fehbg" &
fi

# Restart Polybar
~/.config/polybar/launch.sh &

# Restart Picom
killall -q picom 2>/dev/null || true
sleep 0.2
picom -b &

# Reload Dunst
if pidof dunst >/dev/null; then
    killall -SIGUSR2 dunst 2>/dev/null || true
else
    dunst &
fi

# Reload i3
i3-msg reload >/dev/null 2>&1 || true

notify-send -t 1500 -i "$HOME/.config/swaync/images/ja.png" "Desktop Refreshed" "Polybar, Picom, Dunst & i3wm reloaded"
