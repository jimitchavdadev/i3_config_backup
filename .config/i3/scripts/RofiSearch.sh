#!/usr/bin/env bash
# Web search using Rofi
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-search.rasi"
msg="Search the web via your default browser"

pkill -x rofi 2>/dev/null || true

if [ -f "$rofi_theme" ]; then
    query=$(printf '' | rofi -dmenu -config "$rofi_theme" -mesg "$msg" 2>/dev/null || true)
else
    query=$(printf '' | rofi -dmenu -p "Search Web" -mesg "$msg" 2>/dev/null || true)
fi

[[ -z "$query" ]] && exit 0

encoded=$(printf '%s' "$query" | jq -sRr @uri 2>/dev/null || echo "$query")
xdg-open "https://www.google.com/search?q=${encoded}" >/dev/null 2>&1 &
