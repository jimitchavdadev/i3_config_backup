#!/usr/bin/env python3
"""
Vagabond Blood Katana Screen Unlocker for i3
- Keystrokes: Dynamic tiny Katana blood slashes inside the Ensō circle.
- Wrong password: Red Blasting Demon Eye (紅蓮の魔眼) erupts with shockwaves & arterial sparks.
- Successful unlock [Enter]: The final epic full-screen Katana Strike (居合血斬), slicing reality
  with an incandescent blood trail and silver blade flash, then smoothly dissolving into the desktop.
"""

import sys
import os
import re
import math
import time
import signal
import random
import struct
import subprocess
import warnings

# Suppress PyGI deprecation warnings
warnings.filterwarnings("ignore")

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import cairo

def get_monitors():
    monitors = []
    try:
        output = subprocess.check_output(["xrandr", "--query"], stderr=subprocess.DEVNULL).decode("utf-8")
        for line in output.splitlines():
            m = re.match(r'^([a-zA-Z0-9_-]+)\s+connected\s+(primary\s+)?([0-9]+)x([0-9]+)\+([0-9]+)\+([0-9]+)', line)
            if m:
                monitors.append({
                    "name": m.group(1),
                    "primary": bool(m.group(2)),
                    "w": int(m.group(3)),
                    "h": int(m.group(4)),
                    "x": int(m.group(5)),
                    "y": int(m.group(6))
                })
    except Exception:
        pass
    if not monitors:
        monitors.append({"name": "default", "primary": True, "w": 1920, "h": 1080, "x": 0, "y": 0})
    return monitors

def find_keyboards():
    """Finds active keyboard evdev interfaces to detect keystrokes."""
    keyboards = []
    try:
        with open('/proc/bus/input/devices', 'r') as f:
            curr_handlers = []
            for line in f:
                line = line.strip()
                if line.startswith('H: Handlers='):
                    curr_handlers = line[12:].split()
                elif line.startswith('B: EV='):
                    if 'kbd' in curr_handlers:
                        for h in curr_handlers:
                            if h.startswith('event'):
                                dev_path = f'/dev/input/{h}'
                                if os.path.exists(dev_path) and dev_path not in keyboards:
                                    try:
                                        fd = os.open(dev_path, os.O_RDONLY | os.O_NONBLOCK)
                                        os.close(fd)
                                        keyboards.append(dev_path)
                                    except Exception:
                                        pass
    except Exception:
        pass
    return keyboards

class TinySlash:
    """A swift, lethal miniature katana slash striking across the Ensō circle upon each keystroke."""
    def __init__(self, cx, cy, scale, is_backspace=False):
        self.start_time = time.time()
        self.duration = 0.28
        self.scale = scale

        jitter_r = random.uniform(0, 28.0 * scale)
        jitter_a = random.uniform(0, 2 * math.pi)
        scx = cx + jitter_r * math.cos(jitter_a)
        scy = cy + jitter_r * math.sin(jitter_a)

        if is_backspace:
            angle = random.uniform(-0.15, 0.15)
            length = random.uniform(140.0, 180.0) * scale
        else:
            angle = random.choice([
                random.uniform(-0.85, -0.35),
                random.uniform(0.35, 0.85),
                random.uniform(-1.45, -1.05),
                random.uniform(1.05, 1.45)
            ])
            length = random.uniform(90.0, 150.0) * scale

        dx = math.cos(angle) * (length / 2.0)
        dy = math.sin(angle) * (length / 2.0)

        self.p0 = (scx - dx, scy - dy)
        self.p1 = (scx + dx, scy + dy)

        bow = random.uniform(-12.0, 12.0) * scale
        self.pctrl = (scx - math.sin(angle) * bow, scy + math.cos(angle) * bow)

        self.drops = []
        for _ in range(random.randint(5, 9)):
            self.drops.append({
                "u": random.uniform(0.12, 0.88),
                "offset": random.uniform(-18.0, 18.0) * scale,
                "r": random.uniform(1.8, 3.8) * scale,
            })

    def is_alive(self, now):
        return (now - self.start_time) < self.duration

    def draw(self, cr, now):
        elapsed = now - self.start_time
        t = min(1.0, elapsed / self.duration)

        strike_u = min(1.0, (t / 0.07) ** 1.35)
        fade_a = max(0.0, float(1.0 - (t / self.duration) ** 1.4))

        steps = max(3, int(16 * strike_u))
        pts = []
        for i in range(steps + 1):
            u = (i / float(steps)) * strike_u
            omt = 1.0 - u
            x = omt * omt * self.p0[0] + 2.0 * omt * u * self.pctrl[0] + u * u * self.p1[0]
            y = omt * omt * self.p0[1] + 2.0 * omt * u * self.pctrl[1] + u * u * self.p1[1]
            pts.append((x, y))

        if len(pts) >= 2:
            # 1. Crimson Blood Mist Wash
            cr.set_source_rgba(0.82, 0.08, 0.08, 0.55 * fade_a)
            cr.set_line_width(15.0 * self.scale)
            cr.move_to(*pts[0])
            for pt in pts[1:]:
                cr.line_to(*pt)
            cr.stroke()

            # 2. Rich Arterial Vermilion Core
            cr.set_source_rgba(0.96, 0.12, 0.08, 0.90 * fade_a)
            cr.set_line_width(5.8 * self.scale)
            cr.move_to(*pts[0])
            for pt in pts[1:]:
                cr.line_to(*pt)
            cr.stroke()

            # 3. Razor Silver Blade Edge Flash
            flash_a = max(0.0, float(1.0 - (t / 0.10) ** 1.5))
            if flash_a > 0.01:
                cr.set_source_rgba(1.0, 0.98, 0.98, flash_a * 0.95)
                cr.set_line_width(2.0 * self.scale)
                cr.move_to(*pts[0])
                for pt in pts[1:]:
                    cr.line_to(*pt)
                cr.stroke()

            # 4. Tiny Blood Droplets
            for d in self.drops:
                if strike_u >= d["u"]:
                    omt = 1.0 - d["u"]
                    bx = omt * omt * self.p0[0] + 2.0 * omt * d["u"] * self.pctrl[0] + d["u"] * d["u"] * self.p1[0]
                    by = omt * omt * self.p0[1] + 2.0 * omt * d["u"] * self.pctrl[1] + d["u"] * d["u"] * self.p1[1]
                    dx = bx + d["offset"]
                    dy = by + d["offset"]
                    cr.set_source_rgba(0.90, 0.08, 0.08, 0.85 * fade_a)
                    cr.arc(dx, dy, d["r"], 0, 2 * math.pi)
                    cr.fill()

class RedBlastingEye:
    """The Red Blasting Demon Eye that awakens and blasts in the center upon incorrect password."""
    def __init__(self, cx, cy, scale):
        self.cx = cx
        self.cy = cy
        self.scale = scale
        self.start_time = time.time()
        self.duration = 1.15  # 1.15s dramatic blast & glare

        # 36 radial blast particles / sparks
        self.particles = []
        for _ in range(36):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(70.0, 165.0) * scale
            r = random.uniform(2.2, 5.0) * scale
            self.particles.append((angle, speed, r))

        # Vein branches
        self.veins = []
        for _ in range(8):
            angle = random.uniform(-0.6, 0.6) if random.random() < 0.5 else random.uniform(2.5, 3.7)
            length = random.uniform(30.0, 65.0) * scale
            self.veins.append((angle, length))

    def is_alive(self, now):
        return (now - self.start_time) < self.duration

    def draw(self, cr, now):
        elapsed = now - self.start_time
        t = min(1.0, elapsed / self.duration)

        # Eye snap open curve
        open_ratio = min(1.0, (t / 0.12) ** 1.6)

        # Dissolve fade curve
        if t < 0.45:
            fade_a = 1.0
        else:
            fade_a = max(0.0, float((1.0 - (t - 0.45) / 0.55) ** 1.6))

        # Camera tremor / screen shake during blast (first 0.15s)
        if t < 0.15:
            shake_y = (1.0 - t / 0.15) * 5.0 * math.sin(t * 110)
            shake_x = (1.0 - t / 0.15) * 3.0 * math.cos(t * 90)
        else:
            shake_x, shake_y = 0.0, 0.0

        cx = self.cx + shake_x
        cy = self.cy + shake_y
        scale = self.scale

        eye_w = 88.0 * scale
        eye_h = 50.0 * scale * open_ratio

        # -------------------------------------------------------------
        # 1. Outer Crimson Ambient Aura
        # -------------------------------------------------------------
        cr.set_source_rgba(0.92, 0.06, 0.06, 0.38 * fade_a)
        cr.arc(cx, cy, eye_w * 1.35, 0, 2 * math.pi)
        cr.fill()

        # -------------------------------------------------------------
        # 2. Almond Eyelid Contour & Dark Sclera
        # -------------------------------------------------------------
        cr.move_to(cx - eye_w, cy)
        cr.curve_to(cx - eye_w * 0.5, cy - eye_h * 1.25, cx + eye_w * 0.5, cy - eye_h * 1.25, cx + eye_w, cy)
        cr.curve_to(cx + eye_w * 0.5, cy + eye_h * 1.25, cx - eye_w * 0.5, cy + eye_h * 1.25, cx - eye_w, cy)
        cr.close_path()

        # Deep demonic blood sclera
        cr.set_source_rgba(0.24, 0.02, 0.02, 0.95 * fade_a)
        cr.fill_preserve()

        # Fiery vermilion eyelid stroke
        cr.set_source_rgba(0.95, 0.12, 0.08, 0.95 * fade_a)
        cr.set_line_width(3.4 * scale)
        cr.stroke()

        # -------------------------------------------------------------
        # 3. Pulsating Blood Veins
        # -------------------------------------------------------------
        cr.set_line_width(1.6 * scale)
        cr.set_source_rgba(0.85, 0.08, 0.08, 0.75 * fade_a)
        for ang, length in self.veins:
            x0 = cx + math.cos(ang) * (eye_w * 0.75)
            y0 = cy + math.sin(ang) * (eye_h * 0.4)
            x1 = x0 + math.cos(ang) * length
            y1 = y0 + math.sin(ang) * (length * 0.5)
            cr.move_to(x0, y0)
            cr.line_to(x1, y1)
        cr.stroke()

        # -------------------------------------------------------------
        # 4. Glowing Iris
        # -------------------------------------------------------------
        iris_r = 25.0 * scale * open_ratio
        cr.set_source_rgba(0.96, 0.10, 0.06, 0.96 * fade_a)
        cr.arc(cx, cy, iris_r, 0, 2 * math.pi)
        cr.fill()

        # Inner Iris Ring
        cr.set_source_rgba(1.0, 0.38, 0.10, 0.92 * fade_a)
        cr.set_line_width(2.0 * scale)
        cr.arc(cx, cy, iris_r * 0.65, 0, 2 * math.pi)
        cr.stroke()

        # -------------------------------------------------------------
        # 5. Demonic Vertical Slit Pupil
        # -------------------------------------------------------------
        cr.save()
        cr.translate(cx, cy)
        cr.scale(1.0, 3.8)
        cr.set_source_rgba(0.02, 0.01, 0.02, 1.0 * fade_a)
        cr.arc(0, 0, 4.2 * scale * open_ratio, 0, 2 * math.pi)
        cr.fill()
        cr.restore()

        # Eye specular glint
        cr.set_source_rgba(1.0, 0.96, 0.96, 0.95 * fade_a)
        cr.arc(cx - 5.0 * scale, cy - 6.0 * scale, 2.5 * scale, 0, 2 * math.pi)
        cr.fill()

        # -------------------------------------------------------------
        # 6. Energy Blast Shockwave Rings
        # -------------------------------------------------------------
        if t > 0.06:
            sw_prog1 = (t - 0.06) / 0.42
            if sw_prog1 < 1.0:
                sw_r1 = sw_prog1 * 140.0 * scale
                sw_a1 = (1.0 - sw_prog1) * fade_a
                cr.set_source_rgba(1.0, 0.16, 0.10, sw_a1 * 0.85)
                cr.set_line_width(2.8 * scale)
                cr.arc(cx, cy, sw_r1, 0, 2 * math.pi)
                cr.stroke()

        if t > 0.12:
            sw_prog2 = (t - 0.12) / 0.45
            if sw_prog2 < 1.0:
                sw_r2 = sw_prog2 * 115.0 * scale
                sw_a2 = (1.0 - sw_prog2) * fade_a
                cr.set_source_rgba(0.92, 0.08, 0.08, sw_a2 * 0.70)
                cr.set_line_width(2.0 * scale)
                cr.arc(cx, cy, sw_r2, 0, 2 * math.pi)
                cr.stroke()

        # -------------------------------------------------------------
        # 7. Radial Blast Sparks & Blood Particles
        # -------------------------------------------------------------
        if t > 0.05:
            p_prog = min(1.0, (t - 0.05) / 0.48)
            p_alpha = (1.0 - p_prog) * fade_a
            for ang, spd, pr in self.particles:
                dist = p_prog * spd
                px = cx + math.cos(ang) * dist
                py = cy + math.sin(ang) * dist
                cr.set_source_rgba(1.0, 0.18, 0.08, p_alpha * 0.92)
                cr.arc(px, py, pr, 0, 2 * math.pi)
                cr.fill()

class BloodKatanaFader:
    def __init__(self, img_path, duration=0.72):
        self.img_path = img_path
        self.duration = float(duration)
        self.bg_surface = None

        display = Gdk.Display.get_default()
        screen = display.get_default_screen()
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Pre-cache background into cairo ImageSurface for 300+ FPS rendering
        if img_path and os.path.isfile(img_path):
            try:
                pb = GdkPixbuf.Pixbuf.new_from_file(img_path)
                self.bg_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.width, self.height)
                cr_bg = cairo.Context(self.bg_surface)
                Gdk.cairo_set_source_pixbuf(cr_bg, pb, 0, 0)
                cr_bg.paint()
            except Exception as e:
                sys.stderr.write(f"Failed to prepare background: {e}\n")

        # Setup monitors and trajectories
        self.monitors = get_monitors()
        self.slashes = []
        self.tiny_slashes = []
        self.wrong_eyes = []
        random.seed(1584)  # Musashi birth year for deterministic final blood splatters

        for m in self.monitors:
            mx, my, mw, mh = m["x"], m["y"], m["w"], m["h"]
            cx = mx + (mw // 2)
            cy = my + (mh // 2)
            scale = mh / 1080.0

            p0 = (cx - mw * 0.44, cy - mh * 0.34)
            p1 = (cx + mw * 0.44, cy + mh * 0.34)
            pctrl = (cx + 25.0 * scale, cy + 45.0 * scale)

            particles = []
            for _ in range(45):
                u = random.uniform(0.06, 0.94)
                offset = random.uniform(-45.0, 45.0) * scale
                r = random.uniform(2.5, 6.5) * scale
                alpha = random.uniform(0.70, 0.95)
                particles.append({
                    "u": u,
                    "offset": offset,
                    "r": r,
                    "alpha": alpha,
                    "spray_t": u * 0.18
                })

            self.slashes.append({
                "cx": cx,
                "cy": cy,
                "p0": p0,
                "p1": p1,
                "pctrl": pctrl,
                "scale": scale,
                "particles": particles
            })

        # Override-redirect POPUP window covering all monitors
        GLib.set_prgname("unlock_fader")
        GLib.set_application_name("unlock_fader")
        self.window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.window.set_wmclass("unlock_fader", "unlock_fader")
        self.window.set_role("lockscreen_overlay")
        self.window.set_default_size(self.width, self.height)
        self.window.set_size_request(self.width, self.height)
        self.window.move(0, 0)
        self.window.set_app_paintable(True)
        self.window.set_keep_above(True)

        empty_region = cairo.Region()
        self.window.input_shape_combine_region(empty_region)

        self.window.connect("draw", self.on_draw)

        self.final_animating = False
        self.final_start_time = None
        self.final_t = 0.0
        self.tick_timer_id = None

        # Setup keyboard event listeners
        self.kbd_fds = []
        for dev in find_keyboards():
            try:
                fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)
                self.kbd_fds.append(fd)
                GLib.io_add_watch(fd, GLib.IO_IN, self.on_key_event, fd)
            except Exception:
                pass

        # IPC Triggers (stdin and signals)
        GLib.io_add_watch(sys.stdin.fileno(), GLib.IO_IN, self.on_stdin)
        signal.signal(signal.SIGUSR1, self.on_sig_disappear)
        signal.signal(signal.SIGUSR2, self.on_sig_wrong)
        signal.signal(signal.SIGTERM, self.on_signal_exit)
        signal.signal(signal.SIGINT, self.on_signal_exit)

        # Safety auto-timeout (2 hours)
        GLib.timeout_add_seconds(7200, self.on_timeout)

        self.window.show_all()
        sys.stdout.write("READY\n")
        sys.stdout.flush()

    def on_key_event(self, source, condition, fd):
        """Reads raw keyboard events from evdev to trigger tiny slashes on each keystroke."""
        try:
            data = os.read(fd, 24 * 16)
            while len(data) >= 24:
                sec, usec, ev_type, code, val = struct.unpack('qqHHi', data[:24])
                data = data[24:]
                if ev_type == 1 and val == 1:
                    # Clear wrong eye once user starts typing again
                    if self.wrong_eyes:
                        self.wrong_eyes.clear()
                    if code not in (28, 96):
                        is_bksp = (code == 14)
                        self.trigger_keystroke_slash(is_bksp)
        except Exception:
            pass
        return True

    def trigger_keystroke_slash(self, is_backspace=False):
        """Spawns a tiny blood slash inside each monitor's Ensō circle."""
        if self.final_animating:
            return

        for slash in self.slashes:
            cx, cy, scale = slash["cx"], slash["cy"], slash["scale"]
            self.tiny_slashes.append(TinySlash(cx, cy, scale, is_backspace=is_backspace))

        if self.tick_timer_id is None:
            self.tick_timer_id = GLib.timeout_add(16, self.on_tick)

        self.window.queue_draw()

    def trigger_wrong_password_eye(self):
        """Spawns the Red Blasting Demon Eye in the center on wrong password."""
        if self.final_animating:
            return

        self.tiny_slashes.clear()
        self.wrong_eyes.clear()

        for slash in self.slashes:
            cx, cy, scale = slash["cx"], slash["cy"], slash["scale"]
            self.wrong_eyes.append(RedBlastingEye(cx, cy, scale))

        if self.tick_timer_id is None:
            self.tick_timer_id = GLib.timeout_add(16, self.on_tick)

        self.window.queue_draw()

    def eval_bezier(self, p0, pctrl, p1, u):
        omt = 1.0 - u
        x = omt * omt * p0[0] + 2.0 * omt * u * pctrl[0] + u * u * p1[0]
        y = omt * omt * p0[1] + 2.0 * omt * u * pctrl[1] + u * u * p1[1]
        return x, y

    def eval_tangent(self, p0, pctrl, p1, u):
        omt = 1.0 - u
        dx = 2.0 * omt * (pctrl[0] - p0[0]) + 2.0 * u * (p1[0] - pctrl[0])
        dy = 2.0 * omt * (pctrl[1] - p0[1]) + 2.0 * u * (p1[1] - pctrl[1])
        mag = math.hypot(dx, dy) or 1.0
        return dx / mag, dy / mag

    def on_draw(self, widget, cr):
        now = time.time()

        # 1. Base Wallpaper
        if self.bg_surface:
            cr.set_source_surface(self.bg_surface, 0, 0)
            cr.paint()
        else:
            cr.set_source_rgb(0.06, 0.05, 0.06)
            cr.paint()

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        # 2. Render Red Blasting Eye (Wrong Password)
        if self.wrong_eyes:
            for eye in self.wrong_eyes:
                eye.draw(cr, now)

        # 3. Render Keystroke Tiny Slashes
        if self.tiny_slashes:
            for ts in self.tiny_slashes:
                ts.draw(cr, now)

        # 4. Render Final Full-Screen Blood Katana Strike
        if self.final_animating:
            t = self.final_t
            strike_u = min(1.0, (t / 0.22) ** 1.35)

            if t < 0.24:
                blood_alpha = min(1.0, t / 0.08)
            else:
                blood_alpha = max(0.0, float(1.0 - ((t - 0.24) / 0.76) ** 1.2))

            for slash in self.slashes:
                p0 = slash["p0"]
                p1 = slash["p1"]
                pctrl = slash["pctrl"]
                scale = slash["scale"]
                particles = slash["particles"]

                steps = max(4, int(40 * strike_u))
                pts = [self.eval_bezier(p0, pctrl, p1, (i / float(steps)) * strike_u) for i in range(steps + 1)]

                if len(pts) >= 2:
                    # Outer Crimson Mist Wash
                    cr.set_source_rgba(0.75, 0.06, 0.06, 0.55 * blood_alpha)
                    cr.set_line_width(36.0 * scale)
                    cr.move_to(*pts[0])
                    for pt in pts[1:]:
                        cr.line_to(*pt)
                    cr.stroke()

                    # Arterial Vermilion Core
                    cr.set_source_rgba(0.92, 0.10, 0.08, 0.88 * blood_alpha)
                    cr.set_line_width(14.0 * scale)
                    cr.move_to(*pts[0])
                    for pt in pts[1:]:
                        cr.line_to(*pt)
                    cr.stroke()

                    # Incision Sumi Crevice
                    cr.set_source_rgba(0.06, 0.04, 0.05, 0.75 * blood_alpha)
                    cr.set_line_width(5.0 * scale)
                    cr.move_to(*pts[0])
                    for pt in pts[1:]:
                        cr.line_to(*pt)
                    cr.stroke()

                    # Silver Katana Blade Edge
                    blade_flash = max(0.0, float(1.0 - (t / 0.28) ** 1.5))
                    if blade_flash > 0.01:
                        cr.set_source_rgba(1.0, 0.98, 0.98, blade_flash * 0.95)
                        cr.set_line_width(3.2 * scale)
                        cr.move_to(*pts[0])
                        for pt in pts[1:]:
                            cr.line_to(*pt)
                        cr.stroke()

                    # Blade Tip Spark Burst
                    if strike_u < 1.0:
                        tip_x, tip_y = pts[-1]
                        burst_r = (24.0 * (1.0 - strike_u) + 8.0) * scale
                        cr.set_source_rgba(1.0, 0.96, 0.90, 0.90)
                        cr.arc(tip_x, tip_y, burst_r * 0.45, 0, 2 * math.pi)
                        cr.fill()
                        cr.set_source_rgba(0.95, 0.15, 0.10, 0.65)
                        cr.arc(tip_x, tip_y, burst_r, 0, 2 * math.pi)
                        cr.fill()

                    # Arterial Blood Droplets
                    for drop in particles:
                        u = drop["u"]
                        if strike_u >= u:
                            bx, by = self.eval_bezier(p0, pctrl, p1, u)
                            tx, ty = self.eval_tangent(p0, pctrl, p1, u)
                            nx, ny = -ty, tx
                            time_since_cut = max(0.0, t - drop["spray_t"])
                            spread = min(1.0, time_since_cut / 0.15)
                            dx = bx + nx * drop["offset"] * spread
                            dy = by + ny * drop["offset"] * spread

                            drop_a = drop["alpha"] * blood_alpha
                            if drop_a > 0.01:
                                cr.set_source_rgba(0.88, 0.08, 0.08, drop_a)
                                cr.arc(dx, dy, drop["r"], 0, 2 * math.pi)
                                cr.fill()

        return True

    def on_stdin(self, fd, condition):
        try:
            line = sys.stdin.readline()
            if line:
                cmd = line.strip()
                if cmd == "WRONG":
                    self.trigger_wrong_password_eye()
                elif cmd == "DISAPPEAR":
                    self.trigger_final_disappear()
        except Exception:
            pass
        return True

    def on_sig_disappear(self, signum, frame):
        GLib.idle_add(self.trigger_final_disappear)

    def on_sig_wrong(self, signum, frame):
        GLib.idle_add(self.trigger_wrong_password_eye)

    def on_signal_exit(self, signum, frame):
        self.cleanup_fds()
        GLib.idle_add(Gtk.main_quit)

    def on_timeout(self):
        self.cleanup_fds()
        Gtk.main_quit()
        return False

    def cleanup_fds(self):
        for fd in self.kbd_fds:
            try:
                os.close(fd)
            except Exception:
                pass
        self.kbd_fds.clear()

    def trigger_final_disappear(self):
        """Called upon successful PAM authentication / Enter."""
        if self.final_animating:
            return
        self.final_animating = True
        self.final_start_time = time.time()
        self.cleanup_fds()

        if self.tick_timer_id is None:
            self.tick_timer_id = GLib.timeout_add(16, self.on_tick)

    def on_tick(self):
        now = time.time()

        self.tiny_slashes = [s for s in self.tiny_slashes if s.is_alive(now)]
        self.wrong_eyes = [e for e in self.wrong_eyes if e.is_alive(now)]

        if self.final_animating:
            elapsed = now - self.final_start_time
            t = min(1.0, elapsed / self.duration)
            self.final_t = t

            self.window.queue_draw()

            if t < 0.18:
                alpha = 1.0
            else:
                p_fade = min(1.0, max(0.0, (t - 0.18) / 0.82))
                alpha = max(0.0, float((1.0 - p_fade) ** 1.6))

            self.window.set_opacity(alpha)

            if t >= 1.0:
                self.window.destroy()
                Gtk.main_quit()
                return False
            return True

        elif self.tiny_slashes or self.wrong_eyes:
            self.window.queue_draw()
            return True
        else:
            self.window.queue_draw()
            self.tick_timer_id = None
            return False

def main():
    img_path = "/tmp/i3lock_aesthetic.png"
    duration = 0.72

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--bg" and i + 1 < len(args):
            img_path = args[i + 1]
            i += 2
        elif args[i] == "--duration" and i + 1 < len(args):
            duration = float(args[i + 1])
            i += 2
        else:
            i += 1

    app = BloodKatanaFader(img_path, duration)
    Gtk.main()

if __name__ == "__main__":
    main()
