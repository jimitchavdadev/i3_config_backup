#!/usr/bin/env bash
# Clipboard manager for i3 (supports greenclip & cliphist)
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-clipboard.rasi"
msg="👀 Note: Select an item to copy to clipboard"

pkill -x rofi 2>/dev/null || true

if command -v greenclip >/dev/null 2>&1; then
    if [ -f "$rofi_theme" ]; then
        rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}' -config "$rofi_theme" -mesg "$msg"
    else
        rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}' -mesg "$msg"
    fi
elif command -v cliphist >/dev/null 2>&1; then
    choice=$(cliphist list | rofi -i -dmenu -mesg "$msg" 2>/dev/null || true)
    if [ -n "$choice" ]; then
        cliphist decode <<<"$choice" | xclip -selection clipboard
    fi
fi
