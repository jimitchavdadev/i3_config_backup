#!/usr/bin/env bash
# ==================================================
#  Workspace Cycling for i3 (Per-Display / Multi-Monitor)
# ==================================================
# Cycles strictly through workspaces active on the currently focused display,
# preventing cross-display jumping during multi-monitor setups.
set -euo pipefail

dir="${1:-next}"

# 1. Rescue any workspaces stranded on disconnected/inactive outputs
active_outputs=$(i3-msg -t get_outputs 2>/dev/null | jq -r '.[] | select(.active == true) | .name' || true)
primary_output=$(i3-msg -t get_outputs 2>/dev/null | jq -r '.[] | select(.primary == true) | .name' || true)
if [[ -z "$primary_output" ]]; then
    primary_output=$(echo "$active_outputs" | head -n 1)
fi

if [[ -n "$active_outputs" && -n "$primary_output" ]]; then
    act_json=$(printf '%s\n' "$active_outputs" | jq -R . | jq -s .)
    orphans=$(i3-msg -t get_workspaces 2>/dev/null | jq -r --argjson act "$act_json" '.[] | select(.output as $o | ($act | index($o)) == null) | .name' || true)
    for ws in $orphans; do
        i3-msg "workspace $ws, move workspace to output $primary_output" >/dev/null 2>&1 || true
    done
fi

# 2. Retrieve current workspace state
ws_json=$(i3-msg -t get_workspaces 2>/dev/null || true)
if [[ -z "$ws_json" || "$ws_json" == "[]" ]]; then
    exit 0
fi

# 3. Detect current focused output and workspace
current_output=$(echo "$ws_json" | jq -r '.[] | select(.focused == true) | .output // empty' | head -n 1)
current_ws=$(echo "$ws_json" | jq -r '.[] | select(.focused == true) | .name // empty' | head -n 1)

if [[ -z "$current_output" ]]; then
    current_output="$primary_output"
fi

# 4. Filter workspaces ONLY belonging to the current focused monitor
mapfile -t workspaces < <(echo "$ws_json" | jq -r --arg out "$current_output" 'sort_by(.num) | .[] | select(.output == $out) | .name' || true)

total=${#workspaces[@]}
if [ "$total" -le 1 ]; then
    # Fallback: if only 1 workspace exists on this monitor, cycle all open workspaces
    # so navigation never gets dead-locked on the extended display
    mapfile -t workspaces < <(echo "$ws_json" | jq -r 'sort_by(.num) | .[].name' || true)
    total=${#workspaces[@]}
    if [ "$total" -le 1 ]; then
        exit 0
    fi
fi

# 5. Find index of current focused workspace within this monitor's workspaces
current_idx=-1
for i in "${!workspaces[@]}"; do
    if [[ "${workspaces[$i]}" == "$current_ws" ]]; then
        current_idx=$i
        break
    fi
done

if [ "$current_idx" -eq -1 ]; then
    current_idx=0
fi

# 6. Calculate next or previous index with wrap-around on this monitor
if [ "$dir" = "next" ]; then
    target_idx=$(( (current_idx + 1) % total ))
else
    target_idx=$(( (current_idx - 1 + total) % total ))
fi

target="${workspaces[$target_idx]}"

# 7. Switch to the target workspace on the current monitor
i3-msg "workspace $target" >/dev/null 2>&1
