#!/usr/bin/env bash
# Global Theme Switcher using Wallust
set -euo pipefail

wallust_cmd="wallust"
if ! command -v wallust >/dev/null 2>&1; then
    wallust_cmd="$HOME/.cargo/bin/wallust"
fi

pkill -x rofi 2>/dev/null || true

choice=$("$wallust_cmd" theme list 2>/dev/null \
    | sed -e '1d' -e 's/^- //' \
    | rofi -dmenu -i -p "Select Global Theme" 2>/dev/null || true)

[[ -z "$choice" ]] && exit 0

"$wallust_cmd" theme -- "$choice" || true

# Refresh components
"$HOME/.config/i3/scripts/Refresh.sh" &
notify-send -i "$HOME/.config/swaync/icons/palette.png" "Theme Changed" "Selected: $choice"
