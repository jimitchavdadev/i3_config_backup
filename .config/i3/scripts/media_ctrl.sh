#!/usr/bin/env bash
# Media Controls using playerctl
set -euo pipefail

iDIR="$HOME/.config/swaync/icons"

case "${1:-}" in
    "--pause"|"play-pause")
        playerctl play-pause 2>/dev/null || true
        title=$(playerctl metadata --format '{{title}} - {{artist}}' 2>/dev/null || echo "Play/Pause")
        notify-send -t 2000 -i "$iDIR/music.png" "Media" "$title" 2>/dev/null || true
        ;;
    "--nxt"|"next")
        playerctl next 2>/dev/null || true
        sleep 0.2
        title=$(playerctl metadata --format '{{title}} - {{artist}}' 2>/dev/null || echo "Next Track")
        notify-send -t 2000 -i "$iDIR/music.png" "Media Next" "$title" 2>/dev/null || true
        ;;
    "--prv"|"prev")
        playerctl previous 2>/dev/null || true
        sleep 0.2
        title=$(playerctl metadata --format '{{title}} - {{artist}}' 2>/dev/null || echo "Previous Track")
        notify-send -t 2000 -i "$iDIR/music.png" "Media Previous" "$title" 2>/dev/null || true
        ;;
    "--stop"|"stop")
        playerctl stop 2>/dev/null || true
        notify-send -t 1500 -i "$iDIR/music.png" "Media" "Stopped" 2>/dev/null || true
        ;;
esac
