#!/usr/bin/env bash
# Power menu replicating wlogout actions for i3
set -euo pipefail

sDIR="$HOME/.config/i3/scripts"

# Actions matching wlogout: Lock, Suspend, Hibernate, Logout, Reboot, Shutdown
options="  Lock\n  Suspend\n󰤄  Hibernate\n  Logout\n  Reboot\n  Shutdown"

selected=$(echo -e "$options" | rofi -dmenu -i -p "Power" \
    -theme-str 'window {width: 280px; border: 2px; border-radius: 12px;} listview {lines: 6;}')

case "$selected" in
    *"Lock"*)
        "$sDIR/LockScreen.sh"
        ;;
    *"Suspend"*)
        systemctl suspend
        ;;
    *"Hibernate"*)
        systemctl hibernate
        ;;
    *"Logout"*)
        i3-msg exit
        ;;
    *"Reboot"*)
        "$sDIR/SaveSession.sh" reboot
        ;;
    *"Shutdown"*)
        "$sDIR/SaveSession.sh" poweroff
        ;;
esac
