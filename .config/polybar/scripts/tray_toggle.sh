#!/usr/bin/env bash
# ==================================================
#  Polybar Tray Drawer Toggle (Windows-style Flyout)
# ==================================================
# Positions and toggles the background process drawer
# on whichever monitor it was clicked.
set -euo pipefail

# 1. Get mouse location
eval "$(xdotool getmouselocation --shell 2>/dev/null || echo "X=0 Y=0")"

# 2. Find polybar-tray window
WID=$(xdotool search --name "polybar-tray" 2>/dev/null | head -n 1 || true)
if [ -z "$WID" ]; then
    # Fallback: start it if not running
    polybar -c "$HOME/.config/polybar/config.ini" tray >/dev/null 2>&1 &
    sleep 0.4
    WID=$(xdotool search --name "polybar-tray" 2>/dev/null | head -n 1 || true)
fi

[ -z "$WID" ] && exit 0

is_mapped=0
if xwininfo -id "$WID" 2>/dev/null | grep -q "Map State: IsViewable"; then
    is_mapped=1
fi

# 3. Detect current monitor bounds where mouse was clicked
mon_x=0
mon_w=1920
while read -r line; do
    if [[ "$line" =~ ([a-zA-Z0-9_-]+)\ connected\ (primary\ )?([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+) ]]; then
        w="${BASH_REMATCH[3]}"
        ox="${BASH_REMATCH[5]}"
        if [ "$X" -ge "$ox" ] && [ "$X" -lt $(( ox + w )) ]; then
            mon_x="$ox"
            mon_w="$w"
            break
        fi
    fi
done < <(xrandr --query 2>/dev/null | grep " connected")

box_w=340
target_x=$(( X - (box_w / 2) ))
min_allowed=$(( mon_x + 10 ))
max_allowed=$(( mon_x + mon_w - box_w - 10 ))

if [ "$target_x" -lt "$min_allowed" ]; then
    target_x="$min_allowed"
fi
if [ "$target_x" -gt "$max_allowed" ]; then
    target_x="$max_allowed"
fi
target_y=50

if [ "$is_mapped" -eq 1 ]; then
    curr_x=$(xwininfo -id "$WID" 2>/dev/null | grep "Absolute upper-left X:" | awk '{print $4}' || echo 0)
    diff=$(( X - curr_x ))
    diff=${diff#-} # absolute value
    if [ "$diff" -gt 350 ]; then
        # Clicked on a different monitor: move it directly there
        xdotool windowmove "$WID" "$target_x" "$target_y"
        xdotool windowraise "$WID"
        polybar-msg action "#tray-toggle.hook.1" >/dev/null 2>&1 || true
    else
        # Clicked to close
        xdotool windowunmap "$WID"
        polybar-msg action "#tray-toggle.hook.0" >/dev/null 2>&1 || true
    fi
else
    # Currently hidden: position, show, and raise
    xdotool windowmove "$WID" "$target_x" "$target_y"
    xdotool windowmap "$WID"
    xdotool windowraise "$WID"
    polybar-msg action "#tray-toggle.hook.1" >/dev/null 2>&1 || true
fi
