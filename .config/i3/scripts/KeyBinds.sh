#!/usr/bin/env bash
# Searchable keybindings list in Rofi
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-keybinds.rasi"
msg="Search i3 keybindings (Press ESC to close)"
config_file="$HOME/.config/i3/config"

pkill -x rofi 2>/dev/null || true

if [ ! -f "$config_file" ]; then exit 1; fi

keybinds=$(grep -E '^\s*bindsym\s+' "$config_file" | sed 's/^\s*bindsym\s\+//' | awk '
{
    key=$1;
    $1="";
    sub(/^[ \t]+/, "");
    printf "%-30s %s\n", key, $0;
}')

if [ -f "$rofi_theme" ]; then
    printf '%s\n' "$keybinds" | rofi -dmenu -i -config "$rofi_theme" -mesg "$msg"
else
    printf '%s\n' "$keybinds" | rofi -dmenu -i -p "Keybinds" -mesg "$msg"
fi
