#!/usr/bin/env python3
"""
Aesthetic Multi-Monitor Lock Screen Generator for i3
Dynamically adapts to all connected monitors, scales/crops wallpaper
with aspect-fill, applies smooth glassmorphism blur, and composites
a modern Hyprlock-inspired clock, date, and user pill.
"""

import os
import re
import sys
import time
import subprocess
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont

BASE_CACHE_IMG = "/tmp/i3lock_blurred_base.png"
BASE_CACHE_META = "/tmp/i3lock_base.meta"
OUTPUT_LOCK_IMG = "/tmp/i3lock_aesthetic.png"

# Default theme colors (Wallust / Catppuccin inspired)
BG_HEX = "1A1313"
BG_COLOR = (26, 19, 19)
FG_COLOR = (218, 245, 253)
PRIMARY_COLOR = (182, 131, 105)
SECONDARY_COLOR = (112, 170, 188)
MUTED_COLOR = (136, 163, 171)

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return None

def load_theme_colors():
    global BG_HEX, BG_COLOR, FG_COLOR, PRIMARY_COLOR, SECONDARY_COLOR, MUTED_COLOR
    colors_file = os.path.expanduser("~/.config/polybar/colors.ini")
    if os.path.isfile(colors_file):
        try:
            with open(colors_file) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("background ="):
                        raw = line.split("=")[1].strip().lstrip("#")
                        c = hex_to_rgb(raw)
                        if c:
                            BG_COLOR = c
                            BG_HEX = raw
                    elif line.startswith("foreground ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: FG_COLOR = c
                    elif line.startswith("primary ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: PRIMARY_COLOR = c
                    elif line.startswith("secondary ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: SECONDARY_COLOR = c
                    elif line.startswith("disabled ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: MUTED_COLOR = c
        except Exception:
            pass

def get_monitors():
    monitors = []
    total_w = 0
    total_h = 0
    try:
        output = subprocess.check_output(["xrandr", "--query"], stderr=subprocess.DEVNULL).decode("utf-8")
        for line in output.splitlines():
            m = re.match(r'^([a-zA-Z0-9_-]+)\s+connected\s+(primary\s+)?([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+)', line)
            if m:
                name = m.group(1)
                is_primary = bool(m.group(2))
                w = int(m.group(3))
                h = int(m.group(4))
                ox = int(m.group(5))
                oy = int(m.group(6))
                monitors.append({
                    "name": name,
                    "primary": is_primary,
                    "width": w,
                    "height": h,
                    "x": ox,
                    "y": oy
                })
                total_w = max(total_w, ox + w)
                total_h = max(total_h, oy + h)
    except Exception:
        pass
    if not monitors:
        monitors.append({"name": "default", "primary": True, "width": 1920, "height": 1080, "x": 0, "y": 0})
        total_w, total_h = 1920, 1080
    return monitors, total_w, total_h

def get_wallpaper_path():
    curr_wall_file = os.path.expanduser("~/.config/i3/wallpaper_effects/.wallpaper_current")
    if os.path.isfile(curr_wall_file):
        try:
            with open(curr_wall_file) as f:
                p = f.read().strip()
                if os.path.isfile(p):
                    return p
        except Exception:
            pass
    fallback = os.path.expanduser("~/Pictures/wallpapers/Techno-Geek.png")
    if os.path.isfile(fallback):
        return fallback
    return None

def cover_and_blur(src_img, tw, th):
    """Aspect fill (cover) crop and smooth Gaussian blur."""
    iw, ih = src_img.size
    dw = max(1, tw // 3)
    dh = max(1, th // 3)
    scale = max(dw / iw, dh / ih)
    dnw = int(iw * scale + 0.5)
    dnh = int(ih * scale + 0.5)
    
    small = src_img.resize((dnw, dnh), Image.Resampling.BILINEAR)
    left = (dnw - dw) // 2
    top = (dnh - dh) // 2
    cropped = small.crop((left, top, left + dw, top + dh))
    
    blurred = cropped.filter(ImageFilter.GaussianBlur(radius=8))
    full = blurred.resize((tw, th), Image.Resampling.BILINEAR)
    return full

def build_blurred_base(monitors, tw, th, wall_path):
    canvas = Image.new("RGBA", (tw, th), (*BG_COLOR, 255))
    try:
        if wall_path and os.path.isfile(wall_path):
            src_wall = Image.open(wall_path).convert("RGBA")
        else:
            src_wall = Image.new("RGBA", (1920, 1080), (*BG_COLOR, 255))
    except Exception:
        src_wall = Image.new("RGBA", (1920, 1080), (*BG_COLOR, 255))

    for m in monitors:
        mw, mh = m["width"], m["height"]
        mx, my = m["x"], m["y"]
        bg_m = cover_and_blur(src_wall, mw, mh)
        canvas.paste(bg_m, (mx, my))

    # Apply elegant dark overlay for contrast & readability
    overlay = Image.new("RGBA", (tw, th), (0, 0, 0, 105))
    canvas = Image.alpha_composite(canvas, overlay)
    
    base_rgb = canvas.convert("RGB")
    base_rgb.save(BASE_CACHE_IMG, "PNG", compress_level=1)
    
    # Save cache metadata
    mtime = str(os.path.getmtime(wall_path)) if wall_path and os.path.isfile(wall_path) else "0"
    mon_key = ";".join(f"{m['name']}:{m['width']}x{m['height']}+{m['x']}+{m['y']}" for m in monitors)
    try:
        with open(BASE_CACHE_META, "w") as f:
            f.write(f"{wall_path}\n{mtime}\n{mon_key}\n")
    except Exception:
        pass
    
    return base_rgb

def get_or_create_base(monitors, tw, th, wall_path):
    mtime = str(os.path.getmtime(wall_path)) if wall_path and os.path.isfile(wall_path) else "0"
    mon_key = ";".join(f"{m['name']}:{m['width']}x{m['height']}+{m['x']}+{m['y']}" for m in monitors)
    
    if os.path.isfile(BASE_CACHE_IMG) and os.path.isfile(BASE_CACHE_META):
        try:
            with open(BASE_CACHE_META) as f:
                lines = [l.strip() for l in f.readlines()]
            if len(lines) >= 3 and lines[0] == str(wall_path) and lines[1] == mtime and lines[2] == mon_key:
                return Image.open(BASE_CACHE_IMG).convert("RGB")
        except Exception:
            pass
            
    return build_blurred_base(monitors, tw, th, wall_path)

def generate_lock_image():
    load_theme_colors()
    monitors, tw, th = get_monitors()
    wall_path = get_wallpaper_path()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cache-base":
        build_blurred_base(monitors, tw, th, wall_path)
        print("Pre-cached base lock image successfully.")
        return

    base_img = get_or_create_base(monitors, tw, th, wall_path)
    canvas = base_img.copy()
    draw = ImageDraw.Draw(canvas)

    font_bold_path = os.path.expanduser("~/.local/share/fonts/JetBrainsMono/JetBrainsMonoNerdFont-Bold.ttf")
    font_reg_path = os.path.expanduser("~/.local/share/fonts/JetBrainsMono/JetBrainsMonoNerdFont-Regular.ttf")

    now = datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%A, %d %B")
    user_name = os.environ.get("USER", "jimitchavda")

    for m in monitors:
        mw, mh = m["width"], m["height"]
        mx, my = m["x"], m["y"]
        cx = mx + (mw // 2)
        cy = my + (mh // 2)
        scale = mh / 1080.0
        
        time_size = int(82 * scale)
        date_size = int(22 * scale)
        sub_size = int(14 * scale)
        badge_size = int(14 * scale)
        
        try:
            f_time = ImageFont.truetype(font_bold_path, time_size)
            f_date = ImageFont.truetype(font_reg_path, date_size)
            f_sub = ImageFont.truetype(font_reg_path, sub_size)
            f_badge = ImageFont.truetype(font_bold_path, badge_size)
        except Exception:
            f_time = f_date = f_sub = f_badge = ImageFont.load_default()
        
        # Clock
        tb = draw.textbbox((0, 0), time_str, font=f_time)
        tw_text = tb[2] - tb[0]
        th_text = tb[3] - tb[1]
        time_y = cy - int(245 * scale)
        time_x = cx - (tw_text // 2)
        draw.text((time_x, time_y), time_str, font=f_time, fill=FG_COLOR)
        
        # Date
        db = draw.textbbox((0, 0), date_str, font=f_date)
        dw_text = db[2] - db[0]
        date_y = time_y + th_text + int(14 * scale)
        date_x = cx - (dw_text // 2)
        draw.text((date_x, date_y), date_str, font=f_date, fill=SECONDARY_COLOR)
        
        # User Pill Badge
        badge_text = f"  {user_name}"
        bb = draw.textbbox((0, 0), badge_text, font=f_badge)
        bw_text = bb[2] - bb[0]
        bh_text = bb[3] - bb[1]
        pill_pad_x = int(18 * scale)
        pill_pad_y = int(8 * scale)
        pill_w = bw_text + (pill_pad_x * 2)
        pill_h = bh_text + (pill_pad_y * 2)
        pill_x1 = cx - (pill_w // 2)
        pill_y1 = date_y + int(38 * scale)
        pill_x2 = pill_x1 + pill_w
        pill_y2 = pill_y1 + pill_h
        
        draw.rounded_rectangle(
            [pill_x1, pill_y1, pill_x2, pill_y2],
            radius=int(14 * scale),
            fill=BG_COLOR,
            outline=PRIMARY_COLOR,
            width=1
        )
        badge_x = cx - (bw_text // 2)
        badge_y = pill_y1 + pill_pad_y - 1
        draw.text((badge_x, badge_y), badge_text, font=f_badge, fill=FG_COLOR)
        
        # Unlock instruction placed cleanly below i3lock's 190px ring (center is cy)
        sub_text = "󰌾  Type password to unlock"
        sb = draw.textbbox((0, 0), sub_text, font=f_sub)
        sw_text = sb[2] - sb[0]
        sub_y = cy + int(125 * scale)
        sub_x = cx - (sw_text // 2)
        draw.text((sub_x, sub_y), sub_text, font=f_sub, fill=MUTED_COLOR)

    canvas.save(OUTPUT_LOCK_IMG, "PNG", compress_level=1)
    # Output the background hex color for i3lock -c
    print(f"BG_HEX={BG_HEX}")

if __name__ == "__main__":
    generate_lock_image()
