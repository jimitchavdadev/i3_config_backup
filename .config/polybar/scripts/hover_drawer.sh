#!/usr/bin/env bash
# ==================================================
#  Polybar hover detector for system specs drawer
# ==================================================
# Supports multi-monitor setups (eDP-1 + HDMI-1, etc.)
set -euo pipefail

LOCK_FILE="/tmp/hover_drawer.lock"
exec 201>"$LOCK_FILE"
if ! flock -n 201; then
    exit 0
fi

sDIR="$HOME/.config/polybar/scripts"
leave_count=0
is_expanded=0

get_screens() {
    screens=()
    while read -r line; do
        if [[ "$line" =~ ([a-zA-Z0-9_-]+)\ connected\ (primary\ )?([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+) ]]; then
            w="${BASH_REMATCH[3]}"
            ox="${BASH_REMATCH[5]}"
            screens+=("$ox:$w")
        fi
    done < <(xrandr --query 2>/dev/null | grep " connected")
}

get_screens
screen_cache_counter=0

while true; do
    screen_cache_counter=$(( screen_cache_counter + 1 ))
    if [ "$screen_cache_counter" -ge 20 ]; then
        get_screens
        screen_cache_counter=0
    fi

    if ! eval "$(xdotool getmouselocation --shell 2>/dev/null)"; then
        sleep 0.5
        continue
    fi

    in_zone=0
    if [ "$Y" -le 44 ]; then
        for s in "${screens[@]}"; do
            ox="${s%%:*}"
            w="${s##*:}"
            if [ "$X" -ge "$ox" ] && [ "$X" -lt $(( ox + w )) ]; then
                local_x=$(( X - ox ))
                # System specs drawer sits on right side of bar
                min_x=$(( w * 45 / 100 ))
                max_x=$(( w - 60 ))
                if [ "$local_x" -ge "$min_x" ] && [ "$local_x" -le "$max_x" ]; then
                    in_zone=1
                    break
                fi
            fi
        done
    fi

    if [ "$in_zone" -eq 1 ]; then
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
