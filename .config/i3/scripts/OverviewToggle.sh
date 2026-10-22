#!/usr/bin/env bash
# ==================================================
#  KoolDots - Overview / Window & Workspace Switcher
# ==================================================
# Toggles Rofi showing all open windows with workspace numbers and app icons

set -euo pipefail

# If rofi is already running, toggle it off
if pgrep -x rofi >/dev/null; then
    pkill -x rofi
    exit 0
fi

# Launch Rofi in window overview mode
rofi -show window \
    -modi window \
    -show-icons \
    -window-format "󰍹 WS {w}  │  {t}  ({c})" \
    -theme "$HOME/.config/rofi/config.rasi" \
    -p "Windows & Workspaces"
