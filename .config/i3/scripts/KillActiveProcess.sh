#!/usr/bin/env bash
# Force terminate active window/process
set -euo pipefail

notif="$HOME/.config/swaync/images"

win_id=$(xdotool getactivewindow 2>/dev/null || echo "")

if [ -n "$win_id" ]; then
    pid=$(xdotool getwindowpid "$win_id" 2>/dev/null || echo "")
    if [ -n "$pid" ] && [ "$pid" -gt 0 ]; then
        kill -9 "$pid" 2>/dev/null || true
        notify-send -u low -i "$notif/ja.png" "Kill Process" "Killed PID: $pid"
        exit 0
    fi
    xkill -id "$win_id" 2>/dev/null || true
    notify-send -u low -i "$notif/ja.png" "Kill Process" "Terminated active window"
else
    notify-send -u low -i "$notif/error.png" "Kill Process" "No active window found"
fi
