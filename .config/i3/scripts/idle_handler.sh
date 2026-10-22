#!/usr/bin/env bash
# Idle handler for i3wm replicating hypridle
LOCK_SCRIPT="$HOME/.config/i3/scripts/LockScreen.sh"

killall -q xidlehook xautolock 2>/dev/null || true

if command -v xautolock >/dev/null 2>&1; then
    xautolock -time 10 -locker "$LOCK_SCRIPT" -detectsleep &
elif command -v xidlehook >/dev/null 2>&1; then
    xidlehook --not-when-fullscreen --not-when-audio --timer 600 "$LOCK_SCRIPT" '' &
fi
