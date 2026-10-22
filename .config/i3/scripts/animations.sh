#!/usr/bin/env bash
# Animation / Fading profile switcher for Picom
set -euo pipefail

PICOM_CONF="$HOME/.config/picom/picom.conf"
rofi_theme="$HOME/.config/rofi/config-Animations.rasi"

options="Disabled (Instant)\nFast (Snappy)\nSmooth (Default)"

if [ -f "$rofi_theme" ]; then
    choice=$(echo -e "$options" | rofi -i -dmenu -config "$rofi_theme" -mesg "Choose Animation Profile")
else
    choice=$(echo -e "$options" | rofi -i -dmenu -p "Animation Profile")
fi

[[ -z "$choice" ]] && exit 0

case "$choice" in
    *"Disabled"*)
        sed -i 's/^fading = .*/fading = false;/' "$PICOM_CONF"
        notify-send "Animations" "Disabled"
        ;;
    *"Fast"*)
        sed -i 's/^fading = .*/fading = true;/' "$PICOM_CONF"
        sed -i 's/^fade-delta = .*/fade-delta = 3;/' "$PICOM_CONF"
        notify-send "Animations" "Fast Profile Applied"
        ;;
    *"Smooth"*)
        sed -i 's/^fading = .*/fading = true;/' "$PICOM_CONF"
        sed -i 's/^fade-delta = .*/fade-delta = 6;/' "$PICOM_CONF"
        notify-send "Animations" "Smooth Profile Applied"
        ;;
esac

killall -q picom || true
sleep 0.2
picom -b &
