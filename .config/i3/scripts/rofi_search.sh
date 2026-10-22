#!/usr/bin/env bash
# /* ---- 💫 Rofi Web Search 💫 ---- */
set -euo pipefail

ROFI_THEME="$HOME/.config/rofi/config-search.rasi"
MSG='🔎 Enter search query (opens in default browser)'

if pgrep -x "rofi" >/dev/null; then pkill -x "rofi" || true; fi

if [ -f "$ROFI_THEME" ]; then
    QUERY=$(printf '' | rofi -dmenu -config "$ROFI_THEME" -mesg "$MSG")
else
    QUERY=$(printf '' | rofi -dmenu -p "Search" -mesg "$MSG" -theme-str 'window {width: 450px;}')
fi

[[ -z "${QUERY:-}" ]] && exit 0

ENCODED=$(printf '%s' "$QUERY" | jq -sRr @uri)
xdg-open "https://www.google.com/search?q=${ENCODED}" >/dev/null 2>&1 &
