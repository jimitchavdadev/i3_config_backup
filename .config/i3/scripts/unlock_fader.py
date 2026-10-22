#!/usr/bin/env python3
"""
Vagabond Blood Katana Screen Unlocker for i3
- With each keystroke: strikes dynamic tiny blood sword slashes inside the Ensō circle.
- On successful unlock [Enter]: unleashes the epic, full-screen lethal Katana strike (居合血斬),
  slicing reality with an incandescent blood trail and silver blade flash, then smoothly dissolving
  into the active desktop.
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
    """Finds all active keyboard evdev interfaces to detect keystrokes."""
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
        self.duration = 0.28  # 280ms lifetime
        self.scale = scale

        # Subtle jitter within the Ensō circle void
        jitter_r = random.uniform(0, 28.0 * scale)
        jitter_a = random.uniform(0, 2 * math.pi)
        scx = cx + jitter_r * math.cos(jitter_a)
        scy = cy + jitter_r * math.sin(jitter_a)

        if is_backspace:
            # Horizontal cut for backspace
            angle = random.uniform(-0.15, 0.15)
            length = random.uniform(140.0, 180.0) * scale
        else:
            # Dynamic diagonal katana angles
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

        # Subtle curved arc
        bow = random.uniform(-12.0, 12.0) * scale
        self.pctrl = (scx - math.sin(angle) * bow, scy + math.cos(angle) * bow)

        # 5-8 tiny blood droplets / ink splatters
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

        # Blade moves across in first 0.07s
        strike_u = min(1.0, (t / 0.07) ** 1.35)
        # Fade out curve
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
        random.seed(1584)  # Musashi birth year for deterministic final blood splatters

        for m in self.monitors:
            mx, my, mw, mh = m["x"], m["y"], m["w"], m["h"]
            cx = mx + (mw // 2)
            cy = my + (mh // 2)
            scale = mh / 1080.0

            # Final katana slash cutting diagonally across entire screen
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

        # Critical: Empty input shape ensures all keystrokes and clicks pass to i3lock
        empty_region = cairo.Region()
        self.window.input_shape_combine_region(empty_region)

        # Connect draw event
        self.window.connect("draw", self.on_draw)

        self.final_animating = False
        self.final_start_time = None
        self.final_t = 0.0
        self.tick_timer_id = None

        # Setup keyboard event listeners for keystroke slashes
        self.kbd_fds = []
        for dev in find_keyboards():
            try:
                fd = os.open(dev, os.O_RDONLY | os.O_NONBLOCK)
                self.kbd_fds.append(fd)
                GLib.io_add_watch(fd, GLib.IO_IN, self.on_key_event, fd)
            except Exception:
                pass

        # IPC Triggers (stdin and signals) for final unlock
        GLib.io_add_watch(sys.stdin.fileno(), GLib.IO_IN, self.on_stdin)
        signal.signal(signal.SIGUSR1, self.on_signal_trigger)
        signal.signal(signal.SIGTERM, self.on_signal_exit)
        signal.signal(signal.SIGINT, self.on_signal_exit)

        # Safety auto-timeout (2 hours)
        GLib.timeout_add_seconds(7200, self.on_timeout)

        # Show window and confirm readiness
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
                # EV_KEY (1) and KEY_DOWN (1)
                if ev_type == 1 and val == 1:
                    # Ignore Enter (handled by final unlock)
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

        # Ensure render tick loop is active
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

        # 1. Base Lock Screen Wallpaper
        if self.bg_surface:
            cr.set_source_surface(self.bg_surface, 0, 0)
            cr.paint()
        else:
            cr.set_source_rgb(0.06, 0.05, 0.06)
            cr.paint()

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        # 2. Render Active Keystroke Tiny Slashes
        if self.tiny_slashes:
            for ts in self.tiny_slashes:
                ts.draw(cr, now)

        # 3. Render Final Epic Full-Screen Blood Katana Strike
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
                self.trigger_final_disappear()
        except Exception:
            pass
        return False

    def on_signal_trigger(self, signum, frame):
        GLib.idle_add(self.trigger_final_disappear)

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

        # Clean expired tiny slashes
        self.tiny_slashes = [s for s in self.tiny_slashes if s.is_alive(now)]

        if self.final_animating:
            elapsed = now - self.final_start_time
            t = min(1.0, elapsed / self.duration)
            self.final_t = t

            self.window.queue_draw()

            # Dissolve window opacity into active desktop
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

        elif self.tiny_slashes:
            # Active tiny slashes still animating
            self.window.queue_draw()
            return True
        else:
            # Idle: no slashes active, pause tick timer to save CPU
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
