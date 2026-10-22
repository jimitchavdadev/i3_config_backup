#!/usr/bin/env bash
# Wallpaper Selector with Preview for i3
set -euo pipefail

wallDIR="$HOME/Pictures/wallpapers"
cacheDIR="$HOME/.cache/i3/wallpapers"
current="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"
rofi_theme="$HOME/.config/rofi/config-wallpaper.rasi"
iDIR="$HOME/.config/swaync/icons"
sDIR="$HOME/.config/i3/scripts"

mkdir -p "$wallDIR" "$cacheDIR" "$(dirname "$current")"

# Kill existing rofi instance
pkill -x rofi 2>/dev/null || true

# Gather wallpapers
mapfile -d '' PICS < <(find -L "$wallDIR" -type f \( \
  -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) -print0)

if [ ${#PICS[@]} -eq 0 ]; then
    notify-send -i "$iDIR/picture.png" "Wallpapers" "No wallpapers found in $wallDIR"
    exit 1
fi

generate_preview() {
    local img="$1"
    local thumb="$cacheDIR/$(basename "$img").thumb.jpg"
    if [ ! -f "$thumb" ] || [ "$img" -nt "$thumb" ]; then
        magick "$img" -thumbnail 240x160^ -gravity center -extent 240x160 "$thumb" 2>/dev/null || true
    fi
    if [ -f "$thumb" ]; then
        echo "$thumb"
    else
        echo "$img"
    fi
}

RANDOM_PIC="${PICS[$((RANDOM % ${#PICS[@]}))]}"
RANDOM_PIC_NAME=". Random Wallpaper"

menu() {
    printf "%s\x00icon\x1f%s\n" "$RANDOM_PIC_NAME" "$RANDOM_PIC"
    readarray -t sorted < <(printf '%s\n' "${PICS[@]}" | sort -V)
    for pic in "${sorted[@]}"; do
        pic_name=$(basename "$pic")
        thumb=$(generate_preview "$pic")
        printf "%s\x00icon\x1f%s\n" "$pic_name" "$thumb"
    done
}

# Run rofi with icons enabled
if [ -f "$rofi_theme" ]; then
    choice=$(menu | rofi -i -dmenu -config "$rofi_theme" -show-icons || true)
else
    choice=$(menu | rofi -i -dmenu -p "Wallpaper" -show-icons || true)
fi

# Trim whitespace
choice=$(echo "$choice" | xargs 2>/dev/null || echo "$choice")
[[ -z "$choice" ]] && exit 0

if [[ "$choice" == "$RANDOM_PIC_NAME" ]] || [[ "$choice" == ". random" ]]; then
    selected_file="$RANDOM_PIC"
else
    selected_file=""
    for pic in "${PICS[@]}"; do
        if [[ "$(basename "$pic")" == "$choice" ]]; then
            selected_file="$pic"
            break
        fi
    done
    if [[ -z "$selected_file" ]]; then
        choice_basename=$(basename "$choice" | sed 's/\(.*\)\.[^.]*$/\1/')
        selected_file=$(find -L "$wallDIR" -iname "$choice_basename.*" -print -quit 2>/dev/null || true)
    fi
fi

if [[ -n "$selected_file" && -f "$selected_file" ]]; then
    "$sDIR/WallustFeh.sh" "$selected_file"
    notify-send -i "$iDIR/picture.png" "Wallpaper" "Applied: $(basename "$selected_file")"
else
    notify-send -i "$iDIR/picture.png" "Wallpaper" "Failed to locate: $choice"
fi
