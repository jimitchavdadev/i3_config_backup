#!/usr/bin/env bash
# ==================================================
#  Polybar Tray Drawer Toggle (Windows-style)
# ==================================================
# Toggles visibility of background processes in polybar
set -euo pipefail

STATE_FILE="/tmp/polybar_tray_drawer_state"
state=$(cat "$STATE_FILE" 2>/dev/null || echo 0)

if [ "$state" = "1" ]; then
    echo 0 > "$STATE_FILE"
    polybar-msg action "#tray.module_hide" >/dev/null 2>&1 || true
    polybar-msg action "#tray-toggle.hook.0" >/dev/null 2>&1 || true
else
    echo 1 > "$STATE_FILE"
    polybar-msg action "#tray.module_show" >/dev/null 2>&1 || true
    polybar-msg action "#tray-toggle.hook.1" >/dev/null 2>&1 || true
fi
