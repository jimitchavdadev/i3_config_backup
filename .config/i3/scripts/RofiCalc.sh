#!/usr/bin/env bash
# Interactive Calculator using rofi and qalc/bc
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-calc.rasi"
calc_result=""

pkill -x rofi 2>/dev/null || true

while true; do
    if [ -f "$rofi_theme" ]; then
        result=$(rofi -i -dmenu -config "$rofi_theme" -mesg "$calc_result" 2>/dev/null || true)
    else
        result=$(rofi -i -dmenu -p "Calculate" -mesg "$calc_result" 2>/dev/null || true)
    fi

    [[ -z "$result" ]] && exit 0

    if command -v qalc >/dev/null 2>&1; then
        calc_result=$(qalc -t "$result" 2>/dev/null || echo "Error")
    else
        calc_result=$(echo "$result" | bc -l 2>/dev/null || echo "Error")
    fi

    echo "$calc_result" | xclip -selection clipboard 2>/dev/null || true
done
