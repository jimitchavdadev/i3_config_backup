#!/usr/bin/env bash
# ==================================================
#  Idle & Sleep Handler for i3wm
# ==================================================
LOCK_SCRIPT="$HOME/.config/i3/scripts/LockScreen.sh"

# Terminate any duplicate instances
killall -q xidlehook xautolock xss-lock 2>/dev/null || true

# Determine active user logind session ID
SESSION_ID=$(loginctl show-user "$USER" -p Display --value 2>/dev/null || true)
if [ -z "$SESSION_ID" ]; then
    SESSION_ID=$(loginctl list-sessions 2>/dev/null | awk -v u="$USER" '$3 == u && ($5 == "user" || $5 == "seat0") {print $1; exit}')
fi

# Launch xss-lock to lock screen before systemd suspend/sleep (e.g. laptop lid close)
if command -v xss-lock >/dev/null 2>&1; then
    if [ -n "$SESSION_ID" ]; then
        xss-lock --session="$SESSION_ID" --transfer-sleep-lock -- "$LOCK_SCRIPT" &
    else
        xss-lock --transfer-sleep-lock -- "$LOCK_SCRIPT" &
    fi
fi

# Screen lock after 10 minutes of inactivity
if command -v xautolock >/dev/null 2>&1; then
    xautolock -time 10 -locker "$LOCK_SCRIPT" -detectsleep &
elif command -v xidlehook >/dev/null 2>&1; then
    xidlehook --not-when-fullscreen --not-when-audio --timer 600 "$LOCK_SCRIPT" '' &
fi
