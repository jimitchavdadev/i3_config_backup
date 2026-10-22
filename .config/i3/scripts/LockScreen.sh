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
FADER_SCRIPT="$HOME/.config/i3/scripts/unlock_fader.py"

# Clean up fader background process on script exit
cleanup() {
    if [ -n "${FADER_PID:-}" ] && kill -0 "$FADER_PID" 2>/dev/null; then
        kill -9 "$FADER_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# Generate aesthetic multi-monitor lock wallpaper
BG_HEX="0F0E10"
if [ -f "$GEN_SCRIPT" ]; then
    eval "$("$GEN_SCRIPT" 2>/dev/null || echo "BG_HEX=0F0E10")"
fi

# Fallback image check
if [ ! -f "$OUTPUT_LOCK_IMG" ]; then
    OUTPUT_LOCK_IMG="/tmp/i3lock_blurred.png"
fi

# Launch the magical disappearing unlock fader overlay in background underneath i3lock
FADER_PID=""
if [ -f "$OUTPUT_LOCK_IMG" ] && [ -x "$FADER_SCRIPT" ]; then
    coproc FADER { "$FADER_SCRIPT" --bg "$OUTPUT_LOCK_IMG" --duration 0.72; }
    FADER_PID="${FADER_PID:-$!}"
    # Wait briefly for overlay window to report READY
    read -r -t 1 -u "${FADER[0]}" _ 2>/dev/null || true
fi

# Lock the screen with matching dark background canvas color and image
# -c: background canvas color (eliminates any white borders/flickers)
# -i: composite multi-monitor image
# -e: ignore empty password
# -f: show failed attempt counter
# -n: nofork (clean integration with systemd/xss-lock)
# -u: --no-unlock-indicator (makes the middle circle completely black/invisible when clicked or typed)
# -d: debug mode (emits 'Authentication failure' on PAM wrong password)
if [ -f "$OUTPUT_LOCK_IMG" ]; then
    LOCK_ARGS=(-c "${BG_HEX:-0F0E10}" -i "$OUTPUT_LOCK_IMG" -e -f -n -u -d)
else
    LOCK_ARGS=(-c "${BG_HEX:-0F0E10}" -e -f -n -u -d)
fi

# Run i3lock and monitor for Authentication failure in real-time
while IFS= read -r line; do
    if [[ "$line" == *"Authentication failure"* ]]; then
        if [ -n "${FADER_PID:-}" ] && kill -0 "$FADER_PID" 2>/dev/null; then
            echo "WRONG" >&"${FADER[1]}" 2>/dev/null || true
            kill -USR2 "$FADER_PID" 2>/dev/null || true
        fi
    fi
done < <(i3lock "${LOCK_ARGS[@]}" 2>&1)

# On successful password entry (i3lock exits cleanly):
# Trigger the magical disappearing animation to smoothly dissolve into the desktop
if [ -n "${FADER_PID:-}" ] && kill -0 "$FADER_PID" 2>/dev/null; then
    echo "DISAPPEAR" >&"${FADER[1]}" 2>/dev/null || true
    kill -USR1 "$FADER_PID" 2>/dev/null || true
    wait "$FADER_PID" 2>/dev/null || true
fi
