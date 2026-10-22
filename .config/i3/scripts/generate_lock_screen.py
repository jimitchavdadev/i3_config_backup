#!/usr/bin/env python3
"""
Vagabond (Miyamoto Musashi) Philosophical Lock Screen Generator for i3
Minimalist Sumi-e ink wash aesthetic with a single bold philosophical quote
in the center, Zen Ensō brush circle, and 'ENTER THE REALM' invocation.
"""

import os
import re
import sys
import math
import subprocess
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance

BASE_CACHE_IMG = "/tmp/i3lock_blurred_base.png"
BASE_CACHE_META = "/tmp/i3lock_base.meta"
OUTPUT_LOCK_IMG = "/tmp/i3lock_aesthetic.png"

# Vagabond Classical Japanese Palette
BG_HEX = "0F0E10"
BG_COLOR = (15, 14, 16)             # Deep Sumi Charcoal Ink
WASHI_WHITE = (245, 239, 234)       # Handcrafted Washi / Rice Paper
INK_MUTED = (165, 158, 152)         # Washed ink gray
INK_FAINT = (115, 110, 106)         # Distant mist gray
VERMILION_RED = (184, 50, 39)       # Traditional Inkan / Cinnabar Red (#B83227)
SEAL_FILL = (184, 50, 39, 45)       # Translucent vermilion seal wash

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return None

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
    samurai_wall = os.path.expanduser("~/Pictures/wallpapers/samurai.jpg")
    if os.path.isfile(samurai_wall):
        return samurai_wall

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

def cover_and_sumie(src_img, tw, th):
    """Aspect-fill crop, desaturate to manga ink wash, and apply soft atmospheric blur."""
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
    
    gray = cropped.convert("L")
    enhancer = ImageEnhance.Contrast(gray)
    gray_contrasted = enhancer.enhance(1.25)
    
    blurred = gray_contrasted.filter(ImageFilter.GaussianBlur(radius=6))
    full = blurred.resize((tw, th), Image.Resampling.BILINEAR)
    return full.convert("RGBA")

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
        bg_m = cover_and_sumie(src_wall, mw, mh)
        canvas.paste(bg_m, (mx, my))

    # Deep sumi ink wash overlay
    ink_wash = Image.new("RGBA", (tw, th), (14, 13, 15, 140))
    canvas = Image.alpha_composite(canvas, ink_wash)

    base_rgb = canvas.convert("RGB")
    base_rgb.save(BASE_CACHE_IMG, "PNG", compress_level=1)
    
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

def draw_enso_circle(draw, cx, cy, r_base, scale):
    """Draws an authentic Zen Ensō brush circle framing the 95px i3lock ring."""
    segments = 120
    start_angle = -2.4
    end_angle = 3.3
    points_outer = []
    points_inner = []
    for i in range(segments + 1):
        t = i / float(segments)
        angle = start_angle + t * (end_angle - start_angle)
        pressure = math.sin(t * math.pi) ** 1.3
        thickness = (3.0 + 7.0 * pressure) * scale
        r_mod = r_base + math.sin(angle * 3.0) * (2.0 * scale)
        ro = r_mod + (thickness / 2.0)
        ri = r_mod - (thickness / 2.0)
        points_outer.append((cx + ro * math.cos(angle), cy + ro * math.sin(angle)))
        points_inner.append((cx + ri * math.cos(angle), cy + ri * math.sin(angle)))
    enso_poly = points_outer + list(reversed(points_inner))
    draw.polygon(enso_poly, fill=(*WASHI_WHITE, 160))

def draw_hanko_seal(draw, cx, cy, kanji, size):
    """Draws a traditional Japanese red vermilion artist seal (Hanko/Inkan)."""
    half = size / 2.0
    x1, y1 = cx - half, cy - half
    x2, y2 = cx + half, cy + half
    draw.rounded_rectangle([x1, y1, x2, y2], radius=4, fill=SEAL_FILL, outline=VERMILION_RED, width=2)
    font_serif_bold = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
    f_seal = ImageFont.truetype(font_serif_bold, int(size * 0.55))
    draw.text((cx, cy), kanji, font=f_seal, fill=VERMILION_RED, anchor="mm")

def generate_lock_image():
    monitors, tw, th = get_monitors()
    wall_path = get_wallpaper_path()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cache-base":
        build_blurred_base(monitors, tw, th, wall_path)
        print("Pre-cached base lock image successfully.")
        return

    base_img = get_or_create_base(monitors, tw, th, wall_path)
    canvas = base_img.copy()
    draw = ImageDraw.Draw(canvas)

    font_serif_bold = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
    font_jb_reg = os.path.expanduser("~/.local/share/fonts/JetBrainsMono/JetBrainsMonoNerdFont-Regular.ttf")

    now = datetime.now()
    time_raw = now.strftime("%H:%M")
    time_spaced = f"{time_raw[0]} {time_raw[1]} : {time_raw[3]} {time_raw[4]}"
    date_str = now.strftime("%B %d, %Y").upper()

    for m in monitors:
        mw, mh = m["width"], m["height"]
        mx, my = m["x"], m["y"]
        cx = mx + (mw // 2)
        cy = my + (mh // 2)
        scale = mh / 1080.0
        
        # Typographic scale
        time_size = int(88 * scale)
        kanji_header_size = int(22 * scale)
        date_size = int(14 * scale)
        quote_size = int(24 * scale)          # BIGGER & BOLDER single quote
        quote_author_size = int(13 * scale)
        realm_size = int(14 * scale)
        
        try:
            f_time = ImageFont.truetype(font_serif_bold, time_size)
            f_kanji_header = ImageFont.truetype(font_serif_bold, kanji_header_size)
            f_date = ImageFont.truetype(font_jb_reg, date_size)
            f_quote_bold = ImageFont.truetype(font_serif_bold, quote_size)
            f_quote_author = ImageFont.truetype(font_serif_bold, quote_author_size)
            f_realm = ImageFont.truetype(font_serif_bold, realm_size)
        except Exception:
            f_time = f_kanji_header = f_date = f_quote_bold = f_quote_author = f_realm = ImageFont.load_default()
        
        # ---------------------------------------------------------------------
        # 1. Zen Ensō Brush Circle (Framing the 95px i3lock ring)
        # ---------------------------------------------------------------------
        r_enso = int(115 * scale)
        draw_enso_circle(draw, cx, cy, r_enso, scale)
        
        # ---------------------------------------------------------------------
        # 2. Clock, Kanji & Date (Above the Ensō)
        # ---------------------------------------------------------------------
        clock_y = cy - r_enso - int(160 * scale)
        
        # Subtle calligraphic shadow
        draw.text((cx + 1, clock_y + 1), time_spaced, font=f_time, fill=(0, 0, 0, 160), anchor="mm")
        draw.text((cx, clock_y), time_spaced, font=f_time, fill=WASHI_WHITE, anchor="mm")
        
        # Kanji Title: 天 下 無 双 ("Invincible Under the Heavens")
        kanji_y = clock_y + int(54 * scale)
        draw_tracked_text(draw, cx, kanji_y, "天 下 無 双", f_kanji_header, WASHI_WHITE, spacing=int(14 * scale))
        
        # Date & Hanko Seal
        date_y = kanji_y + int(34 * scale)
        draw_tracked_text(draw, cx - int(24 * scale), date_y, date_str, f_date, INK_MUTED, spacing=int(3 * scale))
        hanko_x = cx + int(120 * scale)
        draw_hanko_seal(draw, hanko_x, date_y, "武蔵", int(26 * scale))
        
        # ---------------------------------------------------------------------
        # 3. The Single Quote (Bigger & Bolder, in the Middle of the Screen)
        # ---------------------------------------------------------------------
        quote_y = cy + r_enso + int(55 * scale)
        
        q1 = "“Preoccupied with a single leaf, you won't see the tree.”"
        q2 = "“Preoccupied with a single tree, you won't see the entire forest.”"
        
        # Depth shadow for the bold quote
        draw.text((cx + 1, quote_y + 1), q1, font=f_quote_bold, fill=(0, 0, 0, 180), anchor="mm")
        draw.text((cx, quote_y), q1, font=f_quote_bold, fill=WASHI_WHITE, anchor="mm")
        
        line2_y = quote_y + int(36 * scale)
        draw.text((cx + 1, line2_y + 1), q2, font=f_quote_bold, fill=(0, 0, 0, 180), anchor="mm")
        draw.text((cx, line2_y), q2, font=f_quote_bold, fill=WASHI_WHITE, anchor="mm")
        
        author_y = line2_y + int(36 * scale)
        author_text = "— 沢庵 宗彭  ·  TAKUAN SŌHŌ  ·  VAGABOND"
        draw.text((cx, author_y), author_text, font=f_quote_author, fill=VERMILION_RED, anchor="mm")
        
        # ---------------------------------------------------------------------
        # 4. "ENTER THE REALM"
        # ---------------------------------------------------------------------
        realm_y = author_y + int(46 * scale)
        draw_tracked_text(draw, cx, realm_y, "E N T E R   T H E   R E A L M", f_realm, WASHI_WHITE, spacing=int(6 * scale))
        
        # Subtle vermilion calligraphic divider mark
        div_y = realm_y + int(20 * scale)
        draw.line([(cx - int(30 * scale), div_y), (cx + int(30 * scale), div_y)], fill=(*VERMILION_RED, 140), width=1)

    canvas.save(OUTPUT_LOCK_IMG, "PNG", compress_level=1)
    print(f"BG_HEX={BG_HEX}")

if __name__ == "__main__":
    generate_lock_image()
