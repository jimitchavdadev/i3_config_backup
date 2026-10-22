#!/usr/bin/env python3
"""
Cyberpunk Multi-Monitor Lock Screen Generator for i3
Renders high-tech HUD elements, digital neon glow clock, chamfered user badge,
reticle targeting frame around i3lock indicator, scanlines, and corner telemetry.
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

# Cyberpunk Theme Colors
BG_HEX = "1A1313"
BG_COLOR = (22, 17, 24)
FG_COLOR = (218, 245, 253)
NEON_CYAN = (21, 191, 245)
NEON_PINK = (242, 146, 223)
NEON_AMBER = (246, 178, 105)
MUTED_TEXT = (112, 170, 188)

def hex_to_rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 6:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return None

def load_theme_colors():
    global BG_HEX, BG_COLOR, FG_COLOR, NEON_CYAN, NEON_PINK, NEON_AMBER, MUTED_TEXT
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
                    elif line.startswith("color9 =") or line.startswith("color14 ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: NEON_CYAN = c
                    elif line.startswith("color10 ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: NEON_PINK = c
                    elif line.startswith("color13 =") or line.startswith("color11 ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: NEON_AMBER = c
                    elif line.startswith("secondary ="):
                        c = hex_to_rgb(line.split("=")[1])
                        if c: MUTED_TEXT = c
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

    # Dark cyber vignette overlay
    overlay = Image.new("RGBA", (tw, th), (8, 6, 12, 135))
    canvas = Image.alpha_composite(canvas, overlay)

    # Subtle horizontal cyber scanlines
    scanlines = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(scanlines)
    for y in range(0, th, 4):
        sdraw.line([(0, y), (tw, y)], fill=(0, 0, 0, 35))
    canvas = Image.alpha_composite(canvas, scanlines)

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
    date_str = now.strftime("%A // %d %B %Y").upper()
    user_name = os.environ.get("USER", "jimitchavda").upper()

    for m in monitors:
        mw, mh = m["width"], m["height"]
        mx, my = m["x"], m["y"]
        cx = mx + (mw // 2)
        cy = my + (mh // 2)
        scale = mh / 1080.0
        
        # Scale fonts
        time_size = int(90 * scale)
        date_size = int(17 * scale)
        badge_size = int(13 * scale)
        hud_size = int(12 * scale)
        corner_size = int(11 * scale)
        
        try:
            f_time = ImageFont.truetype(font_bold_path, time_size)
            f_date = ImageFont.truetype(font_reg_path, date_size)
            f_badge = ImageFont.truetype(font_bold_path, badge_size)
            f_hud = ImageFont.truetype(font_bold_path, hud_size)
            f_corner = ImageFont.truetype(font_reg_path, corner_size)
        except Exception:
            f_time = f_date = f_badge = f_hud = f_corner = ImageFont.load_default()
        
        # ---------------------------------------------------------------------
        # 1. Central Cyberpunk HUD Reticle around i3lock ring
        # ---------------------------------------------------------------------
        r_hud = int(118 * scale)
        bracket_len = int(24 * scale)
        
        # Glowing Corner Tech Brackets
        draw.line([(cx - r_hud, cy - r_hud + bracket_len), (cx - r_hud, cy - r_hud), (cx - r_hud + bracket_len, cy - r_hud)], fill=NEON_CYAN, width=2)
        draw.line([(cx + r_hud - bracket_len, cy - r_hud), (cx + r_hud, cy - r_hud), (cx + r_hud, cy - r_hud + bracket_len)], fill=NEON_CYAN, width=2)
        draw.line([(cx - r_hud, cy + r_hud - bracket_len), (cx - r_hud, cy + r_hud), (cx - r_hud + bracket_len, cy + r_hud)], fill=NEON_CYAN, width=2)
        draw.line([(cx + r_hud - bracket_len, cy + r_hud), (cx + r_hud, cy + r_hud), (cx + r_hud, cy + r_hud - bracket_len)], fill=NEON_CYAN, width=2)
        
        # Concentric HUD arcs (Neon Pink)
        arc_inset = int(10 * scale)
        draw.arc([cx - r_hud + arc_inset, cy - r_hud + arc_inset, cx + r_hud - arc_inset, cy + r_hud - arc_inset], start=30, end=60, fill=NEON_PINK, width=2)
        draw.arc([cx - r_hud + arc_inset, cy - r_hud + arc_inset, cx + r_hud - arc_inset, cy + r_hud - arc_inset], start=120, end=150, fill=NEON_PINK, width=2)
        draw.arc([cx - r_hud + arc_inset, cy - r_hud + arc_inset, cx + r_hud - arc_inset, cy + r_hud - arc_inset], start=210, end=240, fill=NEON_PINK, width=2)
        draw.arc([cx - r_hud + arc_inset, cy - r_hud + arc_inset, cx + r_hud - arc_inset, cy + r_hud - arc_inset], start=300, end=330, fill=NEON_PINK, width=2)
        
        # Crosshair alignment ticks
        tick_in = r_hud + int(6 * scale)
        tick_out = r_hud + int(16 * scale)
        draw.line([(cx - tick_out, cy), (cx - tick_in, cy)], fill=NEON_CYAN, width=1)
        draw.line([(cx + tick_in, cy), (cx + tick_out, cy)], fill=NEON_CYAN, width=1)
        draw.line([(cx, cy - tick_out), (cx, cy - tick_in)], fill=NEON_CYAN, width=1)
        draw.line([(cx, cy + tick_in), (cx, cy + tick_out)], fill=NEON_CYAN, width=1)
        
        # Reticle Top Tag
        reticle_tag = "[ BIOMETRIC // LOCK ]"
        draw.text((cx, cy - r_hud - int(12 * scale)), reticle_tag, font=f_hud, fill=NEON_PINK, anchor="ms")
        
        # ---------------------------------------------------------------------
        # 2. Clock & Date (Above Reticle with guaranteed clearance)
        # ---------------------------------------------------------------------
        clock_y = cy - r_hud - int(160 * scale)
        
        # Neon Glow pass for Clock
        for ox, oy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
            draw.text((cx + ox, clock_y + oy), time_str, font=f_time, fill=(*NEON_CYAN, 70), anchor="mm")
        # Crisp core
        draw.text((cx, clock_y), time_str, font=f_time, fill=FG_COLOR, anchor="mm")
        
        # Tech divider line with center diamond
        div_w = int(170 * scale)
        div_y = clock_y + int(48 * scale)
        draw.line([(cx - div_w, div_y), (cx - 16, div_y)], fill=(*NEON_CYAN, 160), width=1)
        draw.polygon([(cx - 5, div_y), (cx, div_y - 4), (cx + 5, div_y), (cx, div_y + 4)], fill=NEON_PINK)
        draw.line([(cx + 16, div_y), (cx + div_w, div_y)], fill=(*NEON_CYAN, 160), width=1)
        
        # Date
        date_y = div_y + int(18 * scale)
        draw.text((cx, date_y), date_str, font=f_date, fill=NEON_CYAN, anchor="mm")
        
        # ---------------------------------------------------------------------
        # 3. Chamfered Sci-Fi User Badge
        # ---------------------------------------------------------------------
        badge_y = date_y + int(38 * scale)
        badge_text = f"// USER: {user_name} // NODE: 0x7F //"
        bb = draw.textbbox((0, 0), badge_text, font=f_badge)
        bw = bb[2] - bb[0]
        bh = bb[3] - bb[1]
        
        pw = bw + int(32 * scale)
        ph = bh + int(14 * scale)
        px1 = cx - (pw // 2)
        py1 = badge_y - (ph // 2)
        px2 = px1 + pw
        py2 = py1 + ph
        chamfer = int(6 * scale)
        
        badge_poly = [
            (px1 + chamfer, py1),
            (px2 - chamfer, py1),
            (px2, py1 + chamfer),
            (px2, py2 - chamfer),
            (px2 - chamfer, py2),
            (px1 + chamfer, py2),
            (px1, py2 - chamfer),
            (px1, py1 + chamfer)
        ]
        draw.polygon(badge_poly, fill=(24, 18, 28, 220), outline=NEON_PINK)
        draw.text((cx, badge_y), badge_text, font=f_badge, fill=FG_COLOR, anchor="mm")
        
        # ---------------------------------------------------------------------
        # 4. Input Command Prompt (Below Reticle with guaranteed clearance)
        # ---------------------------------------------------------------------
        prompt_y = cy + r_hud + int(36 * scale)
        prompt_w = int(320 * scale)
        prompt_h = int(34 * scale)
        pr_x1 = cx - (prompt_w // 2)
        pr_y1 = prompt_y
        pr_x2 = pr_x1 + prompt_w
        pr_y2 = pr_y1 + prompt_h
        
        # Cyber bracket container
        draw.line([(pr_x1, pr_y1), (pr_x1 + 12, pr_y1)], fill=NEON_CYAN, width=1)
        draw.line([(pr_x1, pr_y1), (pr_x1, pr_y2)], fill=NEON_CYAN, width=1)
        draw.line([(pr_x1, pr_y2), (pr_x1 + 12, pr_y2)], fill=NEON_CYAN, width=1)
        
        draw.line([(pr_x2 - 12, pr_y1), (pr_x2, pr_y1)], fill=NEON_CYAN, width=1)
        draw.line([(pr_x2, pr_y1), (pr_x2, pr_y2)], fill=NEON_CYAN, width=1)
        draw.line([(pr_x2 - 12, pr_y2), (pr_x2, pr_y2)], fill=NEON_CYAN, width=1)
        
        prompt_text = ">> ENTER ACCESS CIPHER [ _ ]"
        draw.text((cx, prompt_y + (prompt_h // 2)), prompt_text, font=f_hud, fill=NEON_AMBER, anchor="mm")
        
        # ---------------------------------------------------------------------
        # 5. Screen Corner HUD Telemetry
        # ---------------------------------------------------------------------
        pad_x = int(38 * scale)
        pad_y = int(32 * scale)
        
        # Top-Left
        draw.text((mx + pad_x, my + pad_y), f"┌─ [ CYBERDECK // {m['name']} ]", font=f_corner, fill=NEON_CYAN)
        draw.text((mx + pad_x, my + pad_y + int(16 * scale)), f"│  RES: {mw}x{mh} // ENCRYPT: AES-256", font=f_corner, fill=MUTED_TEXT)
        
        # Top-Right
        draw.text((mx + mw - pad_x, my + pad_y), "[ FIREWALL: ARMORED ] ─┐", font=f_corner, fill=NEON_PINK, anchor="ra")
        draw.text((mx + mw - pad_x, my + pad_y + int(16 * scale)), "SYS_INTEGRITY: 100% │", font=f_corner, fill=MUTED_TEXT, anchor="ra")
        
        # Bottom-Left
        draw.text((mx + pad_x, my + mh - pad_y - int(16 * scale)), "│  KERNEL: LINUX_x86_64 // i3-NEO", font=f_corner, fill=MUTED_TEXT)
        draw.text((mx + pad_x, my + mh - pad_y), "└─ [ SESSION: STANDBY ]", font=f_corner, fill=NEON_CYAN)
        
        # Bottom-Right
        draw.text((mx + mw - pad_x, my + mh - pad_y - int(16 * scale)), "PORT: PAM_AUTH // TTY1 │", font=f_corner, fill=MUTED_TEXT, anchor="ra")
        draw.text((mx + mw - pad_x, my + mh - pad_y), "[ READY FOR DECRYPT ] ─┘", font=f_corner, fill=NEON_AMBER, anchor="ra")

    canvas.save(OUTPUT_LOCK_IMG, "PNG", compress_level=1)
    print(f"BG_HEX={BG_HEX}")

if __name__ == "__main__":
    generate_lock_image()
