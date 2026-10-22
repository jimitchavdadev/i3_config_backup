#!/usr/bin/env python3
"""
Vagabond Blood Katana Striking Screen Unlock Fader for i3
Executes a lethal samurai sword strike (居合血斬) across the screen upon unlocking,
carving through the realm with a crimson arterial blood trail and silver blade flash,
then smoothly dissolving into the active desktop.
"""

import sys
import os
import re
import math
import time
import signal
import random
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

        # Setup monitors and sword strike trajectories
        self.monitors = get_monitors()
        self.slashes = []
        random.seed(1584)  # Musashi birth year for deterministic blood splatters

        for m in self.monitors:
            mx, my, mw, mh = m["x"], m["y"], m["w"], m["h"]
            cx = mx + (mw // 2)
            cy = my + (mh // 2)
            scale = mh / 1080.0

            # Authentic katana slash arc cutting diagonally through center
            p0 = (cx - mw * 0.44, cy - mh * 0.34)
            p1 = (cx + mw * 0.44, cy + mh * 0.34)
            pctrl = (cx + 25.0 * scale, cy + 45.0 * scale)

            # Blood droplets / arterial splatter particles along the slash
            particles = []
            for _ in range(45):
                u = random.uniform(0.06, 0.94)
                offset = random.uniform(-45.0, 45.0) * scale
                r = random.uniform(2.5, 6.5) * scale
                alpha = random.uniform(0.70, 0.95)
                # Blood droplet spurts perpendicular to blade
                particles.append({
                    "u": u,
                    "offset": offset,
                    "r": r,
                    "alpha": alpha,
                    "spray_t": u * 0.18
                })

            self.slashes.append({
                "p0": p0,
                "p1": p1,
                "pctrl": pctrl,
                "scale": scale,
                "particles": particles
            })

        # Override-redirect POPUP window covering all monitors
        self.window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.window.set_default_size(self.width, self.height)
        self.window.set_size_request(self.width, self.height)
        self.window.move(0, 0)
        self.window.set_app_paintable(True)

        # Critical: Empty input shape ensures all input passes directly to desktop/i3lock
        empty_region = cairo.Region()
        self.window.input_shape_combine_region(empty_region)

        # Connect draw event
        self.window.connect("draw", self.on_draw)

        self.animating = False
        self.start_time = None
        self.t_progress = 0.0

        # IPC Triggers
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
        # 1. Base Wallpaper
        if self.bg_surface:
            cr.set_source_surface(self.bg_surface, 0, 0)
            cr.paint()
        else:
            cr.set_source_rgb(0.06, 0.05, 0.06)
            cr.paint()

        # If not animating yet, passive render
        if not self.animating:
            return True

        t = self.t_progress

        # Katana Strike Velocity (Strike reaches full length in first 0.22s)
        strike_u = min(1.0, (t / 0.22) ** 1.35)

        # Blood & Blade Intensity
        if t < 0.24:
            blood_alpha = min(1.0, t / 0.08)
        else:
            blood_alpha = max(0.0, 1.0 - ((t - 0.24) / 0.76) ** 1.2)

        cr.set_line_cap(cairo.LINE_CAP_ROUND)
        cr.set_line_join(cairo.LINE_JOIN_ROUND)

        for slash in self.slashes:
            p0 = slash["p0"]
            p1 = slash["p1"]
            pctrl = slash["pctrl"]
            scale = slash["scale"]
            particles = slash["particles"]

            # Sample points along the cutting arc up to current blade progress
            steps = max(4, int(40 * strike_u))
            pts = [self.eval_bezier(p0, pctrl, p1, (i / float(steps)) * strike_u) for i in range(steps + 1)]

            if len(pts) >= 2:
                # -------------------------------------------------------------
                # Layer 1: Crimson Arterial Blood Mist / Outer Aura
                # -------------------------------------------------------------
                cr.set_source_rgba(0.75, 0.06, 0.06, 0.55 * blood_alpha)
                cr.set_line_width(36.0 * scale)
                cr.move_to(*pts[0])
                for pt in pts[1:]:
                    cr.line_to(*pt)
                cr.stroke()

                # -------------------------------------------------------------
                # Layer 2: Deep Incandescent Blood-Red Core
                # -------------------------------------------------------------
                cr.set_source_rgba(0.92, 0.10, 0.08, 0.88 * blood_alpha)
                cr.set_line_width(14.0 * scale)
                cr.move_to(*pts[0])
                for pt in pts[1:]:
                    cr.line_to(*pt)
                cr.stroke()

                # -------------------------------------------------------------
                # Layer 3: Dark Ink Incision Crevice (Sumi Cut)
                # -------------------------------------------------------------
                cr.set_source_rgba(0.06, 0.04, 0.05, 0.75 * blood_alpha)
                cr.set_line_width(5.0 * scale)
                cr.move_to(*pts[0])
                for pt in pts[1:]:
                    cr.line_to(*pt)
                cr.stroke()

                # -------------------------------------------------------------
                # Layer 4: Razor-Sharp Silver Katana Edge (Blinding White-Hot)
                # -------------------------------------------------------------
                blade_flash = max(0.0, 1.0 - (t / 0.28) ** 1.5)
                if blade_flash > 0.01:
                    cr.set_source_rgba(1.0, 0.98, 0.98, blade_flash * 0.95)
                    cr.set_line_width(3.2 * scale)
                    cr.move_to(*pts[0])
                    for pt in pts[1:]:
                        cr.line_to(*pt)
                    cr.stroke()

                # -------------------------------------------------------------
                # Layer 5: Blade Tip Spark Burst (Active during strike)
                # -------------------------------------------------------------
                if strike_u < 1.0:
                    tip_x, tip_y = pts[-1]
                    burst_r = (24.0 * (1.0 - strike_u) + 8.0) * scale
                    cr.set_source_rgba(1.0, 0.96, 0.90, 0.90)
                    cr.arc(tip_x, tip_y, burst_r * 0.45, 0, 2 * math.pi)
                    cr.fill()
                    # Crimson bloom around tip
                    cr.set_source_rgba(0.95, 0.15, 0.10, 0.65)
                    cr.arc(tip_x, tip_y, burst_r, 0, 2 * math.pi)
                    cr.fill()

                # -------------------------------------------------------------
                # Layer 6: Arterial Blood Droplets & Ink Splatters
                # -------------------------------------------------------------
                for drop in particles:
                    u = drop["u"]
                    if strike_u >= u:
                        bx, by = self.eval_bezier(p0, pctrl, p1, u)
                        tx, ty = self.eval_tangent(p0, pctrl, p1, u)
                        # Perpendicular normal
                        nx, ny = -ty, tx
                        
                        # Droplets burst outwards as blade cuts
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
                self.trigger_disappear()
        except Exception:
            pass
        return False

    def on_signal_trigger(self, signum, frame):
        GLib.idle_add(self.trigger_disappear)

    def on_signal_exit(self, signum, frame):
        GLib.idle_add(Gtk.main_quit)

    def on_timeout(self):
        Gtk.main_quit()
        return False

    def trigger_disappear(self):
        if self.animating:
            return
        self.animating = True
        self.start_time = time.time()
        GLib.timeout_add(16, self.on_tick)

    def on_tick(self):
        now = time.time()
        elapsed = now - self.start_time
        t = min(1.0, elapsed / self.duration)
        self.t_progress = t

        # Redraw blood sword strike animation frame
        self.window.queue_draw()

        # Dissolve curve:
        # Full opacity during initial strike, then smoothly dissolves into active desktop
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
