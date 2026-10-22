# 💫 KoolDots i3 Desktop Environment 💫

An ultra-refined, fully customized **i3wm** desktop environment on X11, meticulously replicated from the modern Wayland [dots](https://github.com/jimitchavda/dots) ecosystem with dynamic color palette generation, smooth animations, multi-monitor display auto-negotiation, and modular Polybar status architecture.

---

## 🌟 Key Highlights & Features

- **Dynamic Color Harmony ([Wallust](https://codeberg.org/explosion-mental/wallust)):** Every wallpaper change automatically extracts dominant hues and regenerates harmonious themes for i3 borders, Polybar, Dunst, Rofi, Kitty, and Cava on the fly.
- **Centered Workspaces with Geometry Anchoring:** Polybar workspace indicators stay locked dead-center at all times, flanked by live weather on the left and date/time on the right.
- **Windows-Style Background Process Drawer:** Background system tray applications (Livepatch, Photonix, Nextcloud, etc.) are tucked away behind a sleek collapsible chevron button (`󰅃`), keeping the taskbar uncluttered.
- **Expandable Hover System Drawer:** Hovering over the top-right metrics area smoothly expands detailed CPU, RAM, and network speeds via native Polybar IPC hooks.
- **Per-Display Workspace Cycling:** `$mod+Tab` and `$mod+grave` cycle strictly through workspaces assigned to the currently focused display, eliminating disruptive cross-monitor jumping.
- **Smart Display Hotplug & Orphan Rescue ([Autorandr](https://github.com/phillipberndt/autorandr)):** Connecting or disconnecting external monitors automatically detects native display modes and rescues any stranded workspaces without restarting or crashing Polybar.
- **Full Window Overview (`Super + a`):** Fast, searchable Rofi overview showing all open windows with application icons and workspace badges across all monitors.
- **Modern Notification Integration ([Dunst](https://dunst-project.org/)):** Left-clicking notifications immediately navigates to and focuses the corresponding application window and workspace.

---

## 📦 Included Tool Configurations

| Tool | Config Location | Description |
| :--- | :--- | :--- |
| **i3wm** | `.config/i3/` | Tiling window manager config, window rules, keybindings & utility scripts |
| **Polybar** | `.config/polybar/` | Custom status bar with IPC drawers, weather, battery, network, audio & controls |
| **Rofi** | `.config/rofi/` | App launcher, window switcher, clipboard manager, emoji picker, calc & theme selector |
| **Dunst** | `.config/dunst/` | Notification daemon styled with Wallust dynamic templates and interactive actions |
| **Picom** | `.config/picom/` | Compositor with dual-kawase blur, rounded corners, shadows, and smooth transitions |
| **Wallust** | `.config/wallust/` | Fast palette generator with custom templates for all installed tools |
| **Kitty** | `.config/kitty/` | GPU-accelerated terminal with font ligatures and Wallust color syncing |
| **Autorandr** | `.config/autorandr/` | Multi-monitor profile management with automated udev hooks and workspace migration |
| **SwayNC Assets** | `.config/swaync/` | High-DPI status icons and notification imagery |
| **Fastfetch** | `.config/fastfetch/` | Modern system information tool formatted for clean terminal display |
| **Cava** | `.config/cava/` | Audio visualizer with Wallust template integration |
| **Btop** | `.config/btop/` | High-fidelity interactive terminal system monitor |

---

## ⌨️ Essential Keybindings

### 🚀 Core Applications
- `Super + Return` — Open Kitty Terminal
- `Super + Shift + Return` — Dropdown Scratchpad Terminal
- `Super + d` — Application Launcher (Rofi)
- `Super + a` — Windows & Workspaces Overview (Rofi)
- `Super + b` — Google Chrome (`--new-window`)
- `Super + Shift + b` — Google Chrome Incognito
- `Super + e` — File Manager (Thunar)
- `Super + c` — Code Editor (VS Code)
- `Ctrl + Shift + Esc` — System Monitor (GNOME System Monitor / Btop)

### 🪟 Window Management
- `Super + q` — Close Focused Window
- `Super + Shift + q` — Force Kill Active Process
- `Super + f` — Fullscreen Toggle
- `Super + Space` — Toggle Floating Mode
- `Super + h/j/k/l` or `Arrows` — Move Focus (Left / Down / Up / Right)
- `Super + Shift + h/j/k/l` — Move Window (Left / Down / Up / Right)
- `Super + s` — Stacking Layout
- `Super + w` — Tabbed Layout
- `Super + g` — Split Layout Toggle

### 🧭 Workspace Navigation
- `Super + 1..0` — Switch to Workspace 1 through 10
- `Super + Shift + 1..0` — Move Window to Workspace 1 through 10
- `Super + Tab` — Cycle to Next Workspace on Current Monitor
- `Super + Shift + Tab` — Cycle to Previous Workspace on Current Monitor
- `Super + ` ` ` (Grave) — Cycle to Previous Workspace on Current Monitor
- `Super + Shift + ` ` ` — Cycle to Next Workspace on Current Monitor

### 🎨 Ricing & Quick Tools
- `Super + w` (Wallpaper Menu) — Select Wallpaper with visual preview
- `Super + Shift + w` — Apply ImageMagick Wallpaper Effects
- `Super + Alt + v` — Clipboard History (Greenclip)
- `Super + Alt + e` — Searchable Emoji Picker
- `Super + Alt + c` — Quick Calculator
- `Super + Shift + e` — Quick Settings Center
- `Super + Shift + s` — Interactive Area Screenshot (Swappy / Flameshot)
- `Super + l` or `Ctrl + Alt + l` — Lock Screen with Blur
- `Super + Alt + r` — Refresh Desktop (Reload Polybar, Picom & i3)

---

## 🚀 Reproduction & Quick Installation

### 1. Clone the Repository
```bash
git clone https://github.com/jimitchavda/i3_config_backup.git ~/i3_config_backup
cd ~/i3_config_backup
```

### 2. Run the Automated Installer
```bash
chmod +x install.sh
./install.sh
```

The script will:
1. Detect your package manager (`apt` or `pacman`) and install all necessary dependencies.
2. Back up any existing `~/.config/` configurations with timestamped folders.
3. Deploy `.config/` components and sample wallpapers.
4. Set execution permissions on all automation scripts.
5. Generate the initial color palette using `wallust` and apply the wallpaper with `feh`.

### 3. Log In to i3
Select **i3** at your display manager (GDM / LightDM / SDDM) login prompt, or if already running i3, reload with:
```bash
i3-msg reload
```

---

## 🖥️ Multi-Monitor Setup

Display profiles are handled dynamically by `autorandr` and `display_manage.sh`:
- **Auto Detect:** Automatically configures dual monitors horizontally side-by-side when plugged in.
- **Laptop Only:** `~/.config/i3/scripts/display_manage.sh laptop`
- **Dual Screen:** `~/.config/i3/scripts/display_manage.sh dual`
- When displays change, orphaned workspaces are automatically rescued to the primary display.

---

## 📜 License
GPL-3.0 License. Custom ricing, scripts, and layout enhancements inspired by the KoolDots ecosystem.
