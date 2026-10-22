#!/usr/bin/env bash
# Quick Settings Menu for i3 (SUPER SHIFT E)
set -euo pipefail

rofi_theme="$HOME/.config/rofi/config-edit.rasi"
sDIR="$HOME/.config/i3/scripts"

pkill -x rofi 2>/dev/null || true

options="📶  Network Connections (nm-connection-editor)
  Bluetooth Manager (blueman)
   Audio Mixer (pavucontrol)
󰍹  Display Settings (arandr)
🎮  Toggle GameMode
🌇  Toggle Night Light (Redshift)
󰈈  Toggle Window Blur (Picom)
✨  Switch Animations Profile
🎨  Choose Global Theme (Wallust)
🐱  Choose Kitty Terminal Theme
📝  Edit i3wm Configuration
📊  Edit Polybar Configuration
🔔  Edit Dunst Notifications
🐚  Edit Zsh Configuration (.zshrc)"

if [ -f "$rofi_theme" ]; then
    choice=$(echo -e "$options" | rofi -i -dmenu -config "$rofi_theme" -mesg "Quick Settings")
else
    choice=$(echo -e "$options" | rofi -i -dmenu -p "Quick Settings")
fi

[[ -z "$choice" ]] && exit 0

case "$choice" in
    *"Network"*) nm-connection-editor & ;;
    *"Bluetooth"*) blueman-manager & ;;
    *"Audio Mixer"*) pavucontrol & ;;
    *"Display Settings"*) arandr & ;;
    *"GameMode"*) "$sDIR/GameMode.sh" ;;
    *"Night Light"*) "$sDIR/Hyprsunset.sh" toggle ;;
    *"Window Blur"*) "$sDIR/ChangeBlur.sh" ;;
    *"Animations"*) "$sDIR/Animations.sh" ;;
    *"Global Theme"*) "$sDIR/ThemeChanger.sh" ;;
    *"Kitty"*) "$sDIR/Kitty_themes.sh" ;;
    *"Edit i3wm"*) ${EDITOR:-code} "$HOME/.config/i3/config" & ;;
    *"Edit Polybar"*) ${EDITOR:-code} "$HOME/.config/polybar/config.ini" & ;;
    *"Edit Dunst"*) ${EDITOR:-code} "$HOME/.config/dunst/dunstrc" & ;;
    *"Edit Zsh"*) ${EDITOR:-code} "$HOME/.zshrc" & ;;
esac
