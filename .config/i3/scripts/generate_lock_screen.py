#!/usr/bin/env python3
"""
Vagabond (Miyamoto Musashi) Philosophical Lock Screen Generator for i3
Inspired by Takehiko Inoue's legendary manga 'Vagabond'.
Features Sumi-e ink wash aesthetics, authentic Zen Ensō brush circle framing the
unlock indicator, traditional Japanese calligraphy (Noto Serif CJK), vermilion Hanko seal,
and profound philosophical quotes from Musashi and Takuan Sōhō.
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
INK_MUTED = (160, 154, 148)         # Washed ink gray
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
    # Prioritize user's samurai wallpaper for the authentic Vagabond atmosphere
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
    
    # Atmospheric monochrome sumi-e ink
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

def draw_enso_circle(draw, cx, cy, r_base, scale):
    """Draws an authentic Zen Ensō brush circle framing the 95px i3lock ring."""
    segments = 120
    start_angle = -2.4  # radians (~-137 deg)
    end_angle = 3.3     # radians (~190 deg, leaves Zen open gap)
    
    points_outer = []
    points_inner = []
    
    for i in range(segments + 1):
        t = i / float(segments)
        angle = start_angle + t * (end_angle - start_angle)
        
        # Brush pressure dynamics: swells gracefully and tapers toward tail
        pressure = math.sin(t * math.pi) ** 1.3
        thickness = (3.0 + 7.0 * pressure) * scale
        r_mod = r_base + math.sin(angle * 3.0) * (2.0 * scale)
        
        ro = r_mod + (thickness / 2.0)
        ri = r_mod - (thickness / 2.0)
        
        xo = cx + ro * math.cos(angle)
        yo = cy + ro * math.sin(angle)
        xi = cx + ri * math.cos(angle)
        yi = cy + ri * math.sin(angle)
        
        points_outer.append((xo, yo))
        points_inner.append((xi, yi))
    
    enso_poly = points_outer + list(reversed(points_inner))
    draw.polygon(enso_poly, fill=(*WASHI_WHITE, 160))

def draw_hanko_seal(draw, cx, cy, kanji, size):
    """Draws a traditional Japanese vermilion artist seal (Hanko/Inkan)."""
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
    font_serif_reg = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"
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
        time_size = int(86 * scale)
        kanji_header_size = int(22 * scale)
        date_size = int(14 * scale)
        quote_size = int(13 * scale)
        quote_author_size = int(11 * scale)
        corner_size = int(11 * scale)
        corner_sub_size = int(10 * scale)
        
        try:
            f_time = ImageFont.truetype(font_serif_bold, time_size)
            f_kanji_header = ImageFont.truetype(font_serif_bold, kanji_header_size)
            f_date = ImageFont.truetype(font_jb_reg, date_size)
            f_quote = ImageFont.truetype(font_serif_reg, quote_size)
            f_quote_author = ImageFont.truetype(font_serif_bold, quote_author_size)
            f_corner = ImageFont.truetype(font_serif_reg, corner_size)
            f_corner_sub = ImageFont.truetype(font_serif_bold, corner_sub_size)
            f_enso_label = ImageFont.truetype(font_serif_bold, int(11 * scale))
        except Exception:
            f_time = f_kanji_header = f_date = f_quote = f_quote_author = f_corner = f_corner_sub = f_enso_label = ImageFont.load_default()
        
        # ---------------------------------------------------------------------
        # 1. Zen Ensō Brush Circle (Framing the 95px i3lock ring)
        # ---------------------------------------------------------------------
        r_enso = int(115 * scale)
        draw_enso_circle(draw, cx, cy, r_enso, scale)
        
        # Ensō Zen Label (Above & Below the circle)
        draw_tracked_text(draw, cx, cy - r_enso - int(18 * scale), "無  限", f_enso_label, INK_MUTED, spacing=int(6 * scale))
        draw_tracked_text(draw, cx, cy + r_enso + int(18 * scale), "円  相", f_enso_label, (*INK_MUTED, 180), spacing=int(6 * scale))
        
        # ---------------------------------------------------------------------
        # 2. Clock, Kanji & Date (Above the Ensō with serene spacing)
        # ---------------------------------------------------------------------
        clock_y = cy - r_enso - int(170 * scale)
        
        # Subtle calligraphic shadow
        draw.text((cx + 1, clock_y + 1), time_spaced, font=f_time, fill=(0, 0, 0, 160), anchor="mm")
        # Crisp Washi White
        draw.text((cx, clock_y), time_spaced, font=f_time, fill=WASHI_WHITE, anchor="mm")
        
        # Kanji Title: 天 下 無 双 ("Invincible Under the Heavens")
        kanji_y = clock_y + int(52 * scale)
        draw_tracked_text(draw, cx, kanji_y, "天 下 無 双", f_kanji_header, WASHI_WHITE, spacing=int(14 * scale))
        
        # Date & Hanko Seal Row
        date_y = kanji_y + int(34 * scale)
        draw_tracked_text(draw, cx - int(24 * scale), date_y, date_str, f_date, INK_MUTED, spacing=int(3 * scale))
        
        # Red Vermilion Hanko Stamp: [ 武蔵 ] (Musashi)
        hanko_x = cx + int(120 * scale)
        draw_hanko_seal(draw, hanko_x, date_y, "武蔵", int(26 * scale))
        
        # ---------------------------------------------------------------------
        # 3. Philosophical Inscription (Below the Ensō)
        # ---------------------------------------------------------------------
        quote_y = cy + r_enso + int(56 * scale)
        
        q1 = "“Preoccupied with a single leaf, you won't see the tree.”"
        q2 = "“Preoccupied with a single tree, you won't see the entire forest.”"
        draw.text((cx, quote_y), q1, font=f_quote, fill=WASHI_WHITE, anchor="mm")
        draw.text((cx, quote_y + int(22 * scale)), q2, font=f_quote, fill=WASHI_WHITE, anchor="mm")
        
        author_text = "— 沢庵 宗彭  ·  TAKUAN SŌHŌ  ·  VAGABOND"
        draw.text((cx, quote_y + int(46 * scale)), author_text, font=f_quote_author, fill=VERMILION_RED, anchor="mm")
        
        # Unlock instruction
        unlock_y = quote_y + int(76 * scale)
        draw_tracked_text(draw, cx, unlock_y, "心を留めるな  ·  ENTER KEY TO CLEAR THE MIND", f_date, INK_MUTED, spacing=int(2 * scale))
        
        # ---------------------------------------------------------------------
        # 4. Corner Telemetry (Classical Japanese Calligraphy & Philosophical Verses)
        # ---------------------------------------------------------------------
        pad_x = int(48 * scale)
        pad_y = int(40 * scale)
        
        # Top-Left: Musashi & The Way of the Sword
        draw.text((mx + pad_x, my + pad_y), "宮本 武蔵  ·  MIYAMOTO MUSASHI", font=f_corner_sub, fill=WASHI_WHITE)
        draw.text((mx + pad_x, my + pad_y + int(18 * scale)), "“Invincible is merely a word.”", font=f_corner, fill=INK_MUTED)
        
        # Top-Right: Takehiko Inoue Quote
        draw.text((mx + mw - pad_x, my + pad_y), "“Do you see how infinite you are?”", font=f_corner, fill=WASHI_WHITE, anchor="ra")
        draw.text((mx + mw - pad_x, my + pad_y + int(18 * scale)), "井上 雄彦  ·  TAKEHIKO INOUE", font=f_corner_sub, fill=INK_FAINT, anchor="ra")
        
        # Bottom-Left: The Water Scroll Philosophy
        draw.text((mx + pad_x, my + mh - pad_y - int(18 * scale)), "“Water obeys only itself. Thoroughly water. Absolutely free.”", font=f_corner, fill=INK_MUTED)
        draw.text((mx + pad_x, my + mh - pad_y), "五輪書  ·  THE BOOK OF FIVE RINGS", font=f_corner_sub, fill=INK_FAINT)
        
        # Bottom-Right: Strength and Kindness
        draw.text((mx + mw - pad_x, my + mh - pad_y - int(18 * scale)), "“All truly strong people are kind.”", font=f_corner, fill=WASHI_WHITE, anchor="ra")
        draw.text((mx + mw - pad_x, my + mh - pad_y), "浪人  ·  THE PATH OF THE VAGABOND", font=f_corner_sub, fill=VERMILION_RED, anchor="ra")

    canvas.save(OUTPUT_LOCK_IMG, "PNG", compress_level=1)
    print(f"BG_HEX={BG_HEX}")

if __name__ == "__main__":
    generate_lock_image()
