#!/usr/bin/env bash
# Polybar hover detector for expandable system specs drawer
set -euo pipefail

sDIR="$HOME/.config/polybar/scripts"
leave_count=0
is_expanded=0

while true; do
    if ! eval "$(xdotool getmouselocation --shell 2>/dev/null)"; then
        sleep 0.5
        continue
    fi

    primary_w=$(xrandr --query 2>/dev/null | grep " connected primary" | grep -oP '\d+(?=x\d+)' || echo 1366)
    min_x=$(( primary_w * 50 / 100 ))
    max_x=$(( primary_w - 40 ))

    if [ "$Y" -le 42 ] && [ "$X" -ge "$min_x" ] && [ "$X" -le "$max_x" ]; then
        leave_count=0
        if [ "$is_expanded" -eq 0 ]; then
            "$sDIR/sysdrawer.sh" expand
            is_expanded=1
        fi
    else
        if [ "$is_expanded" -eq 1 ]; then
            leave_count=$(( leave_count + 1 ))
            if [ "$leave_count" -ge 4 ]; then # ~600ms grace period
                "$sDIR/sysdrawer.sh" collapse
                is_expanded=0
                leave_count=0
            fi
        fi
    fi

    sleep 0.15
done
