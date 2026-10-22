#!/usr/bin/env bash
# Keybindings cheat sheet for i3
set -euo pipefail

pkill -x yad 2>/dev/null || true
pkill -x rofi 2>/dev/null || true

if command -v yad >/dev/null 2>&1; then
    yad --center \
        --title="i3wm Quick Cheat Sheet" \
        --width=750 --height=620 \
        --no-buttons \
        --list \
        --column="Key Combination" \
        --column="Action / Feature" \
        --column="Details" \
        "SUPER + Enter" "Terminal" "Launch Kitty" \
        "SUPER + Shift + Enter" "Dropdown Terminal" "Scratchpad Terminal" \
        "SUPER + D" "App Launcher" "Rofi application menu" \
        "SUPER + A" "Window Overview" "Overview of all windows & workspaces (Rofi)" \
        "SUPER + B" "Web Browser" "Launch Google Chrome" \
        "SUPER + Shift + B" "Private Browser" "Launch Google Chrome Incognito" \
        "SUPER + E" "File Manager" "Launch Thunar / Nautilus" \
        "SUPER + C" "Code Editor" "Launch VS Code" \
        "SUPER + Q" "Close Window" "Close active container" \
        "SUPER + Shift + Q" "Kill Process" "Force terminate active window" \
        "SUPER + F" "Fullscreen" "Toggle fullscreen" \
        "SUPER + Space" "Floating Toggle" "Toggle floating on active window" \
        "SUPER + G" "Group / Tabbed" "Toggle tabbed layout" \
        "SUPER + W" "Wallpaper Selector" "Preview & select wallpapers" \
        "SUPER + Shift + W" "Wallpaper Effects" "Apply ImageMagick effects" \
        "Ctrl + Alt + W" "Random Wallpaper" "Pick random wallpaper & colors" \
        "SUPER + T" "Global Theme Switcher" "Wallust dynamic palettes" \
        "SUPER + S" "Web Search" "Search Google directly via Rofi" \
        "SUPER + Ctrl + S" "Window Switcher" "Switch between active windows" \
        "SUPER + Alt + V" "Clipboard Manager" "Greenclip clipboard history" \
        "SUPER + Alt + E" "Emoji Picker" "Searchable emoji menu" \
        "SUPER + Alt + C" "Calculator" "Quick math with qalc/bc" \
        "SUPER + Shift + M" "RofiBeats" "Online music radio streamer" \
        "SUPER + Shift + E" "Quick Settings" "Wi-Fi, Bluetooth, Audio, Displays" \
        "SUPER + Shift + N" "Notification Center" "DND & Notification history" \
        "SUPER + N" "Night Light Toggle" "Redshift warm temperature mode" \
        "SUPER + Shift + G" "GameMode" "Disable picom & gaps for max FPS" \
        "SUPER + Alt + O" "Toggle Blur" "Enable/disable compositor blur" \
        "SUPER + Shift + A" "Animations" "Adjust picom animations profile" \
        "Print" "Screenshot Full" "Capture full desktop to file/clip" \
        "SUPER + Shift + S" "Screenshot Area (Swappy)" "Interactive snip & annotate" \
        "SUPER + L / Ctrl + Alt + L" "Lock Screen" "Lock desktop with blur" \
        "Ctrl + Alt + P" "Power Menu" "Lock, Suspend, Logout, Reboot, Poweroff" \
        "SUPER + Alt + R" "Refresh Desktop" "Reload bar, picom, dunst, i3" \
        "SUPER + Shift + R" "Restart i3" "In-place WM restart" \
        "SUPER + Shift + C" "Reload i3" "Reload configuration" \
        "SUPER + 1..10" "Workspaces" "Switch workspace 1 to 10" \
        "SUPER + Shift + 1..10" "Move Window" "Move active window to workspace"
else
    # Fallback to rofi if yad is unavailable
    cat << 'EOF' | rofi -dmenu -i -p "Keybindings" -theme-str 'window {width: 700px; height: 500px;}'
SUPER + Enter                 Launch Terminal (Kitty)
SUPER + Shift + Enter         Dropdown Terminal (Scratchpad)
SUPER + D                     Application Launcher (Rofi)
SUPER + B                     Launch Browser (Brave)
SUPER + Shift + B             Launch Browser Incognito
SUPER + E                     File Manager
SUPER + C                     VS Code
SUPER + Q                     Close Active Window
SUPER + Shift + Q             Kill Active Process
SUPER + F                     Toggle Fullscreen
SUPER + Space                 Toggle Floating
SUPER + G                     Toggle Tabbed / Group Layout
SUPER + W                     Wallpaper Selector
SUPER + Shift + W             Wallpaper Effects
Ctrl + Alt + W                Random Wallpaper
SUPER + T                     Global Theme Changer (Wallust)
SUPER + S                     Web Search Bar
SUPER + Ctrl + S              Window Switcher
SUPER + Alt + V               Clipboard History Manager
SUPER + Alt + E               Emoji Picker
SUPER + Alt + C               Calculator
SUPER + Shift + M             RofiBeats Music Streamer
SUPER + Shift + E             Quick Settings Menu
SUPER + Shift + N             Notification Center
SUPER + N                     Night Light Toggle
SUPER + Shift + G             GameMode Toggle
Print                         Full Screenshot
SUPER + Shift + S             Area Screenshot (Swappy)
SUPER + L / Ctrl + Alt + L    Lock Screen
Ctrl + Alt + P                Power Menu (Wlogout)
SUPER + Alt + R               Refresh Polybar, Picom, i3
SUPER + Shift + R             Restart i3
SUPER + Shift + C             Reload i3
EOF
fi
