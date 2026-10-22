#!/usr/bin/env bash
# Monitor profiles manager using xrandr
set -euo pipefail

PROFILES_DIR="$HOME/.config/i3/monitor_profiles"
mkdir -p "$PROFILES_DIR"

if [ -z "$(ls -A "$PROFILES_DIR" 2>/dev/null)" ]; then
    cat > "$PROFILES_DIR/default.sh" << 'EOF'
#!/bin/bash
xrandr --auto
EOF
    chmod +x "$PROFILES_DIR/default.sh"
fi

pkill -x rofi 2>/dev/null || true

PROFILES=$(ls "$PROFILES_DIR" | sed 's/\.sh$//')
CHOICE=$(echo "$PROFILES" | rofi -dmenu -i -p "Monitor Profile" 2>/dev/null || true)

if [ -n "$CHOICE" ] && [ -f "$PROFILES_DIR/$CHOICE.sh" ]; then
    bash "$PROFILES_DIR/$CHOICE.sh"
    sleep 0.5
    ~/.config/polybar/launch.sh &
    i3-msg restart >/dev/null 2>&1 || true
    notify-send -i "$HOME/.config/swaync/images/ja.png" "Monitor Profile" "Applied: $CHOICE"
fi
