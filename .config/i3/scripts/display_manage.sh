#!/usr/bin/env bash
# Display Management & Hotplug Handler for i3
# Handles connect/disconnect events, turns off phantom displays, and rescues orphaned workspaces
set -euo pipefail

action="${1:-auto}"
PRIMARY="eDP-1"
iDIR="$HOME/.config/swaync/images"

# Function to rescue any stranded workspaces
rescue_workspaces() {
    local active_outputs primary
    active_outputs=$(i3-msg -t get_outputs 2>/dev/null | jq -r '.[] | select(.active == true) | .name' || true)
    primary=$(i3-msg -t get_outputs 2>/dev/null | jq -r '.[] | select(.primary == true) | .name' || echo "$PRIMARY")
    [[ -z "$primary" ]] && primary=$(echo "$active_outputs" | head -n 1)

    if [[ -n "$active_outputs" && -n "$primary" ]]; then
        local act_json orphans
        act_json=$(printf '%s\n' "$active_outputs" | jq -R . | jq -s .)
        orphans=$(i3-msg -t get_workspaces 2>/dev/null | jq -r --argjson act "$act_json" '.[] | select(.output as $o | ($act | index($o)) == null) | .name' || true)
        for ws in $orphans; do
            i3-msg "workspace $ws, move workspace to output $primary" >/dev/null 2>&1 || true
        done
    fi
}

case "$action" in
    "laptop"|"single")
        # Explicitly turn off all disconnected or secondary outputs
        for out in $(xrandr | grep -E " (disconnected|connected)" | cut -d" " -f1); do
            if [[ "$out" != "$PRIMARY" ]]; then
                xrandr --output "$out" --off 2>/dev/null || true
            fi
        done
        xrandr --output "$PRIMARY" --auto --primary 2>/dev/null || true
        rescue_workspaces
        i3-msg reload >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/polybar/launch.sh" >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/i3/scripts/WallustFeh.sh" >/dev/null 2>&1 || true
        notify-send -i "$iDIR/ja.png" "Display" "Switched to Laptop display"
        ;;

    "dual")
        # Find external connected display
        ext=$(xrandr | grep " connected" | grep -v "$PRIMARY" | head -n 1 | cut -d" " -f1 || true)
        if [[ -n "$ext" ]]; then
            xrandr --output "$PRIMARY" --auto --primary --output "$ext" --auto --right-of "$PRIMARY" 2>/dev/null || true
            notify-send -i "$iDIR/ja.png" "Display" "Dual monitors configured ($PRIMARY + $ext)"
        else
            xrandr --output "$PRIMARY" --auto --primary 2>/dev/null || true
            notify-send -i "$iDIR/ja.png" "Display" "No external display found, using $PRIMARY"
        fi
        rescue_workspaces
        i3-msg reload >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/polybar/launch.sh" >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/i3/scripts/WallustFeh.sh" >/dev/null 2>&1 || true
        ;;

    "auto"|*)
        if command -v autorandr >/dev/null 2>&1; then
            autorandr --change --default horizontal >/dev/null 2>&1 || true
        fi
        # Turn off any outputs marked disconnected in xrandr that are still active
        for out in $(xrandr | grep " disconnected" | cut -d" " -f1); do
            xrandr --output "$out" --off 2>/dev/null || true
        done
        rescue_workspaces
        i3-msg reload >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/polybar/launch.sh" >/dev/null 2>&1 || true
        i3-msg "exec --no-startup-id $HOME/.config/i3/scripts/WallustFeh.sh" >/dev/null 2>&1 || true
        ;;
esac
