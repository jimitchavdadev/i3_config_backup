#!/usr/bin/env bash
# Selects a random wallpaper and applies it
set -euo pipefail

wallDIR="$HOME/Pictures/wallpapers"
sDIR="$HOME/.config/i3/scripts"

if [ ! -d "$wallDIR" ]; then exit 1; fi

mapfile -d '' PICS < <(find -L "$wallDIR" -type f \( \
  -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) -print0)

if [ ${#PICS[@]} -eq 0 ]; then exit 1; fi

RANDOM_WALL="${PICS[$((RANDOM % ${#PICS[@]}))]}"

"$sDIR/WallustFeh.sh" "$RANDOM_WALL"
notify-send -i "$HOME/.config/swaync/icons/picture.png" "Random Wallpaper" "Applied: $(basename "$RANDOM_WALL")"
