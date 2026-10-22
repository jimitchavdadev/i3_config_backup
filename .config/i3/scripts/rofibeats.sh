#!/usr/bin/env bash
# RofiBeats - Online and Local Music Streamer for i3
set -euo pipefail

music_list="$HOME/.config/rofi/online_music.list"
rofi_theme="$HOME/.config/rofi/config-rofi-Beats.rasi"
iDIR="$HOME/.config/swaync/icons"

stop_music() {
    pkill -f "mpv.*--no-video" 2>/dev/null || true
    notify-send -u low -i "$iDIR/music.png" "RofiBeats" "Music stopped"
}

if [[ "${1:-}" == "--stop" ]]; then
    stop_music
    exit 0
fi

# Gather options
options="⏹️  Stop Music\n"
if [ -f "$music_list" ]; then
    while IFS='|' read -r name url; do
        [[ -n "$name" && -n "$url" ]] && options+="$name\n"
    done < "$music_list"
fi

if [ -f "$rofi_theme" ]; then
    choice=$(echo -e "$options" | rofi -i -dmenu -config "$rofi_theme")
else
    choice=$(echo -e "$options" | rofi -i -dmenu -p "RofiBeats")
fi

[[ -z "$choice" ]] && exit 0

if [[ "$choice" == *"Stop Music"* ]]; then
    stop_music
    exit 0
fi

url=$(grep -F "$choice" "$music_list" | cut -d'|' -f2 | xargs || true)

if [ -n "$url" ]; then
    pkill -f "mpv.*--no-video" 2>/dev/null || true
    notify-send -i "$iDIR/music.png" "Now Playing" "$choice"
    mpv --no-video "$url" >/dev/null 2>&1 &
fi
