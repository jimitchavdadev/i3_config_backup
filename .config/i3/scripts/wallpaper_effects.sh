#!/usr/bin/env bash
# Wallpaper Effects using ImageMagick for i3
set -euo pipefail

wallpaper_current="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"
wallpaper_output="$HOME/.config/i3/wallpaper_effects/.wallpaper_modified"
sDIR="$HOME/.config/i3/scripts"
rofi_theme="$HOME/.config/rofi/config-wallpaper-effect.rasi"
iDIR="$HOME/.config/swaync/images"

mkdir -p "$(dirname "$wallpaper_current")"

if [ ! -f "$wallpaper_current" ]; then
    echo "$HOME/Pictures/wallpapers/wallpaper.jpeg" > "$wallpaper_current"
fi

current_img=$(cat "$wallpaper_current" 2>/dev/null || true)
if [ -z "$current_img" ] || [ ! -f "$current_img" ]; then
    current_img="$HOME/Pictures/wallpapers/wallpaper.jpeg"
fi

pkill -x rofi 2>/dev/null || true

menu() {
    cat << 'EOF'
No Effects
Black & White
Blurred
Charcoal
Edge Detect
Emboss
Frame Raised
Frame Sunk
Negate
Oil Paint
Polaroid
Posterize
Sepia Tone
Sharpen
Solarize
Vignette
Vignette-black
Zoomed
EOF
}

if [ -f "$rofi_theme" ]; then
    choice=$(menu | rofi -i -dmenu -config "$rofi_theme" || true)
else
    choice=$(menu | rofi -i -dmenu -p "Wallpaper Effect" || true)
fi

choice=$(echo "$choice" | xargs 2>/dev/null || echo "$choice")
[[ -z "$choice" ]] && exit 0

case "$choice" in
    "No Effects")
        "$sDIR/WallustFeh.sh" "$current_img"
        notify-send -i "$iDIR/ja.png" "Wallpaper Effects" "Reset to original wallpaper"
        exit 0
        ;;
    "Black & White")
        magick "$current_img" -colorspace gray -sigmoidal-contrast 10,40% "$wallpaper_output"
        ;;
    "Blurred")
        magick "$current_img" -blur 0x10 "$wallpaper_output"
        ;;
    "Charcoal")
        magick "$current_img" -charcoal 0x5 "$wallpaper_output"
        ;;
    "Edge Detect")
        magick "$current_img" -edge 1 "$wallpaper_output"
        ;;
    "Emboss")
        magick "$current_img" -emboss 0x5 "$wallpaper_output"
        ;;
    "Frame Raised")
        magick "$current_img" +raise 150 "$wallpaper_output"
        ;;
    "Frame Sunk")
        magick "$current_img" -raise 150 "$wallpaper_output"
        ;;
    "Negate")
        magick "$current_img" -negate "$wallpaper_output"
        ;;
    "Oil Paint")
        magick "$current_img" -paint 4 "$wallpaper_output"
        ;;
    "Polaroid")
        magick "$current_img" -polaroid 0 "$wallpaper_output"
        ;;
    "Posterize")
        magick "$current_img" -posterize 4 "$wallpaper_output"
        ;;
    "Sepia Tone")
        magick "$current_img" -sepia-tone 65% "$wallpaper_output"
        ;;
    "Sharpen")
        magick "$current_img" -sharpen 0x5 "$wallpaper_output"
        ;;
    "Solarize")
        magick "$current_img" -solarize 80% "$wallpaper_output"
        ;;
    "Vignette")
        magick "$current_img" -vignette 0x3 "$wallpaper_output"
        ;;
    "Vignette-black")
        magick "$current_img" -background black -vignette 0x3 "$wallpaper_output"
        ;;
    "Zoomed")
        magick "$current_img" -gravity Center -extent 1:1 "$wallpaper_output"
        ;;
    *)
        exit 0
        ;;
esac

if [ -f "$wallpaper_output" ]; then
    "$sDIR/WallustFeh.sh" "$wallpaper_output"
    notify-send -i "$iDIR/ja.png" "Wallpaper Effects" "Applied: $choice"
fi
