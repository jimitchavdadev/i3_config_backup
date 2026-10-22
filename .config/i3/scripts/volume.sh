#!/usr/bin/env bash
# Volume management script with Dunst OSD progress bar
set -euo pipefail

iDIR="$HOME/.config/swaync/icons"
sDIR="$HOME/.config/i3/scripts"

get_volume() {
    pamixer --get-volume 2>/dev/null || pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\d+%' | head -1 | tr -d '%'
}

is_muted() {
    pamixer --get-mute 2>/dev/null || pactl get-sink-mute @DEFAULT_SINK@ | grep -q "yes" && echo "true" || echo "false"
}

get_icon() {
    local muted
    muted="$(is_muted)"
    if [ "$muted" = "true" ]; then
        echo "$iDIR/volume-mute.png"
        return
    fi

    local vol
    vol="$(get_volume)"
    if [ "$vol" -le 30 ]; then
        echo "$iDIR/volume-low.png"
    elif [ "$vol" -le 60 ]; then
        echo "$iDIR/volume-mid.png"
    else
        echo "$iDIR/volume-high.png"
    fi
}

notify_user() {
    local muted
    muted="$(is_muted)"
    local level
    level="$(get_volume)"

    if [ "$muted" = "true" ] || [ "$level" -eq 0 ]; then
        notify-send -e -h string:x-canonical-private-synchronous:volume_notif \
            -u low -i "$(get_icon)" "Volume" "Muted"
    else
        notify-send -e -h int:value:"$level" -h string:x-canonical-private-synchronous:volume_notif \
            -u low -i "$(get_icon)" "Volume" "${level}%"
        "$sDIR/Sounds.sh" --volume 2>/dev/null || true
    fi
}

case "${1:-}" in
    "--inc"|"up")
        pamixer -i 5 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ +5%
        notify_user
        ;;
    "--dec"|"down")
        pamixer -d 5 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ -5%
        notify_user
        ;;
    "--inc-precise")
        pamixer -i 1 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ +1%
        notify_user
        ;;
    "--dec-precise")
        pamixer -d 1 2>/dev/null || pactl set-sink-volume @DEFAULT_SINK@ -1%
        notify_user
        ;;
    "--toggle"|"mute")
        pamixer -t 2>/dev/null || pactl set-sink-mute @DEFAULT_SINK@ toggle
        notify_user
        ;;
    "--toggle-mic")
        pamixer --default-source -t 2>/dev/null || pactl set-source-mute @DEFAULT_SOURCE@ toggle
        mic_mute=$(pamixer --default-source --get-mute 2>/dev/null || echo "false")
        if [ "$mic_mute" = "true" ]; then
            notify-send -e -h string:x-canonical-private-synchronous:mic_notif -u low -i "$iDIR/microphone-mute.png" "Microphone" "Muted"
        else
            notify-send -e -h string:x-canonical-private-synchronous:mic_notif -u low -i "$iDIR/microphone.png" "Microphone" "Active"
        fi
        ;;
    *)
        get_volume
        ;;
esac
