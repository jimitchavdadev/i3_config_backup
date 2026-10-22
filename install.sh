#!/usr/bin/env bash
# ==============================================================================
#  💫 KoolDots i3 Desktop Environment Installer & Setup Script 💫
# ==============================================================================
# Replicates complete i3wm, Polybar, Wallust, Rofi, Picom, Dunst & dots ecosystem
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config"
WALLPAPER_DIR="$HOME/Pictures/wallpapers"

GREEN="\033[1;32m"
BLUE="\033[1;34m"
YELLOW="\033[1;33m"
CYAN="\033[1;36m"
RESET="\033[0m"

echo -e "${CYAN}====================================================${RESET}"
echo -e "${GREEN}   💫 Installing KoolDots i3wm Desktop Environment 💫 ${RESET}"
echo -e "${CYAN}====================================================${RESET}"

# 1. Install Dependencies
echo -e "\n${BLUE}==> [1/5] Checking and installing dependencies...${RESET}"
if command -v apt-get >/dev/null 2>&1; then
    echo -e "${YELLOW}Detected Debian/Ubuntu system...${RESET}"
    sudo apt-get update -y
    sudo apt-get install -y \
        i3-wm i3status polybar rofi dunst picom feh xdotool jq playerctl \
        autorandr brightnessctl pamixer pavucontrol network-manager \
        flameshot swappy libnotify-bin kitty btop cava fastfetch curl wget rsync
elif command -v pacman >/dev/null 2>&1; then
    echo -e "${YELLOW}Detected Arch Linux system...${RESET}"
    sudo pacman -Sy --needed --noconfirm \
        i3-wm polybar rofi dunst picom feh xdotool jq playerctl \
        autorandr brightnessctl pamixer pavucontrol networkmanager \
        flameshot swappy libnotify kitty btop cava fastfetch
fi

# 2. Install Wallust if missing
if ! command -v wallust >/dev/null 2>&1; then
    echo -e "${YELLOW}Wallust not detected. Installing via cargo/binary...${RESET}"
    if command -v cargo >/dev/null 2>&1; then
        cargo install wallust || true
    fi
fi

# 3. Deploy Dotfiles
echo -e "\n${BLUE}==> [2/5] Deploying configurations to ~/.config/...${RESET}"
mkdir -p "$CONFIG_DIR"
BACKUP_TS=$(date +%Y%m%d_%H%M%S)

for dir in i3 polybar rofi dunst picom wallust kitty autorandr swaync fastfetch cava btop; do
    if [ -d "$CONFIG_DIR/$dir" ]; then
        echo "Backing up existing ~/.config/$dir to ~/.config/${dir}_backup_${BACKUP_TS}"
        mv "$CONFIG_DIR/$dir" "$CONFIG_DIR/${dir}_backup_${BACKUP_TS}"
    fi
    if [ -d "$SCRIPT_DIR/.config/$dir" ]; then
        echo "Installing $dir configuration..."
        cp -r "$SCRIPT_DIR/.config/$dir" "$CONFIG_DIR/"
    fi
done

# 4. Deploy Wallpapers
echo -e "\n${BLUE}==> [3/5] Setting up wallpapers...${RESET}"
mkdir -p "$WALLPAPER_DIR"
if [ -d "$SCRIPT_DIR/wallpapers" ]; then
    cp -rn "$SCRIPT_DIR/wallpapers/"* "$WALLPAPER_DIR/" 2>/dev/null || true
fi

# 5. Fix Permissions
echo -e "\n${BLUE}==> [4/5] Setting executable permissions on scripts...${RESET}"
chmod -R +x "$CONFIG_DIR/i3/scripts" 2>/dev/null || true
chmod -R +x "$CONFIG_DIR/polybar/scripts" 2>/dev/null || true
chmod +x "$CONFIG_DIR/polybar/launch.sh" 2>/dev/null || true
chmod +x "$CONFIG_DIR/autorandr/postswitch" 2>/dev/null || true

# 6. Apply initial colors and wallpaper
echo -e "\n${BLUE}==> [5/5] Generating initial theme and color schemes...${RESET}"
DEFAULT_WALLPAPER="$WALLPAPER_DIR/wallpaper.jpeg"
if [ ! -f "$DEFAULT_WALLPAPER" ]; then
    DEFAULT_WALLPAPER=$(find "$WALLPAPER_DIR" -type f \( -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | head -n 1)
fi

if [ -f "$DEFAULT_WALLPAPER" ] && command -v wallust >/dev/null 2>&1; then
    wallust run -s "$DEFAULT_WALLPAPER" 2>/dev/null || true
fi

echo -e "\n${GREEN}====================================================${RESET}"
echo -e "${GREEN}   ✨ Installation Complete! ✨${RESET}"
echo -e "${CYAN}   Log in to i3 session or reload with: i3-msg reload${RESET}"
echo -e "${GREEN}====================================================${RESET}"
