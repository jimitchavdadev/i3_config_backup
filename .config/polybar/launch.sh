#!/usr/bin/env bash
# Terminate already running bar and drawer instances
killall -q polybar 2>/dev/null || true
pkill -f hover_drawer.sh 2>/dev/null || true
while pgrep -u $UID -x polybar >/dev/null; do sleep 0.1; done

export DISPLAY="${DISPLAY:-:0}"

if command -v xrandr >/dev/null 2>&1; then
    # Detect external connected display
    EXTERNAL=$(xrandr --query 2>/dev/null | grep -E " connected (primary )?[0-9]+x[0-9]+" | grep -v "eDP" | head -n 1 | cut -d" " -f1 || true)

    if [ -n "$EXTERNAL" ]; then
        PRIMARY="$EXTERNAL"
        xrandr --output "$EXTERNAL" --primary 2>/dev/null || true
    else
        PRIMARY=$(xrandr --query 2>/dev/null | grep " connected primary" | cut -d" " -f1 || true)
        if [ -z "$PRIMARY" ]; then
            PRIMARY=$(xrandr --query 2>/dev/null | grep -E " connected (primary )?[0-9]+x[0-9]+" | head -n 1 | cut -d" " -f1 || echo "eDP-1")
        fi
    fi

    # 1. Launch on PRIMARY (external when present) first so it acquires the system tray
    MONITOR=$PRIMARY nohup polybar --reload -c "$HOME/.config/polybar/config.ini" main >/dev/null 2>&1 &
    sleep 0.4

    # 2. Launch secondary bar on other active monitors
    for m in $(xrandr --query 2>/dev/null | grep -E " connected (primary )?[0-9]+x[0-9]+" | cut -d" " -f1); do
        if [ "$m" != "$PRIMARY" ]; then
            MONITOR=$m nohup polybar --reload -c "$HOME/.config/polybar/config.ini" secondary >/dev/null 2>&1 &
        fi
    done
else
    nohup polybar --reload -c "$HOME/.config/polybar/config.ini" main >/dev/null 2>&1 &
fi

# Launch hover detector daemon in background
nohup "$HOME/.config/polybar/scripts/hover_drawer.sh" >/dev/null 2>&1 &
disown -a 2>/dev/null || true
