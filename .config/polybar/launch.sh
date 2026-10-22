#!/usr/bin/env bash
# ==================================================
#  Polybar Multi-Monitor & Floating Tray Launcher
# ==================================================
killall -q polybar 2>/dev/null || true
pkill -f hover_drawer.sh 2>/dev/null || true
while pgrep -u $UID -x polybar >/dev/null; do sleep 0.1; done

export DISPLAY="${DISPLAY:-:0}"

# 1. Launch floating tray bar first to claim X11 system tray selection
setsid polybar -c "$HOME/.config/polybar/config.ini" tray </dev/null >/dev/null 2>&1 &
sleep 0.5

# Immediately hide the floating tray so it starts in collapsed state
TRAY_WID=$(xdotool search --name "polybar-tray" 2>/dev/null | head -n 1 || true)
if [ -n "$TRAY_WID" ]; then
    xdotool windowunmap "$TRAY_WID" 2>/dev/null || true
fi

# Reset drawer state
echo 0 > /tmp/polybar_tray_drawer_state

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

    # Launch main bar on primary monitor
    MONITOR=$PRIMARY setsid polybar --reload -c "$HOME/.config/polybar/config.ini" main </dev/null >/dev/null 2>&1 &

    # Launch secondary bar on other active monitors
    for m in $(xrandr --query 2>/dev/null | grep -E " connected (primary )?[0-9]+x[0-9]+" | cut -d" " -f1); do
        if [ "$m" != "$PRIMARY" ]; then
            MONITOR=$m setsid polybar --reload -c "$HOME/.config/polybar/config.ini" secondary </dev/null >/dev/null 2>&1 &
        fi
    done
else
    setsid polybar --reload -c "$HOME/.config/polybar/config.ini" main </dev/null >/dev/null 2>&1 &
fi

# Launch hover detector daemon in background
setsid "$HOME/.config/polybar/scripts/hover_drawer.sh" </dev/null >/dev/null 2>&1 &
