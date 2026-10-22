#!/usr/bin/env bash
# Screenshot utility for i3wm replicating Hyprland dots
set -euo pipefail

time=$(date "+%d-%b_%H-%M-%S")
PICTURES_DIR="$(xdg-user-dir PICTURES 2>/dev/null || echo "$HOME/Pictures")"
dir="$PICTURES_DIR/Screenshots"
file="Screenshot_${time}_${RANDOM}.png"
target_file="$dir/$file"

iDIR="$HOME/.config/swaync/icons"
iDoR="$HOME/.config/swaync/images"
sDIR="$HOME/.config/i3/scripts"

mkdir -p "$dir"

notify_cmd="notify-send -t 10000 -A action1=Open -A action2=Delete -i $iDIR/picture.png"

notify_view() {
    local shot_path="$1"
    if [ -f "$shot_path" ]; then
        "$sDIR/Sounds.sh" --screenshot 2>/dev/null || true
        resp=$(timeout 6 $notify_cmd "Screenshot Saved" "$(basename "$shot_path")" 2>/dev/null || true)
        case "$resp" in
            action1) xdg-open "$shot_path" & ;;
            action2) rm "$shot_path" & ;;
        esac
    fi
}

countdown() {
    local secs="$1"
    for sec in $(seq "$secs" -1 1); do
        notify-send -t 1000 -i "$iDIR/timer.png" "Taking screenshot" "in $sec seconds..."
        sleep 1
    done
}

case "${1:-full}" in
    "--now"|"full")
        maim "$target_file"
        xclip -selection clipboard -t image/png < "$target_file"
        notify_view "$target_file"
        ;;
    "--area"|"area")
        maim -s "$target_file"
        if [ -s "$target_file" ]; then
            xclip -selection clipboard -t image/png < "$target_file"
            notify_view "$target_file"
        else
            rm -f "$target_file"
        fi
        ;;
    "--active"|"active")
        active_win=$(xdotool getactivewindow 2>/dev/null || echo "")
        if [ -n "$active_win" ]; then
            maim -i "$active_win" "$target_file"
            xclip -selection clipboard -t image/png < "$target_file"
            notify_view "$target_file"
        else
            notify-send -i "$iDoR/error.png" "Screenshot" "No active window found"
        fi
        ;;
    "--in5")
        countdown 5
        maim "$target_file"
        xclip -selection clipboard -t image/png < "$target_file"
        notify_view "$target_file"
        ;;
    "--in10")
        countdown 10
        maim "$target_file"
        xclip -selection clipboard -t image/png < "$target_file"
        notify_view "$target_file"
        ;;
    "--swappy"|"swappy")
        tmp_shot=$(mktemp --suffix=.png)
        maim -s "$tmp_shot"
        if [ -s "$tmp_shot" ]; then
            xclip -selection clipboard -t image/png < "$tmp_shot"
            cp "$tmp_shot" "$target_file"
            if command -v swappy >/dev/null 2>&1; then
                swappy -f "$tmp_shot" &
            fi
            notify_view "$target_file"
        fi
        rm -f "$tmp_shot"
        ;;
    *)
        maim "$target_file"
        xclip -selection clipboard -t image/png < "$target_file"
        notify_view "$target_file"
        ;;
esac
