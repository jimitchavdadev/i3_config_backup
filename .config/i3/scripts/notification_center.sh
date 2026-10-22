#!/usr/bin/env bash
# Notification Center menu for Dunst / i3
set -euo pipefail

IS_PAUSED=$(dunstctl is-paused 2>/dev/null || echo "false")

if [ "$IS_PAUSED" = "true" ]; then
    TOGGLE="🔕  Disable DND (Turn Notifications ON)"
    STATUS="Status: 🔴 Do Not Disturb Active"
else
    TOGGLE="🔔  Enable DND (Silence Notifications)"
    STATUS="Status: 🟢 Notifications Active"
fi

OPTIONS="$STATUS\n$TOGGLE\n📜  Show Last Notification (History Pop)\n📋  Open Notification Context Menu\n🗑️   Clear All Notifications & History"

CHOICE=$(echo -e "$OPTIONS" | rofi -dmenu -i -p "Notifications" \
    -theme-str 'window {width: 380px; border-radius: 12px;} listview {lines: 5;}')

case "$CHOICE" in
    *"DND"*)
        dunstctl set-paused toggle
        NEW_STATUS=$(dunstctl is-paused)
        if [ "$NEW_STATUS" = "true" ]; then
            notify-send "DND" "Notifications silenced"
        else
            notify-send "Notifications" "Notifications active"
        fi
        ;;
    *"Show Last"*)
        dunstctl history-pop
        ;;
    *"Context"*)
        dunstctl context
        ;;
    *"Clear All"*)
        dunstctl close-all
        dunstctl history-clear
        notify-send -t 1500 "Notifications" "History cleared"
        ;;
esac
