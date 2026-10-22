#!/usr/bin/env bash
# /* ---- 💫 Searchable i3 Keybindings in Rofi 💫 ---- */
set -euo pipefail

ROFI_THEME="$HOME/.config/rofi/config-keybinds.rasi"

if pidof rofi >/dev/null; then pkill rofi || true; fi

BINDS="SUPER + Return              Open Terminal (kitty)
SUPER + SHIFT + Return        Dropdown Scratchpad Terminal
SUPER + D                     Application Launcher (Rofi drun)
SUPER + B                     Launch Web Browser
SUPER + SHIFT + B             Browser Incognito / Alternative
SUPER + E                     File Manager (Thunar / Nautilus)
SUPER + Q                     Close Focused Window
SUPER + SHIFT + Q             Kill Focused Process
SUPER + F                     Toggle Fullscreen
SUPER + SPACE                 Toggle Floating Mode
SUPER + U                     Toggle Scratchpad (Special Workspace)
SUPER + SHIFT + U             Move Window to Scratchpad
SUPER + T                     Global Theme Switcher (Wallust)
SUPER + W                     Choose Wallpaper (Rofi Previews)
SUPER + SHIFT + W             Wallpaper Effects Menu
CTRL + ALT + W                Random Wallpaper
SUPER + SHIFT + M             Online Music / Lo-Fi Streams (RofiBeats)
SUPER + S                     Google / Web Search in Browser
SUPER + CTRL + S              Window Switcher
SUPER + ALT + V               Clipboard History Manager (Greenclip)
SUPER + ALT + E               Emoji Picker
SUPER + ALT + C               Calculator (Qalc)
SUPER + SHIFT + N             Notification Center (Dunst)
SUPER + SHIFT + E             KooL Quick Settings Menu
SUPER + H                     Keybindings Cheatsheet (Yad)
SUPER + SHIFT + K             Search All Keybinds (This Menu)
SUPER + ALT + R               Refresh Polybar, Picom, Dunst & i3
SUPER + ALT + O               Toggle Compositor Blur
SUPER + SHIFT + G             Game Mode (Toggle Picom)
CTRL + ALT + L / SUPER + L    Lock Screen
CTRL + ALT + P                Power Menu (Wlogout Style)
CTRL + ALT + Delete           Exit i3 Session
SUPER + 1..10                 Switch to Workspace 1..10
SUPER + SHIFT + 1..10         Move Window to Workspace 1..10
SUPER + Tab                   Next Workspace
SUPER + grave                 Previous Workspace
Print / SUPER + Print         Screenshot (Full Screen)
SUPER + SHIFT + S             Screenshot (Area / Flameshot)
ALT + Print                   Screenshot (Active Window)
AudioRaiseVolume / Lower      Volume Up / Down
AudioMute                     Toggle Mute
AudioMicMute                  Toggle Microphone Mute
MonBrightnessUp / Down        Brightness Up / Down
AudioPlay / Next / Prev       Media Play-Pause / Next / Prev"

if [ -f "$ROFI_THEME" ]; then
    echo -e "$BINDS" | rofi -dmenu -i -p "Keybinds" -config "$ROFI_THEME" -mesg "Press ESC to close"
else
    echo -e "$BINDS" | rofi -dmenu -i -p "Keybinds" -theme-str 'window {width: 650px;} listview {lines: 12;}'
fi
