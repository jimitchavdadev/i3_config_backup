#!/usr/bin/env python3
"""
Aesthetic Magical Disappearing Screen Unlock Fader for i3
Provides a silky smooth, hardware-composited dissolve transition
from the Vagabond lock screen wallpaper into the active desktop.
"""

import sys
import os
import time
import signal
import warnings

# Suppress PyGI deprecation warnings
warnings.filterwarnings("ignore")

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib
import cairo

class UnlockFader:
    def __init__(self, img_path, duration=0.65):
        self.img_path = img_path
        self.duration = float(duration)
        self.pixbuf = None
        
        if img_path and os.path.isfile(img_path):
            try:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(img_path)
            except Exception as e:
                sys.stderr.write(f"Failed to load image: {e}\n")

        display = Gdk.Display.get_default()
        screen = display.get_default_screen()
        self.width = screen.get_width()
        self.height = screen.get_height()

        # Create override-redirect POPUP window covering all monitors
        self.window = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.window.set_default_size(self.width, self.height)
        self.window.set_size_request(self.width, self.height)
        self.window.move(0, 0)
        self.window.set_app_paintable(True)

        # Critical: Empty input shape ensures all mouse and keyboard events pass through
        empty_region = cairo.Region()
        self.window.input_shape_combine_region(empty_region)

        # Connect draw event
        self.window.connect("draw", self.on_draw)

        self.animating = False
        self.start_time = None

        # IPC Triggers: stdin and signals
        GLib.io_add_watch(sys.stdin.fileno(), GLib.IO_IN, self.on_stdin)
        signal.signal(signal.SIGUSR1, self.on_signal_trigger)
        signal.signal(signal.SIGTERM, self.on_signal_exit)
        signal.signal(signal.SIGINT, self.on_signal_exit)

        # Safety auto-timeout (2 hours) to avoid hanging orphaned processes
        GLib.timeout_add_seconds(7200, self.on_timeout)

        # Show window and confirm readiness
        self.window.show_all()
        sys.stdout.write("READY\n")
        sys.stdout.flush()

    def on_draw(self, widget, cr):
        if self.pixbuf:
            Gdk.cairo_set_source_pixbuf(cr, self.pixbuf, 0, 0)
            cr.paint()
        else:
            cr.set_source_rgb(0.06, 0.05, 0.06)
            cr.paint()
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

        # Cinematic magical dissolve curve
        # (1.0 - t)^1.8 gives a smooth, ethereal dissipation
        alpha = (1.0 - t) ** 1.8
        self.window.set_opacity(max(0.0, alpha))

        if t >= 1.0:
            self.window.destroy()
            Gtk.main_quit()
            return False
        return True

def main():
    img_path = "/tmp/i3lock_aesthetic.png"
    duration = 0.65
    
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

    app = UnlockFader(img_path, duration)
    Gtk.main()

if __name__ == "__main__":
    main()
