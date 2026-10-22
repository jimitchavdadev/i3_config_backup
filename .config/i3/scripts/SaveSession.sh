#!/usr/bin/env bash
# Save i3 session and execute power action
SESSION_FILE="$HOME/.cache/i3_saved_session.sh"

echo "#!/usr/bin/env bash" > "$SESSION_FILE"
echo "sleep 2" >> "$SESSION_FILE"

# Query i3-msg get_tree for windows with window_properties.class
if command -v jq >/dev/null 2>&1 && command -v i3-msg >/dev/null 2>&1; then
    tree_data=$(i3-msg -t get_tree 2>/dev/null || echo "")
    if [ -n "$tree_data" ]; then
        echo "$tree_data" | jq -r '
            recurse(.nodes[], .floating_nodes[])
            | select(.window_properties.class != null and .window_properties.class != "")
            | "\(.window_properties.class)"
        ' 2>/dev/null | sort -u | while read -r CLASS; do
            if [[ -n "$CLASS" && "$CLASS" != "Polybar" && "$CLASS" != "Dunst" && "$CLASS" != "scratchpad" ]]; then
                echo "gtk-launch \"$CLASS\" 2>/dev/null || ${CLASS,,} &" >> "$SESSION_FILE"
                echo "sleep 0.8" >> "$SESSION_FILE"
            fi
        done
    fi
fi

chmod +x "$SESSION_FILE"

if [ "${1:-}" = "reboot" ]; then
    systemctl reboot
elif [ "${1:-}" = "poweroff" ]; then
    systemctl poweroff
fi
