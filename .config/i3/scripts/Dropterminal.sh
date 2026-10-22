#!/usr/bin/env bash
# Dropdown Terminal for i3 using Scratchpad
set -euo pipefail

terminal="${1:-kitty}"

# Check if dropdown terminal window exists in X11
if ! xdotool search --classname "dropdown_terminal" 2>/dev/null | grep -q .; then
    "$terminal" --class dropdown_terminal --name dropdown_terminal &
    sleep 0.3
fi

i3-msg '[instance="dropdown_terminal"] scratchpad show' >/dev/null 2>&1
