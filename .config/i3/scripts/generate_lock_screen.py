#!/usr/bin/env python3
"""
Blade Runner 2049 Multi-Monitor Screen Locker for i3
Philosophical, futuristic, and atmospheric design inspired by Denis Villeneuve & Roger Deakins.
Features Wallace Corp typography, Baseline Test echoes, warm amber atmospheric haze,
tracked lettering, and an ultra-delicate circular reticle framing i3lock's indicator.
"""

import os
import re
import sys
import subprocess
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont

BASE_CACHE_IMG = "/tmp/i3lock_blurred_base.png"
BASE_CACHE_META = "/tmp/i3lock_base.meta"
OUTPUT_LOCK_IMG = "/tmp/i3lock_aesthetic.png"

# Blade Runner 2049 Palette (Roger Deakins Cinematic Grade)
BG_HEX = "120E10"
BG_COLOR = (18, 14, 16)             # Deep obsidian / umber shadow
IVORY_WHITE = (245, 238, 224)       # Warm ivory / cream white
AMBER_GOLD = (235, 150, 70)         # Wallace Corp Golden Amber
MUTED_AMBER = (180, 115, 65)        # Weathered sepia / desert bronze
MIST_SLATE = (165, 178, 185)        # Atmospheric fog / rain slate
HAZE_TINT = (35, 20, 15)            # Warm ambient cinematic haze

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return None

def load_theme_colors():
    global BG_HEX, BG_COLOR, IVORY_WHITE, AMBER_GOLD, MUTED_AMBER, MIST_SLATE
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
                        if c: IVORY_WHITE = c
                    elif line.startswith("color13 =") or line.startswith("primary ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: AMBER_GOLD = c
                    elif line.startswith("secondary =") or line.startswith("disabled ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: MIST_SLATE = c
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
    """Aspect-fill (cover) crop and smooth Gaussian blur."""
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

    # Roger Deakins Atmospheric Color Grade:
    # 1. Warm amber/sepia haze wash (Wallace Corp / desert ruin ambient glow)
    amber_haze = Image.new("RGBA", (tw, th), (*HAZE_TINT, 75))
    canvas = Image.alpha_composite(canvas, amber_haze)

    # 2. Cinematic deep vignette
    vignette = Image.new("RGBA", (tw, th), (10, 8, 10, 125))
    canvas = Image.alpha_composite(canvas, vignette)

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

def draw_tracked_text(draw, cx, cy, text, font, fill, spacing=6):
    """Draw text with tracked letter spacing centered at (cx, cy)."""
    chars = list(text)
    boxes = [draw.textbbox((0, 0), ch, font=font) for ch in chars]
    widths = [b[2] - b[0] for b in boxes]
    total_w = sum(widths) + (len(chars) - 1) * spacing
    cur_x = cx - (total_w / 2)
    for i, ch in enumerate(chars):
        draw.text((cur_x, cy), ch, font=font, fill=fill, anchor="lm")
        cur_x += widths[i] + spacing

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
    time_raw = now.strftime("%H:%M")
    # Spaced clock: 1 4 : 4 5
    time_spaced = f"{time_raw[0]} {time_raw[1]} : {time_raw[3]} {time_raw[4]}"
    date_str = now.strftime("%B %d, %Y  ·  EARTH STANDARD").upper()
    user_name = os.environ.get("USER", "jimitchavda").upper()

    for m in monitors:
        mw, mh = m["width"], m["height"]
        mx, my = m["x"], m["y"]
        cx = mx + (mw // 2)
        cy = my + (mh // 2)
        scale = mh / 1080.0
        
        # Proportional typographic scale
        time_size = int(88 * scale)
        date_size = int(14 * scale)
        badge_size = int(12 * scale)
        hud_size = int(11 * scale)
        corner_size = int(10 * scale)
        
        try:
            f_time = ImageFont.truetype(font_bold_path, time_size)
            f_date = ImageFont.truetype(font_reg_path, date_size)
            f_badge = ImageFont.truetype(font_reg_path, badge_size)
            f_hud = ImageFont.truetype(font_reg_path, hud_size)
            f_corner = ImageFont.truetype(font_reg_path, corner_size)
        except Exception:
            f_time = f_date = f_badge = f_hud = f_corner = ImageFont.load_default()
        
        # ---------------------------------------------------------------------
        # 1. Minimalist Blade Runner Reticle around i3lock ring (radius 95px)
        # ---------------------------------------------------------------------
        r_reticle = int(114 * scale)
        
        # Delicate hairline ring
        draw.ellipse(
            [cx - r_reticle, cy - r_reticle, cx + r_reticle, cy + r_reticle],
            outline=(*AMBER_GOLD, 100),
            width=1
        )
        
        # Cardinal crosshair tick marks
        tick_len = int(8 * scale)
        draw.line([(cx - r_reticle - tick_len, cy), (cx - r_reticle + tick_len, cy)], fill=(*AMBER_GOLD, 180), width=1)
        draw.line([(cx + r_reticle - tick_len, cy), (cx + r_reticle + tick_len, cy)], fill=(*AMBER_GOLD, 180), width=1)
        draw.line([(cx, cy - r_reticle - tick_len), (cx, cy - r_reticle + tick_len)], fill=(*AMBER_GOLD, 180), width=1)
        draw.line([(cx, cy + r_reticle - tick_len), (cx, cy + r_reticle + tick_len)], fill=(*AMBER_GOLD, 180), width=1)
        
        # Baseline markers
        draw_tracked_text(draw, cx, cy - r_reticle - int(16 * scale), "·  B A S E L I N E  ·", f_hud, AMBER_GOLD, spacing=int(4 * scale))
        draw_tracked_text(draw, cx, cy + r_reticle + int(16 * scale), "I N T E R L I N K E D", f_hud, (*AMBER_GOLD, 160), spacing=int(4 * scale))
        
        # ---------------------------------------------------------------------
        # 2. Clock & Date (Above the Reticle with guaranteed clearance)
        # ---------------------------------------------------------------------
        clock_y = cy - r_reticle - int(165 * scale)
        
        # Soft ambient warm glow behind clock
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
            draw.text((cx + ox, clock_y + oy), time_spaced, font=f_time, fill=(*AMBER_GOLD, 50), anchor="mm")
        # Crisp ivory core
        draw.text((cx, clock_y), time_spaced, font=f_time, fill=IVORY_WHITE, anchor="mm")
        
        # Minimalist hairline divider with center dot
        div_w = int(140 * scale)
        div_y = clock_y + int(48 * scale)
        draw.line([(cx - div_w, div_y), (cx - 10, div_y)], fill=(*AMBER_GOLD, 100), width=1)
        draw.ellipse([cx - 2, div_y - 2, cx + 2, div_y + 2], fill=AMBER_GOLD)
        draw.line([(cx + 10, div_y), (cx + div_w, div_y)], fill=(*AMBER_GOLD, 100), width=1)
        
        # Date
        date_y = div_y + int(18 * scale)
        draw_tracked_text(draw, cx, date_y, date_str, f_date, (*AMBER_GOLD, 210), spacing=int(2 * scale))
        
        # Replicant / Identity line
        id_y = date_y + int(32 * scale)
        id_text = f"NEXUS-9  //  SERIAL: KD6-3.7  ·  {user_name}"
        draw_tracked_text(draw, cx, id_y, id_text, f_badge, (*MIST_SLATE, 190), spacing=int(2 * scale))
        
        # ---------------------------------------------------------------------
        # 3. Prompt (Below the Reticle)
        # ---------------------------------------------------------------------
        prompt_y = cy + r_reticle + int(54 * scale)
        prompt_text = "CELLS INTERLINKED  ·  ENTER KEY TO CONFIRM BASELINE"
        draw_tracked_text(draw, cx, prompt_y, prompt_text, f_hud, (*IVORY_WHITE, 180), spacing=int(3 * scale))
        
        prompt_sub = ">> [  .  .  .  .  .  .  .  .  ]"
        draw.text((cx, prompt_y + int(22 * scale)), prompt_sub, font=f_hud, fill=(*AMBER_GOLD, 140), anchor="mm")
        
        # ---------------------------------------------------------------------
        # 4. Corner Telemetry (Literary, Philosophical, Wallace Corp)
        # ---------------------------------------------------------------------
        pad_x = int(46 * scale)
        pad_y = int(38 * scale)
        
        # Top-Left: Wallace Corp Header
        draw.text((mx + pad_x, my + pad_y), "WALLACE CORP.  //  MEMORY ARCHIVE", font=f_corner, fill=(*AMBER_GOLD, 190))
        draw.text((mx + pad_x, my + pad_y + int(16 * scale)), f"SECTOR 04  ·  UNIT: {m['name']}  ·  {mw}x{mh}", font=f_corner, fill=(*MIST_SLATE, 130))
        
        # Top-Right: Baseline Status
        draw.text((mx + mw - pad_x, my + pad_y), "POST-BLACKOUT RECORD  ·  2049", font=f_corner, fill=(*AMBER_GOLD, 190), anchor="ra")
        draw.text((mx + mw - pad_x, my + pad_y + int(16 * scale)), "STATUS: CONSTANT", font=f_corner, fill=(*MIST_SLATE, 130), anchor="ra")
        
        # Bottom-Left: Iconic Blade Runner Philosophy
        draw.text((mx + pad_x, my + mh - pad_y - int(16 * scale)), "“All those moments will be lost in time, like tears in rain.”", font=f_corner, fill=(*MIST_SLATE, 120))
        draw.text((mx + pad_x, my + mh - pad_y), "ROY BATTY  ·  2019  ·  TYRELL ARCHIVES", font=f_corner, fill=(*MUTED_AMBER, 110))
        
        # Bottom-Right: Baseline Prompt Echo
        draw.text((mx + mw - pad_x, my + mh - pad_y - int(16 * scale)), "“A system of cells interlinked within cells...”", font=f_corner, fill=(*MIST_SLATE, 120), anchor="ra")
        draw.text((mx + mw - pad_x, my + mh - pad_y), "[ AWAITING PASSPHRASE ]", font=f_corner, fill=(*AMBER_GOLD, 170), anchor="ra")

    canvas.save(OUTPUT_LOCK_IMG, "PNG", compress_level=1)
    print(f"BG_HEX={BG_HEX}")

if __name__ == "__main__":
    generate_lock_image()
