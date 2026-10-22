#!/bin/bash
CACHE_FILE="$HOME/.cache/i3/.theme_mode"
mkdir -p "$(dirname "$CACHE_FILE")"

if [ ! -f "$CACHE_FILE" ]; then echo "Dark" > "$CACHE_FILE"; fi
CURRENT=$(cat "$CACHE_FILE")

if [ "$CURRENT" == "Dark" ]; then NEW="Light"; else NEW="Dark"; fi
echo "$NEW" > "$CACHE_FILE"

if [ "$NEW" == "Dark" ]; then
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita-dark" 2>/dev/null || true
else
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita" 2>/dev/null || true
fi

~/.config/i3/scripts/refresh.sh
notify-send "Theme" "Switched to $NEW mode"
