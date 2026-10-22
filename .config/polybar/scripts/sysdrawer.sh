#!/usr/bin/env bash
# Collapsible System Specs Drawer for Polybar (IPC Module)
set -euo pipefail

STATE_FILE="/tmp/polybar_sysdrawer_state"
CPU_PREV_FILE="/tmp/polybar_sysdrawer_cpu"
NET_PREV_FILE="/tmp/polybar_sysdrawer_net"
COLORS_FILE="$HOME/.config/polybar/colors.ini"

action="${1:-collapsed}"

get_colors() {
    PRIMARY="#CA9885"
    DISABLED="#8E9CA2"
    if [ -f "$COLORS_FILE" ]; then
        PRIMARY=$(grep -E "^primary\s*=" "$COLORS_FILE" 2>/dev/null | awk '{print $3}' || echo "$PRIMARY")
        DISABLED=$(grep -E "^disabled\s*=" "$COLORS_FILE" 2>/dev/null | awk '{print $3}' || echo "$DISABLED")
    fi
}

get_temperature() {
    local t=0
    if [ -f /sys/class/thermal/thermal_zone17/temp ]; then
        t=$(cat /sys/class/thermal/thermal_zone17/temp 2>/dev/null || echo 0)
    elif [ -f /sys/class/thermal/thermal_zone14/temp ]; then
        t=$(cat /sys/class/thermal/thermal_zone14/temp 2>/dev/null || echo 0)
    elif [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        t=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo 0)
    fi
    echo $(( t / 1000 ))
}

get_cpu_usage() {
    local u n s i io irq sirq st total idle total_prev idle_prev diff_total diff_idle usage
    read -r _ u n s i io irq sirq st _ < /proc/stat
    total=$(( u + n + s + i + io + irq + sirq + st ))
    idle=$(( i + io ))

    if [ -f "$CPU_PREV_FILE" ]; then
        read -r total_prev idle_prev < "$CPU_PREV_FILE"
        diff_total=$(( total - total_prev ))
        diff_idle=$(( idle - idle_prev ))
        if [ "$diff_total" -gt 0 ]; then
            usage=$(( (diff_total - diff_idle) * 100 / diff_total ))
        else
            usage=0
        fi
    else
        usage=10
    fi
    echo "$total $idle" > "$CPU_PREV_FILE"
    echo "$usage"
}

get_mem_usage() {
    local total avail
    read -r _ total _ < <(grep "MemTotal:" /proc/meminfo)
    read -r _ avail _ < <(grep "MemAvailable:" /proc/meminfo)
    echo $(( (total - avail) * 100 / total ))
}

get_net_speed() {
    local iface rx now prev_rx prev_time dt diff rate
    iface=$(ip route get 1.1.1.1 2>/dev/null | grep -oP "dev \K\S+" || echo "wlp0s20f3")
    rx=$(cat "/sys/class/net/$iface/statistics/rx_bytes" 2>/dev/null || echo 0)
    now=$(date +%s)

    if [ -f "$NET_PREV_FILE" ]; then
        read -r prev_rx prev_time < "$NET_PREV_FILE"
        dt=$(( now - prev_time ))
        if [ "$dt" -gt 0 ]; then
            diff=$(( rx - prev_rx ))
            rate=$(( diff / dt ))
        else
            rate=0
        fi
    else
        rate=0
    fi
    echo "$rx $now" > "$NET_PREV_FILE"

    if [ "$rate" -ge 1048576 ]; then
        awk "BEGIN {printf \"%.1fM/s\", $rate/1048576}"
    elif [ "$rate" -ge 1024 ]; then
        awk "BEGIN {printf \"%.0fK/s\", $rate/1024}"
    else
        echo "${rate}B/s"
    fi
}

case "$action" in
    "toggle")
        state=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
        if [ "$state" = "1" ]; then
            echo 0 > "$STATE_FILE"
            polybar-msg action "#sysdrawer.hook.0" >/dev/null 2>&1 || true
        else
            echo 1 > "$STATE_FILE"
            polybar-msg action "#sysdrawer.hook.1" >/dev/null 2>&1 || true
        fi
        ;;
    "expand")
        state=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
        if [ "$state" != "1" ]; then
            echo 1 > "$STATE_FILE"
            polybar-msg action "#sysdrawer.hook.1" >/dev/null 2>&1 || true
        fi
        ;;
    "collapse")
        state=$(cat "$STATE_FILE" 2>/dev/null || echo 0)
        if [ "$state" != "0" ]; then
            echo 0 > "$STATE_FILE"
            polybar-msg action "#sysdrawer.hook.0" >/dev/null 2>&1 || true
        fi
        ;;
    "expanded")
        get_colors
        echo 1 > "$STATE_FILE"
        temp=$(get_temperature)
        cpu=$(get_cpu_usage)
        mem=$(get_mem_usage)
        net=$(get_net_speed)
        echo "%{F$PRIMARY}%{F-} ${temp}°C  %{F$PRIMARY}󰻠%{F-} ${cpu}%  %{F$PRIMARY}󰍛%{F-} ${mem}%  %{F$PRIMARY}󰇚%{F-} ${net} %{F$DISABLED}%{F-}"
        ;;
    "collapsed"|*)
        get_colors
        echo 0 > "$STATE_FILE"
        temp=$(get_temperature)
        echo "%{F$PRIMARY}%{F-} ${temp}°C %{F$DISABLED}%{F-}"
        ;;
esac
