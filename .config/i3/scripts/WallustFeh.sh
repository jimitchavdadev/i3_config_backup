#!/usr/bin/env bash
# Wallust + Feh color updater for i3
set -euo pipefail

no_reload=0
passed_path=""
for arg in "$@"; do
    if [[ "$arg" == "--no-reload" ]]; then
        no_reload=1
    elif [[ -z "$passed_path" && -f "$arg" ]]; then
        passed_path="$arg"
    fi
done
rofi_link="$HOME/.config/rofi/.current_wallpaper"
wallpaper_current="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"
wallpaper_path=""

if [[ -n "$passed_path" && -f "$passed_path" ]]; then
    wallpaper_path="$passed_path"
elif [[ -f "$wallpaper_current" ]]; then
    wallpaper_path="$(cat "$wallpaper_current" 2>/dev/null || true)"
fi

if [[ -z "$wallpaper_path" || ! -f "$wallpaper_path" ]]; then
    wallpaper_path="$HOME/Pictures/wallpapers/wallpaper.jpeg"
fi

# Update current wallpaper references
mkdir -p "$(dirname "$wallpaper_current")" "$HOME/.config/rofi"
echo "$wallpaper_path" > "$wallpaper_current"
ln -sf "$wallpaper_path" "$rofi_link" 2>/dev/null || true

# Apply wallpaper with feh across all connected displays
monitors=$(xrandr --query 2>/dev/null | grep " connected" | cut -d" " -f1 || true)
if [[ -n "$monitors" ]]; then
    feh_args=()
    for _ in $monitors; do
        feh_args+=("$wallpaper_path")
    done
    feh --bg-fill "${feh_args[@]}" 2>/dev/null || feh --bg-fill "$wallpaper_path" 2>/dev/null || true
else
    feh --bg-fill "$wallpaper_path" 2>/dev/null || true
fi
chmod +x "$HOME/.fehbg" 2>/dev/null || true

# Run wallust (silent) to regenerate templates defined in ~/.config/wallust/wallust.toml
if command -v wallust >/dev/null 2>&1; then
    wallust run -s "$wallpaper_path" >/dev/null 2>&1 || true
elif [ -x "$HOME/.cargo/bin/wallust" ]; then
    "$HOME/.cargo/bin/wallust" run -s "$wallpaper_path" >/dev/null 2>&1 || true
fi

# Normalize Ghostty palette syntax if present
if [ -f "$HOME/.config/ghostty/wallust.conf" ]; then
    sed -i -E 's/^(\s*palette\s*=\s*)([0-9]{1,2}):/\1\2=/' "$HOME/.config/ghostty/wallust.conf" 2>/dev/null || true
fi

# Reload Kitty colors
if pidof kitty >/dev/null; then
    for pid in $(pidof kitty); do kill -SIGUSR1 "$pid" 2>/dev/null || true; done
fi

# Reload Ghostty colors
if pidof ghostty >/dev/null; then
    for pid in $(pidof ghostty); do kill -SIGUSR2 "$pid" 2>/dev/null || true; done
fi

if [[ "$no_reload" -eq 0 ]]; then
    # Reload Polybar
    if pidof polybar >/dev/null; then
        polybar-msg cmd restart >/dev/null 2>&1 || true
    fi

    # Reload Dunst
    if pidof dunst >/dev/null; then
        dunstctl reload 2>/dev/null || killall -SIGUSR2 dunst 2>/dev/null || true
    fi

    # Reload i3
    if command -v i3-msg >/dev/null 2>&1; then
        i3-msg reload >/dev/null 2>&1 || true
    fi
fi

# Pre-cache aesthetic lock screen background in background
if [ -x "$HOME/.config/i3/scripts/generate_lock_screen.py" ]; then
    nohup "$HOME/.config/i3/scripts/generate_lock_screen.py" --cache-base >/dev/null 2>&1 &
fi
