#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG_DIR = path.resolve(__dirname);
const HOME = process.env.HOME;
const SCRIPTS_DIR = path.join(CONFIG_DIR, 'scripts');

// Utility functions
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function writeScript(filePath, content) {
  fs.writeFileSync(filePath, content, { mode: 0o755 });
  console.log(`✓ Created: ${path.relative(CONFIG_DIR, filePath)}`);
}

function backupFile(filePath) {
  if (fs.existsSync(filePath)) {
    const backup = `${filePath}.backup.${Date.now()}`;
    fs.copyFileSync(filePath, backup);
    console.log(`📦 Backed up: ${path.relative(CONFIG_DIR, filePath)}`);
  }
}

console.log('🚀 Starting i3 → Hyprland-style Transformation...\n');

// ============================================================================
// 1. CREATE DIRECTORY STRUCTURE
// ============================================================================
console.log('📁 Creating directory structure...');

const dirs = [
  SCRIPTS_DIR,
  path.join(CONFIG_DIR, 'themes'),
  path.join(CONFIG_DIR, 'wallpaper_effects'),
  path.join(HOME, 'Pictures/wallpapers'),
  path.join(HOME, 'Pictures/Screenshots'),
  path.join(HOME, '.cache/i3'),
  path.join(HOME, '.config/polybar'),
];

dirs.forEach(ensureDir);

// ============================================================================
// 2. ENHANCED SCRIPTS
// ============================================================================
console.log('\n📝 Creating enhanced scripts...');

// 2.1 Wallpaper Select
writeScript(path.join(SCRIPTS_DIR, 'wallpaper_select.sh'), `#!/bin/bash
# Enhanced Wallpaper Selector with Preview

WALL_DIR="$HOME/Pictures/wallpapers"
CACHE_DIR="$HOME/.cache/i3/wallpapers"
CURRENT="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"

mkdir -p "$CACHE_DIR"
mkdir -p "$(dirname "$CURRENT")"

if [ ! -d "$WALL_DIR" ]; then
    mkdir -p "$WALL_DIR"
    notify-send "Wallpaper" "Created $WALL_DIR - Add wallpapers there!"
    exit 1
fi

# Generate thumbnails for preview
generate_preview() {
    local img="$1"
    local thumb="$CACHE_DIR/$(basename "$img").thumb.jpg"
    
    if [ ! -f "$thumb" ] || [ "$img" -nt "$thumb" ]; then
        convert "$img" -resize 200x200^ -gravity center -extent 200x200 "$thumb" 2>/dev/null
    fi
    echo "$thumb"
}

# Select wallpaper with Rofi
SELECTED=$(find "$WALL_DIR" -type f \\( -iname "*.jpg" -o -iname "*.png" -o -iname "*.jpeg" \\) | while read -r img; do
    thumb=$(generate_preview "$img")
    echo -en "$(basename "$img")\\x00icon\\x1f$thumb\\n"
done | rofi -dmenu -i -p "Wallpaper" -show-icons)

if [ -n "$SELECTED" ]; then
    FULL_PATH="$WALL_DIR/$SELECTED"
    
    # Apply wallpaper
    feh --bg-fill "$FULL_PATH"
    
    # Save current wallpaper
    cp "$FULL_PATH" "$CURRENT"
    
    # Update pywal colors (if installed)
    if command -v wal &>/dev/null; then
        wal -i "$FULL_PATH" -n -q
    fi
    
    # Save restore command
    echo "feh --bg-fill '$FULL_PATH'" > "$HOME/.fehbg"
    chmod +x "$HOME/.fehbg"
    
    # Refresh polybar if running
    if pgrep -x polybar >/dev/null; then
        ~/.config/polybar/launch.sh &
    fi
    
    notify-send -i "$FULL_PATH" "Wallpaper" "Applied: $SELECTED"
fi
`);

// 2.2 Wallpaper Effects
writeScript(path.join(SCRIPTS_DIR, 'wallpaper_effects.sh'), `#!/bin/bash
# Wallpaper Effects using ImageMagick

CURRENT="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"
OUTPUT="$HOME/.config/i3/wallpaper_effects/.wallpaper_modified"

if [ ! -f "$CURRENT" ]; then
    notify-send "Error" "No wallpaper selected yet!"
    exit 1
fi

EFFECTS="No Effects
Black & White
Blurred
Charcoal
Edge Detect
Emboss
Oil Paint
Sepia Tone
Sharpen
Vignette"

CHOICE=$(echo "$EFFECTS" | rofi -dmenu -i -p "Wallpaper Effect")

case "$CHOICE" in
    "No Effects")
        feh --bg-fill "$CURRENT"
        notify-send "Wallpaper" "Original applied"
        ;;
    "Black & White")
        convert "$CURRENT" -colorspace gray -sigmoidal-contrast 10,40% "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Black & White applied"
        ;;
    "Blurred")
        convert "$CURRENT" -blur 0x10 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Blur applied"
        ;;
    "Charcoal")
        convert "$CURRENT" -charcoal 0x5 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Charcoal applied"
        ;;
    "Edge Detect")
        convert "$CURRENT" -edge 1 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Edge Detect applied"
        ;;
    "Emboss")
        convert "$CURRENT" -emboss 0x5 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Emboss applied"
        ;;
    "Oil Paint")
        convert "$CURRENT" -paint 4 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Oil Paint applied"
        ;;
    "Sepia Tone")
        convert "$CURRENT" -sepia-tone 65% "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Sepia Tone applied"
        ;;
    "Sharpen")
        convert "$CURRENT" -sharpen 0x5 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Sharpen applied"
        ;;
    "Vignette")
        convert "$CURRENT" -vignette 0x3 "$OUTPUT"
        feh --bg-fill "$OUTPUT"
        notify-send "Wallpaper" "Vignette applied"
        ;;
esac

# Update pywal if installed
if command -v wal &>/dev/null && [ -f "$OUTPUT" ]; then
    wal -i "$OUTPUT" -n -q
fi
`);

// 2.3 Screenshot (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'screenshot.sh'), `#!/bin/bash
DIR="$HOME/Pictures/Screenshots"
mkdir -p "$DIR"
NAME="Screenshot_$(date +%Y%m%d_%H%M%S).png"

case "$1" in
    "full")
        maim "$DIR/$NAME"
        xclip -selection clipboard -t image/png < "$DIR/$NAME"
        notify-send "Screenshot" "Full screen captured saved to $DIR" -i "$DIR/$NAME"
        ;;
    "area")
        maim -s "$DIR/$NAME"
        xclip -selection clipboard -t image/png < "$DIR/$NAME"
        notify-send "Screenshot" "Area captured saved to $DIR" -i "$DIR/$NAME"
        ;;
esac
`);

// 2.4 Volume (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'volume.sh'), `#!/bin/bash
# Uses pamixer or pactl
case "$1" in
    up)
        pamixer -i 5 || pactl set-sink-volume @DEFAULT_SINK@ +5%
        ;;
    down)
        pamixer -d 5 || pactl set-sink-volume @DEFAULT_SINK@ -5%
        ;;
    mute)
        pamixer -t || pactl set-sink-mute @DEFAULT_SINK@ toggle
        ;;
esac

# Send notification
VOL=$(pamixer --get-volume || pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\\d+%' | head -1)
notify-send -r 1001 -h int:value:"$VOL" "Volume" "Level: $VOL%"
`);

// 2.5 Brightness (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'brightness.sh'), `#!/bin/bash
case "$1" in
    up)
        brightnessctl s +5%
        ;;
    down)
        brightnessctl s 5%-
        ;;
esac

VAL=$(brightnessctl g)
MAX=$(brightnessctl m)
PERCENT=$((VAL * 100 / MAX))
notify-send -r 1002 -h int:value:"$PERCENT" "Brightness" "Level: $PERCENT%"
`);

// 2.6 Power Menu (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'power_menu.sh'), `#!/bin/bash
# Rofi Power Menu

options="Lock\\nLogout\\nReboot\\nShutdown\\nSuspend"

selected=$(echo -e "$options" | rofi -dmenu -i -p "Power" -theme-str 'window {width: 300px;} listview {lines: 5;}')

case "$selected" in
    "Lock")
        ~/.config/i3/scripts/lock.sh
        ;;
    "Logout")
        i3-msg exit
        ;;
    "Reboot")
        systemctl reboot
        ;;
    "Shutdown")
        systemctl poweroff
        ;;
    "Suspend")
        systemctl suspend
        ;;
esac
`);

// 2.7 Lock Screen (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'lock.sh'), `#!/bin/bash
# Checks for i3lock-color or falls back to i3lock

if command -v i3lock-color &>/dev/null; then
    i3lock-color --blur 5 --clock --indicator --ring-color=89b4fa --keyhl-color=a6e3a1
else
    i3lock -c 1e1e2e
fi
`);

// 2.8 Gamemode (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'gamemode.sh'), `#!/bin/bash
# Toggle Compositor for gaming

if pgrep -x picom >/dev/null; then
    killall picom
    notify-send "Game Mode" "Compositor Disabled (Max Performance)"
else
    picom -b
    notify-send "Game Mode" "Compositor Enabled"
fi
`);

// 2.9 Rainbow Borders (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'rainbow_borders.sh'), `#!/bin/bash
# Simple script to cycle border colors for focused window

while true; do
    i3-msg client.focused border pixel 3 >/dev/null
    i3-msg client.focused border color #ff0000 >/dev/null
    sleep 3
    i3-msg client.focused border color #00ff00 >/dev/null
    sleep 3
    i3-msg client.focused border color #0000ff >/dev/null
    sleep 3
done
`);

// 2.10 Quick Settings (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'quick_settings.sh'), `#!/bin/bash
# Quick Rofi menu for common toggles

OPTIONS="Wifi Menu\\nBluetooth Menu\\nAudio Mixer\\nDisplay Settings"

CHOICE=$(echo -e "$OPTIONS" | rofi -dmenu -i -p "Settings")

case "$CHOICE" in
    "Wifi Menu")
        nm-connection-editor &
        ;;
    "Bluetooth Menu")
        blueman-manager &
        ;;
    "Audio Mixer")
        pavucontrol &
        ;;
    "Display Settings")
        arandr &
        ;;
esac
`);

// 2.11 Keyhints (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'keyhints.sh'), `#!/bin/bash
# Simple keyhint display
notify-send "Keybindings" "Super+Return: Term\\nSuper+D: Launcher\\nSuper+W: Wallpaper\\nSuper+Shift+E: Settings" -t 10000
`);

// 2.12 RofiBeats (MISSING IN ORIGINAL)
writeScript(path.join(SCRIPTS_DIR, 'rofibeats.sh'), `#!/bin/bash
# Simple LoFi Radio Player
OPTIONS="Lofi Girl\\nChillhop\\nSmooth Jazz\\nStop All"

CHOICE=$(echo -e "$OPTIONS" | rofi -dmenu -i -p "Radio")

case "$CHOICE" in
    "Lofi Girl")
        pkill mpv
        mpv --no-video "https://www.youtube.com/watch?v=jfKfPfyJRdk" &
        notify-send "Radio" "Playing Lofi Girl"
        ;;
    "Stop All")
        pkill mpv
        ;;
esac
`);

// 2.13 Refresh
writeScript(path.join(SCRIPTS_DIR, 'refresh.sh'), `#!/bin/bash
# Refresh all i3 components

# Kill and restart polybar
if command -v polybar &>/dev/null; then
    killall -q polybar
    while pgrep -x polybar >/dev/null; do sleep 0.1; done
    ~/.config/polybar/launch.sh &
fi

# Restart picom
if command -v picom &>/dev/null; then
    killall -q picom
    sleep 0.5
    picom -b &
fi

# Reload dunst
if command -v dunst &>/dev/null; then
    killall -SIGUSR2 dunst 2>/dev/null
fi

# Reload i3
i3-msg reload

notify-send "i3" "Refreshed all components"
`);

// 2.14 Animations
writeScript(path.join(SCRIPTS_DIR, 'animations.sh'), `#!/bin/bash
# Animation Profiles Selector

PICOM_CONFIG="$HOME/.config/picom/picom.conf"
ANIMATIONS_DIR="$HOME/.config/i3/themes/animations"

mkdir -p "$ANIMATIONS_DIR"

# Create animation profiles
if [ ! -f "$ANIMATIONS_DIR/default.conf" ]; then
    cat > "$ANIMATIONS_DIR/default.conf" << 'EOF'
fading = true;
fade-delta = 10;
transition-length = 300;
transition-pow-x = 0.5;
size-transition = true;
EOF
fi

if [ ! -f "$ANIMATIONS_DIR/fast.conf" ]; then
    cat > "$ANIMATIONS_DIR/fast.conf" << 'EOF'
fading = true;
fade-delta = 5;
transition-length = 150;
transition-pow-x = 0.1;
size-transition = true;
EOF
fi

PROFILES=$(ls "$ANIMATIONS_DIR" | sed 's/.conf//')
CHOICE=$(echo "$PROFILES" | rofi -dmenu -i -p "Animation Profile")

if [ -n "$CHOICE" ]; then
    # Note: Simplistic append strategy
    # For a real robust solution, you'd use a separate include file in picom
    notify-send "Animations" "Selected $CHOICE (Requires Picom Restart)"
    killall -q picom
    sleep 0.5
    picom -b &
fi
`);

// 2.15 Monitor Profiles
writeScript(path.join(SCRIPTS_DIR, 'monitor_profiles.sh'), `#!/bin/bash
PROFILES_DIR="$HOME/.config/i3/monitor_profiles"
mkdir -p "$PROFILES_DIR"

if [ -z "$(ls -A "$PROFILES_DIR")" ]; then
    cat > "$PROFILES_DIR/laptop.sh" << 'EOF'
#!/bin/bash
xrandr --output eDP-1 --auto --primary
EOF
    chmod +x "$PROFILES_DIR/laptop.sh"
fi

PROFILES=$(ls "$PROFILES_DIR" | sed 's/.sh//')
CHOICE=$(echo "$PROFILES" | rofi -dmenu -i -p "Monitor Profile")

if [ -n "$CHOICE" ]; then
    bash "$PROFILES_DIR/$CHOICE.sh"
    i3-msg restart
    notify-send "Monitor" "Profile applied: $CHOICE"
fi
`);

// 2.16 Dark/Light
writeScript(path.join(SCRIPTS_DIR, 'dark_light.sh'), `#!/bin/bash
CACHE_FILE="$HOME/.cache/i3/.theme_mode"
mkdir -p "$(dirname "$CACHE_FILE")"

if [ ! -f "$CACHE_FILE" ]; then echo "Dark" > "$CACHE_FILE"; fi
CURRENT=$(cat "$CACHE_FILE")

if [ "$CURRENT" == "Dark" ]; then NEW="Light"; else NEW="Dark"; fi
echo "$NEW" > "$CACHE_FILE"

if [ "$NEW" == "Dark" ]; then
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita-dark" 2>/dev/null || true
else
    gsettings set org.gnome.desktop.interface gtk-theme "Adwaita" 2>/dev/null || true
fi

~/.config/i3/scripts/refresh.sh
notify-send "Theme" "Switched to $NEW mode"
`);

// 2.17 Random Wallpaper
writeScript(path.join(SCRIPTS_DIR, 'wallpaper_random.sh'), `#!/bin/bash
WALL_DIR="$HOME/Pictures/wallpapers"
CURRENT="$HOME/.config/i3/wallpaper_effects/.wallpaper_current"

if [ ! -d "$WALL_DIR" ]; then exit 1; fi

WALLPAPERS=($(find "$WALL_DIR" -type f \\( -iname "*.jpg" -o -iname "*.png" \\)))
if [ \${#WALLPAPERS[@]} -eq 0 ]; then exit 1; fi

RANDOM_WALL="\${WALLPAPERS[\$RANDOM % \${#WALLPAPERS[@]}]}"

feh --bg-fill "$RANDOM_WALL"
cp "$RANDOM_WALL" "$CURRENT"
if command -v wal &>/dev/null; then wal -i "$RANDOM_WALL" -n -q; fi
`);

// 2.18 Keyboard Layout
writeScript(path.join(SCRIPTS_DIR, 'keyboard_layout.sh'), `#!/bin/bash
LAYOUTS="us\\nus intl\\ngb\\nde\\nfr\\nes"
CURRENT=$(setxkbmap -query | grep layout | awk '{print $2}')
CHOICE=$(echo -e "$LAYOUTS" | rofi -dmenu -i -p "Keyboard Layout" -select "$CURRENT")

if [ -n "$CHOICE" ]; then
    setxkbmap "$CHOICE"
    notify-send "Keyboard" "Layout: $CHOICE"
fi
`);

// 2.19 Change Blur
writeScript(path.join(SCRIPTS_DIR, 'change_blur.sh'), `#!/bin/bash
PICOM_CONFIG="$HOME/.config/picom/picom.conf"
if [ ! -f "$PICOM_CONFIG" ]; then exit 1; fi

CURRENT=$(grep "blur-strength" "$PICOM_CONFIG" | grep -oP '\\d+' | head -1)

if [ -z "$CURRENT" ] || [ "$CURRENT" -lt 5 ]; then
    NEW=10; MSG="Strong Blur"
else
    NEW=2; MSG="Light Blur"
fi

sed -i "s/blur-strength = .*/blur-strength = $NEW;/" "$PICOM_CONFIG"
killall -q picom; picom -b &
notify-send "Blur" "$MSG Applied"
`);

// 2.20 Idle Handler
writeScript(path.join(SCRIPTS_DIR, 'idle_handler.sh'), `#!/bin/bash
IDLE_TIME=600
LOCK_SCRIPT="$HOME/.config/i3/scripts/lock.sh"
xidlehook --not-when-fullscreen --not-when-audio --timer $IDLE_TIME "$LOCK_SCRIPT" '' &
`);

// 2.21 Media Ctrl
writeScript(path.join(SCRIPTS_DIR, 'media_ctrl.sh'), `#!/bin/bash
case "$1" in
    play-pause) playerctl play-pause ;;
    next) playerctl next ;;
    prev) playerctl previous ;;
esac
`);

// ============================================================================
// 3. UPDATE i3 CONFIG
// ============================================================================
console.log('\n⚙️  Updating i3 config...');

const configPath = path.join(CONFIG_DIR, 'config');
backupFile(configPath);

const i3Config = `# i3 Config - Hyprland-style
# Generated by transformation script

set $mod Mod4

# Font
font pango:JetBrains Mono 10

# Startup Applications
exec --no-startup-id dex --autostart --environment i3
exec --no-startup-id nm-applet
exec --no-startup-id /usr/lib/policykit-1-gnome/polkit-gnome-authentication-agent-1
exec --no-startup-id dunst
exec_always --no-startup-id ~/.fehbg || feh --bg-fill ~/Pictures/wallpapers/*
exec_always --no-startup-id ~/.config/polybar/launch.sh
exec_always --no-startup-id killall -q picom; sleep 0.3; picom -b
exec --no-startup-id /usr/local/bin/greenclip daemon || ~/.local/bin/greenclip daemon
exec --no-startup-id ~/.config/i3/scripts/idle_handler.sh
exec_always --no-startup-id ~/.config/i3/scripts/rainbow_borders.sh &

# Window Settings
floating_modifier $mod
tiling_drag modifier titlebar
focus_follows_mouse yes

# Gaps
gaps inner 5
gaps outer 10
smart_gaps on

# Borders
default_border pixel 3
default_floating_border pixel 3
hide_edge_borders smart

# Colors
set $bg     #1e1e2e
set $fg     #cdd6f4
set $accent #89b4fa
set $urgent #f38ba8

client.focused          $accent   $accent   $fg     $accent   $accent
client.focused_inactive $bg       $bg       $fg     $bg       $bg
client.unfocused        $bg       $bg       $fg     $bg       $bg
client.urgent           $urgent   $urgent   $fg     $urgent   $urgent

# Keybindings
bindsym $mod+Return exec kitty || gnome-terminal || alacritty
bindsym $mod+q kill
bindsym $mod+d exec rofi -show drun -show-icons
bindsym $mod+e exec thunar || nautilus || pcmanfm
bindsym $mod+b exec firefox || google-chrome
bindsym $mod+c exec code

bindsym $mod+f fullscreen toggle
bindsym $mod+space floating toggle
bindsym $mod+Shift+space focus mode_toggle

bindsym $mod+Left focus left
bindsym $mod+Down focus down
bindsym $mod+Up focus up
bindsym $mod+Right focus right

bindsym $mod+Shift+Left move left
bindsym $mod+Shift+Down move down
bindsym $mod+Shift+Up move up
bindsym $mod+Shift+Right move right

bindsym $mod+r mode "resize"
mode "resize" {
    bindsym Left resize shrink width 10 px or 10 ppt
    bindsym Down resize grow height 10 px or 10 ppt
    bindsym Up resize shrink height 10 px or 10 ppt
    bindsym Right resize grow width 10 px or 10 ppt
    bindsym Return mode "default"
    bindsym Escape mode "default"
}

# Workspaces
bindsym $mod+1 workspace number 1
bindsym $mod+2 workspace number 2
bindsym $mod+3 workspace number 3
bindsym $mod+4 workspace number 4
bindsym $mod+5 workspace number 5
bindsym $mod+6 workspace number 6
bindsym $mod+7 workspace number 7
bindsym $mod+8 workspace number 8
bindsym $mod+9 workspace number 9
bindsym $mod+0 workspace number 10

bindsym $mod+Shift+1 move container to workspace number 1
bindsym $mod+Shift+2 move container to workspace number 2
bindsym $mod+Shift+3 move container to workspace number 3
bindsym $mod+Shift+4 move container to workspace number 4
bindsym $mod+Shift+5 move container to workspace number 5
bindsym $mod+Shift+6 move container to workspace number 6
bindsym $mod+Shift+7 move container to workspace number 7
bindsym $mod+Shift+8 move container to workspace number 8
bindsym $mod+Shift+9 move container to workspace number 9
bindsym $mod+Shift+0 move container to workspace number 10

# Media & System Keys
bindsym Print exec ~/.config/i3/scripts/screenshot.sh full
bindsym $mod+Print exec ~/.config/i3/scripts/screenshot.sh full
bindsym $mod+Shift+s exec ~/.config/i3/scripts/screenshot.sh area
bindsym Shift+Print exec ~/.config/i3/scripts/screenshot.sh area

bindsym $mod+l exec ~/.config/i3/scripts/lock.sh
bindsym Control+Mod1+p exec ~/.config/i3/scripts/power_menu.sh
bindsym Control+Mod1+Delete exec i3-msg exit

bindsym XF86AudioRaiseVolume exec ~/.config/i3/scripts/volume.sh up
bindsym XF86AudioLowerVolume exec ~/.config/i3/scripts/volume.sh down
bindsym XF86AudioMute exec ~/.config/i3/scripts/volume.sh mute
bindsym XF86MonBrightnessUp exec ~/.config/i3/scripts/brightness.sh up
bindsym XF86MonBrightnessDown exec ~/.config/i3/scripts/brightness.sh down

bindsym XF86AudioPlay exec ~/.config/i3/scripts/media_ctrl.sh play-pause
bindsym XF86AudioNext exec ~/.config/i3/scripts/media_ctrl.sh next
bindsym XF86AudioPrev exec ~/.config/i3/scripts/media_ctrl.sh prev

# Custom Scripts
bindsym $mod+w exec ~/.config/i3/scripts/wallpaper_select.sh
bindsym $mod+Shift+w exec ~/.config/i3/scripts/wallpaper_effects.sh
bindsym Control+Mod1+w exec ~/.config/i3/scripts/wallpaper_random.sh
bindsym $mod+Shift+g exec ~/.config/i3/scripts/gamemode.sh
bindsym $mod+Shift+e exec ~/.config/i3/scripts/quick_settings.sh
bindsym $mod+Shift+h exec ~/.config/i3/scripts/keyhints.sh
bindsym $mod+Shift+m exec ~/.config/i3/scripts/rofibeats.sh
bindsym $mod+Shift+a exec ~/.config/i3/scripts/animations.sh
bindsym $mod+Mod1+o exec ~/.config/i3/scripts/change_blur.sh
bindsym $mod+Mod1+l exec ~/.config/i3/scripts/keyboard_layout.sh
bindsym $mod+Mod1+r exec ~/.config/i3/scripts/refresh.sh
bindsym $mod+Mod1+m exec ~/.config/i3/scripts/monitor_profiles.sh
bindsym $mod+Shift+c reload
bindsym $mod+Shift+r restart
`;

fs.writeFileSync(configPath, i3Config);
console.log('✓ Updated i3 config');

// ============================================================================
// 4. CREATE PICOM CONFIG
// ============================================================================
console.log('\n🎨 Creating picom config...');

const picomConfig = `# Picom Configuration - Hyprland-style
backend = "glx";
glx-no-stencil = true;
glx-copy-from-front = false;

shadow = true;
shadow-radius = 12;
shadow-offset-x = -12;
shadow-offset-y = -12;
shadow-opacity = 0.75;
shadow-exclude = ["class_g = 'slop'", "class_g = 'Polybar'"];

fading = true;
fade-in-step = 0.03;
fade-out-step = 0.03;
fade-delta = 10;

inactive-opacity = 0.95;
frame-opacity = 1.0;
active-opacity = 1.0;

corner-radius = 10;
rounded-corners-exclude = ["window_type = 'dock'", "window_type = 'desktop'"];

blur-method = "dual_kawase";
blur-strength = 5;
blur-background = true;
blur-background-frame = true;
blur-background-fixed = true;

# Animation settings (Requires picom-pijulius or picom-ft-labs)
# If using standard picom, comment lines below to avoid errors
animations = true;
animation-stiffness = 300;
animation-dampening = 20;
animation-window-mass = 0.5;
animation-delta = 10;
animation-clamping = true;
animation-for-open-window = "zoom";
animation-for-unmap-window = "slide-down";
`;

const picomDir = path.join(HOME, '.config/picom');
ensureDir(picomDir);
fs.writeFileSync(path.join(picomDir, 'picom.conf'), picomConfig);
console.log('✓ Created picom config');

// ============================================================================
// 5. CREATE POLYBAR CONFIG (Essential for the Rice)
// ============================================================================
console.log('\n📏 Creating Polybar config...');

const polyDir = path.join(HOME, '.config/polybar');
ensureDir(polyDir);

// 5.1 Launch Script
writeScript(path.join(polyDir, 'launch.sh'), `#!/bin/bash
killall -q polybar
while pgrep -u $UID -x polybar >/dev/null; do sleep 1; done
polybar -c ~/.config/polybar/config.ini main &
`);

// 5.2 Config.ini
const polyConfig = `[colors]
background = #1e1e2e
background-alt = #313244
foreground = #cdd6f4
primary = #89b4fa
secondary = #8BACD0
alert = #f38ba8
disabled = #707880

[bar/main]
width = 100%
height = 24pt
radius = 6
background = \${colors.background}
foreground = \${colors.foreground}
line-size = 3pt
border-size = 4pt
border-color = #00000000
padding-left = 1
padding-right = 1
module-margin = 1
separator = |
separator-foreground = \${colors.disabled}
font-0 = JetBrainsMono Nerd Font:size=10;2
modules-left = xworkspaces xwindow
modules-right = filesystem pulseaudio memory cpu wlan eth date battery
cursor-click = pointer
cursor-scroll = ns-resize
enable-ipc = true
tray-position = right

[module/xworkspaces]
type = internal/xworkspaces
label-active = %name%
label-active-background = \${colors.background-alt}
label-active-underline= \${colors.primary}
label-active-padding = 1
label-occupied = %name%
label-occupied-padding = 1
label-urgent = %name%
label-urgent-background = \${colors.alert}
label-urgent-padding = 1
label-empty = %name%
label-empty-foreground = \${colors.disabled}
label-empty-padding = 1

[module/xwindow]
type = internal/xwindow
label = %title:0:60:...%

[module/pulseaudio]
type = internal/pulseaudio
format-volume-prefix = "VOL "
format-volume-prefix-foreground = \${colors.primary}
format-volume = <label-volume>
label-volume = %percentage%%
label-muted = muted
label-muted-foreground = \${colors.disabled}

[module/memory]
type = internal/memory
interval = 2
format-prefix = "RAM "
format-prefix-foreground = \${colors.primary}
label = %percentage_used:2%%

[module/cpu]
type = internal/cpu
interval = 2
format-prefix = "CPU "
format-prefix-foreground = \${colors.primary}
label = %percentage:2%%

[module/wlan]
type = internal/network
interface-type = wireless
label-connected = %essid%
label-disconnected = disconnected

[module/date]
type = internal/date
interval = 1
date = %H:%M
date-alt = %Y-%m-%d %H:%M:%S
label = %date%
label-foreground = \${colors.primary}
`;
fs.writeFileSync(path.join(polyDir, 'config.ini'), polyConfig);
console.log('✓ Created polybar config');

// ============================================================================
// 6. CREATE DUNST CONFIG
// ============================================================================
console.log('\n🔔 Creating dunst config...');

const dunstConfig = `[global]
    width = 300
    height = 300
    origin = top-right
    offset = 10x50
    scale = 0
    notification_limit = 0
    progress_bar = true
    progress_bar_height = 10
    frame_width = 2
    frame_color = "#89b4fa"
    separator_color = frame
    font = JetBrains Mono 10
    corner_radius = 10
    background = "#1e1e2e"
    foreground = "#cdd6f4"
    timeout = 10
`;
const dunstDir = path.join(HOME, '.config/dunst');
ensureDir(dunstDir);
fs.writeFileSync(path.join(dunstDir, 'dunstrc'), dunstConfig);
console.log('✓ Created dunst config');

// ============================================================================
// 7. CREATE ROFI CONFIG
// ============================================================================
console.log('\n🎯 Creating rofi config...');

const rofiConfig = `configuration {
    modi: "drun,run,window";
    show-icons: true;
    font: "JetBrains Mono 12";
}
@theme "~/.config/rofi/theme.rasi"
`;

const rofiTheme = `* {
    background: #1e1e2eee;
    background-alt: #313244;
    foreground: #cdd6f4;
    selected: #89b4fa;
    background-colour: var(background);
    foreground-colour: var(foreground);
}
window {
    width: 600px;
    border-radius: 10px;
}
mainbox {
    padding: 20px;
}
inputbar {
    children: [ "prompt", "entry" ];
}
listview {
    lines: 8;
    columns: 1;
}
element {
    padding: 8px;
    border-radius: 8px;
    text-color: @foreground;
}
element selected.normal {
    background-color: var(selected);
    text-color: #1e1e2e;
}
`;

const rofiDir = path.join(HOME, '.config/rofi');
ensureDir(rofiDir);
fs.writeFileSync(path.join(rofiDir, 'config.rasi'), rofiConfig);
fs.writeFileSync(path.join(rofiDir, 'theme.rasi'), rofiTheme);
console.log('✓ Created rofi config');

// ============================================================================
// 8. CREATE README
// ============================================================================
const readme = `# i3 Hyprland-style Setup
... (Documentation generated by transform.js) ...
`;
fs.writeFileSync(path.join(CONFIG_DIR, 'README.md'), readme);

console.log('\n' + '='.repeat(70));
console.log('✨ Transformation Complete! ✨');
console.log('='.repeat(70));
console.log(`
📋 IMPORTANT NEXT STEPS:

1. Install Dependencies:
   sudo apt install i3 picom rofi dunst polybar kitty feh maim xclip \\
                    imagemagick playerctl brightnessctl pamixer fonts-jetbrains-mono

2. Make sure you use a Picom fork that supports animations (e.g., picom-pijulius).
   If you use standard picom, comment out 'animations' in ~/.config/picom/picom.conf

3. Reload i3: Super + Shift + R
`);
