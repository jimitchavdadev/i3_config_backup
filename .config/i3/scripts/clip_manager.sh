#!/usr/bin/env bash
# /* ---- 💫 Clipboard Manager for X11 (Greenclip + Rofi) 💫 ---- */

ROFI_THEME="$HOME/.config/rofi/config-clipboard.rasi"

if pgrep -x "rofi" >/dev/null; then pkill -x "rofi" || true; fi

# Ensure greenclip daemon is running
if ! pgrep -x "greenclip" >/dev/null; then
    greenclip daemon &
    sleep 0.2
fi

if [ -f "$ROFI_THEME" ]; then
    rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}' -config "$ROFI_THEME"
else
    rofi -modi "clipboard:greenclip print" -show clipboard -run-command '{cmd}'
fi
