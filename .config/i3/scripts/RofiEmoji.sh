#!/usr/bin/env bash
# Rofi Emoji Picker for i3
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-emoji.rasi"
emoji_file="$HOME/.config/rofi/emoji.list"
msg="👀 Click or press Return to choose and copy emoji"

pkill -x rofi 2>/dev/null || true

if [ ! -f "$emoji_file" ]; then
    exit 1
fi

if [ -f "$rofi_theme" ]; then
    chosen=$(rofi -i -dmenu -config "$rofi_theme" -mesg "$msg" < "$emoji_file" 2>/dev/null || true)
else
    chosen=$(rofi -i -dmenu -p "Emoji" -mesg "$msg" < "$emoji_file" 2>/dev/null || true)
fi

[[ -z "$chosen" ]] && exit 0

emoji=$(echo "$chosen" | awk '{print $1}')
printf "%s" "$emoji" | xclip -selection clipboard 2>/dev/null || true
notify-send -t 1500 -i "$HOME/.config/swaync/images/ja.png" "Emoji Copied" "$emoji copied to clipboard"