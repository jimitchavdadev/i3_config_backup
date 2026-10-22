#!/usr/bin/env bash
# /* ---- 💫 Global Wallust Theme Changer 💫 ---- */
set -euo pipefail

WALLUST_BIN="wallust"
if ! command -v wallust >/dev/null 2>&1; then
    if [ -x "$HOME/.cargo/bin/wallust" ]; then
        WALLUST_BIN="$HOME/.cargo/bin/wallust"
    else
        notify-send -u critical "Theme Changer" "wallust binary not found"
        exit 1
    fi
fi

set +e
choice="$($WALLUST_BIN theme list \
  | sed -e '1d' -e 's/^- //' \
  | rofi -dmenu -i -p 'Select Global Theme')"
prompt_status=$?
set -e

if (( prompt_status != 0 )) || [[ -z "${choice}" ]]; then
  exit 0
fi

if $WALLUST_BIN theme -- "${choice}"; then
  # Normalize Rofi selection colors
  rofi_colors="$HOME/.config/rofi/wallust/colors-rofi.rasi"
  if [ -f "$rofi_colors" ]; then
    accent_hex=$(sed -n 's/^\s*color12:\s*\(#[0-9A-Fa-f]\{6\}\).*/\1/p' "$rofi_colors" | head -n1)
    if [ -n "$accent_hex" ]; then
      sed -i -E "s|^(\s*selected-normal-background:\s*).*$|\1$accent_hex;|" "$rofi_colors" 2>/dev/null || true
      sed -i -E "s|^(\s*selected-active-background:\s*).*$|\1$accent_hex;|" "$rofi_colors" 2>/dev/null || true
    fi
  fi

  ~/.config/i3/scripts/refresh.sh
  notify-send -a ThemeChanger "Global Theme Changed" "Selected: ${choice}"
else
  notify-send -u critical "Theme Changer" "Failed to apply theme ${choice}"
fi
