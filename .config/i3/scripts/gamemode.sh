#!/usr/bin/env bash
# Game Mode for i3wm (Turns off compositor and hides bar for maximum gaming FPS)
set -euo pipefail

MODE_FILE="/tmp/i3_gamemode"
notif="$HOME/.config/swaync/images/ja.png"

if [ ! -f "$MODE_FILE" ]; then
    touch "$MODE_FILE"
    killall -q picom || true
    polybar-msg cmd hide 2>/dev/null || killall -q polybar || true
    i3-msg "gaps inner all set 0; gaps outer all set 0" >/dev/null 2>&1
    notify-send -u low -i "$notif" "GameMode" "Enabled (Picom & Bar stopped, gaps 0)"
else
    rm -f "$MODE_FILE"
    i3-msg "gaps inner all set 4; gaps outer all set 8" >/dev/null 2>&1
    ~/.config/polybar/launch.sh &
    sleep 0.2
    picom -b &
    notify-send -u low -i "$notif" "GameMode" "Disabled (Compositor & Bar restored)"
fi
