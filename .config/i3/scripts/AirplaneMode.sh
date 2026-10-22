#!/usr/bin/env bash
# Airplane Mode toggle using rfkill
set -euo pipefail

notif="$HOME/.config/swaync/images/ja.png"

wifi_blocked=$(rfkill list wifi 2>/dev/null | grep -o "Soft blocked: yes" || echo "")

if [ -n "$wifi_blocked" ]; then
    rfkill unblock wifi
    notify-send -u low -i "$notif" "Airplane Mode" "Disabled (Wi-Fi On)"
else
    rfkill block wifi
    notify-send -u low -i "$notif" "Airplane Mode" "Enabled (Wi-Fi Off)"
fi
