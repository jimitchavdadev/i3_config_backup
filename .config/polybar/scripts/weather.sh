#!/usr/bin/env bash
CACHE_FILE="/tmp/polybar_weather_cache"
CACHE_AGE=900 # 15 minutes

get_weather() {
    local data
    data=$(curl -s --connect-timeout 3 "wttr.in?format=%c+%t" 2>/dev/null || true)
    if [ -n "$data" ] && [[ "$data" != *"Unknown"* ]] && [[ "$data" != *"50"* ]]; then
        local icon="󰖙"
        case "$data" in
            *🌧*|*🌦*) icon="󰖗" ;;
            *🌩*) icon="󰙾" ;;
            *🌨*) icon="󰖘" ;;
            *🌫*) icon="󰖑" ;;
            *☁*)  icon="󰖐" ;;
            *⛅*) icon="󰖕" ;;
            *✨*) icon="󰖙" ;;
            *)    icon="󰖙" ;;
        esac
        local temp
        temp=$(echo "$data" | sed -E 's/[^+-]*([+-]?[0-9]+.*)/\1/' | xargs)
        if [[ -z "$temp" ]]; then
            temp="+25°C"
        fi
        echo "$icon $temp" > "$CACHE_FILE"
        echo "$icon $temp"
    else
        if [ -f "$CACHE_FILE" ]; then
            cat "$CACHE_FILE"
        else
            echo "󰖙 N/A"
        fi
    fi
}

if [ -f "$CACHE_FILE" ]; then
    file_age=$(( $(date +%s) - $(stat -c %Y "$CACHE_FILE" 2>/dev/null || echo 0) ))
    if [ "$file_age" -lt "$CACHE_AGE" ]; then
        cat "$CACHE_FILE"
        exit 0
    fi
fi

get_weather
