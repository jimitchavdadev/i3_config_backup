#!/usr/bin/env bash
# /* ---- 💫 Dropdown Scratchpad Terminal for i3 💫 ---- */

if ! xdotool search --classname "dropdown_terminal" >/dev/null 2>&1; then
    kitty --class dropdown_terminal --name dropdown_terminal &
    sleep 0.3
fi

i3-msg '[instance="dropdown_terminal"] scratchpad show'
