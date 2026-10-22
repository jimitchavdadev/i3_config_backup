#!/usr/bin/env bash
# Brightness control script with Dunst OSD progress bar
set -euo pipefail

iDIR="$HOME/.config/swaync/icons"
step=5

get_brightness() {
    brightnessctl -m | cut -d, -f4 | tr -d '%'
}

get_icon_path() {
    local brightness=$1
    local level=$(( (brightness + 19) / 20 * 20 ))
    if (( level > 100 )); then level=100; fi
    if (( level < 20 )); then level=20; fi
    echo "$iDIR/brightness-${level}.png"
}

send_notification() {
    local brightness=$1
    local icon_path
    icon_path=$(get_icon_path "$brightness")

    notify-send -e \
        -h string:x-canonical-private-synchronous:brightness_notif \
        -h int:value:"$brightness" \
        -u low \
        -i "$icon_path" \
        "Screen" "Brightness: ${brightness}%"
}

change_brightness() {
    local delta=$1
    local current
    current=$(get_brightness)
    local new=$((current + delta))

    (( new < 5 )) && new=5
    (( new > 100 )) && new=100

    brightnessctl set "${new}%" >/dev/null 2>&1
    send_notification "$new"
}

case "${1:-}" in
    "--get")
        get_brightness
        ;;
    "--inc"|"up")
        change_brightness "+$step"
        ;;
    "--dec"|"down")
        change_brightness "-$step"
        ;;
    *)
        get_brightness
        ;;
esac
