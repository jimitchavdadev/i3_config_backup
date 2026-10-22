#!/usr/bin/env bash
# ==================================================
#  Aesthetic Multi-Monitor Screen Locker for i3
# ==================================================
set -euo pipefail

# Prevent duplicate lock processes
if pgrep -x i3lock >/dev/null; then
    exit 0
fi

OUTPUT_LOCK_IMG="/tmp/i3lock_aesthetic.png"
GEN_SCRIPT="$HOME/.config/i3/scripts/generate_lock_screen.py"

# Generate aesthetic multi-monitor lock wallpaper
BG_HEX="1A1313"
if [ -f "$GEN_SCRIPT" ]; then
    eval "$("$GEN_SCRIPT" 2>/dev/null || echo "BG_HEX=1A1313")"
fi

# Fallback image check
if [ ! -f "$OUTPUT_LOCK_IMG" ]; then
    OUTPUT_LOCK_IMG="/tmp/i3lock_blurred.png"
fi

# Lock the screen with matching dark background canvas color and image
# -c: background canvas color (eliminates any white borders/flickers)
# -i: composite multi-monitor image
# -e: ignore empty password
# -f: show failed attempt counter
# -n: nofork (clean integration with systemd/xss-lock)
if [ -f "$OUTPUT_LOCK_IMG" ]; then
    exec i3lock -c "${BG_HEX:-1A1313}" -i "$OUTPUT_LOCK_IMG" -e -f -n
else
    exec i3lock -c "${BG_HEX:-1A1313}" -e -f -n
fi
