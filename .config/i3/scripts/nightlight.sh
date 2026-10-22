#!/usr/bin/env bash
# /* ---- 💫 Night Light Toggle (Redshift for X11 / Hyprsunset Replica) 💫 ---- */

if pgrep -x "redshift" >/dev/null 2>&1; then
    killall -q redshift || true
    notify-send -t 1500 "Night Light" "Disabled (Day mode)"
else
    if command -v redshift >/dev/null 2>&1; then
        redshift -P -O 4500 >/dev/null 2>&1 &
        notify-send -t 1500 "Night Light" "Enabled (4500K Warm)"
    fi
fi
