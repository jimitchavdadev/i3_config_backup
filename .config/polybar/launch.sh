#!/usr/bin/env bash
# ==================================================
#  Polybar Multi-Monitor & Floating Tray Launcher
# ==================================================
set -euo pipefail

export DISPLAY="${DISPLAY:-:0}"
if [[ -z "${XAUTHORITY:-}" ]]; then
    if [[ -f "/run/user/$(id -u)/gdm/Xauthority" ]]; then
        export XAUTHORITY="/run/user/$(id -u)/gdm/Xauthority"
    elif [[ -f "$HOME/.Xauthority" ]]; then
        export XAUTHORITY="$HOME/.Xauthority"
    fi
fi

LOCK_FILE="/tmp/polybar_launch.lock"
exec 200>"$LOCK_FILE"

# Single-flight mutual exclusion:
# If another launcher is currently running, wait for it to finish and exit cleanly.
if ! flock -n 200; then
    flock -x 200
    exec 200>&-
    exit 0
fi

# Ensure lock fd is closed when script exits
trap 'exec 200>&- 2>/dev/null || true' EXIT

# 1. Kill old polybar and hover_drawer instances cleanly
killall -q polybar 2>/dev/null || true
pkill -f hover_drawer.sh 2>/dev/null || true

# Wait up to 2 seconds for previous polybars to terminate
for i in {1..20}; do
    if ! pgrep -u "$UID" -x polybar >/dev/null; then
        break
    fi
    sleep 0.05
done

# Force kill any stubborn lingering polybars or hover_drawer scripts
if pgrep -u "$UID" -x polybar >/dev/null; then
    pkill -9 -u "$UID" -x polybar 2>/dev/null || true
    sleep 0.05
fi
pkill -9 -f hover_drawer.sh 2>/dev/null || true

# 2. Launch floating tray bar first to claim X11 system tray selection
setsid polybar -c "$HOME/.config/polybar/config.ini" tray 200>&- </dev/null >/dev/null 2>&1 &

# Wait for tray window to appear and immediately hide it (collapsed state)
for i in {1..20}; do
    TRAY_WID=$(xdotool search --name "polybar-tray" 2>/dev/null | head -n 1 || true)
    if [ -n "$TRAY_WID" ]; then
        xdotool windowunmap "$TRAY_WID" 2>/dev/null || true
        break
    fi
    sleep 0.05
done

# Reset drawer state
echo 0 > /tmp/polybar_tray_drawer_state

# 3. Detect displays and launch main/secondary bars
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
    MONITOR=$PRIMARY setsid polybar --reload -c "$HOME/.config/polybar/config.ini" main 200>&- </dev/null >/dev/null 2>&1 &

    # Launch secondary bar on other active monitors
    for m in $(xrandr --query 2>/dev/null | grep -E " connected (primary )?[0-9]+x[0-9]+" | cut -d" " -f1); do
        if [ "$m" != "$PRIMARY" ]; then
            MONITOR=$m setsid polybar --reload -c "$HOME/.config/polybar/config.ini" secondary 200>&- </dev/null >/dev/null 2>&1 &
        fi
    done
else
    setsid polybar --reload -c "$HOME/.config/polybar/config.ini" main 200>&- </dev/null >/dev/null 2>&1 &
fi

# 4. Launch hover detector daemon in background
setsid "$HOME/.config/polybar/scripts/hover_drawer.sh" 200>&- </dev/null >/dev/null 2>&1 &
