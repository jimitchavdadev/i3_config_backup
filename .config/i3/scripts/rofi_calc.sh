#!/usr/bin/env bash
# /* ---- 💫 Rofi Calculator (Qalculate) 💫 ---- */

ROFI_THEME="$HOME/.config/rofi/config-calc.rasi"

if pgrep -x "rofi" >/dev/null; then pkill -x "rofi" || true; fi

result=""
calc_result=""

while true; do
    if [ -f "$ROFI_THEME" ]; then
        result=$(rofi -i -dmenu -config "$ROFI_THEME" -mesg "$result = $calc_result")
    else
        result=$(rofi -i -dmenu -p "Calc" -mesg "$result = $calc_result" -theme-str 'window {width: 400px;}')
    fi

    if [ $? -ne 0 ]; then
        exit 0
    fi

    if [ -n "$result" ]; then
        if command -v qalc >/dev/null 2>&1; then
            calc_result=$(qalc -t "$result" 2>/dev/null || echo "Error")
        elif command -v bc >/dev/null 2>&1; then
            calc_result=$(echo "$result" | bc -l 2>/dev/null || echo "Error")
        fi
        echo -n "$calc_result" | xclip -selection clipboard 2>/dev/null || true
    fi
done
