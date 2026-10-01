"""Run the game in Dolphin as the reference: screenshots and key presses on a timeline.

    python tools/dolphin.py GAME.wbfs OUT_DIR "5 10 15:RETURN 20 25:RETURN 30" [--dolphin PATH] [--quit 40]

Each item of the timeline is SECONDS (a screenshot of the render window at
that time, OUT_DIR/dolphin_SECONDS.png) or SECONDS:KEY[+KEY...] (the keys
pressed for 150 ms, then a screenshot). Keys are Windows virtual-key names
(RETURN, BACK, TAB, UP, DOWN, LEFT, RIGHT, HOME, ESCAPE, SPACE) or a letter
or digit. Dolphin reads them through DirectInput, so the window is brought
to the front first; the keys reach it as the controller profile maps them
(Dolphin's GameSettings/<ID>.ini picks the profile). Windows only; needs
Pillow for the screenshots.
"""
import argparse
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import time

from PIL import ImageGrab

user32 = ctypes.windll.user32
VK = {"RETURN": 0x0D, "BACK": 0x08, "TAB": 0x09, "ESCAPE": 0x1B, "SPACE": 0x20, "LEFT": 0x25,
      "UP": 0x26, "RIGHT": 0x27, "DOWN": 0x28, "HOME": 0x24, "MINUS": 0xBD}
DOLPHIN = os.environ.get("DOLPHIN", "Dolphin.exe")         # or --dolphin PATH


def render_window(pid):
    """The biggest visible top-level window of the Dolphin process."""
    found = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wt.HWND, wt.LPARAM)
    def cb(hwnd, _):
        p = wt.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
        if p.value == pid and user32.IsWindowVisible(hwnd):
            r = wt.RECT()
            user32.GetClientRect(hwnd, ctypes.byref(r))
            found.append((r.right * r.bottom, hwnd))
        return True

    user32.EnumWindows(cb, 0)
    return max(found)[1] if found else None


def client_box(hwnd):
    r = wt.RECT()
    user32.GetClientRect(hwnd, ctypes.byref(r))
    pt = wt.POINT(0, 0)
    user32.ClientToScreen(hwnd, ctypes.byref(pt))
    return (pt.x, pt.y, pt.x + r.right, pt.y + r.bottom)


def press(hwnd, keys):
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.05)
    codes = [VK[k] if k in VK else ord(k.upper()) for k in keys]
    for c in codes:
        user32.keybd_event(c, user32.MapVirtualKeyW(c, 0), 0, 0)
    time.sleep(0.15)
    for c in reversed(codes):
        user32.keybd_event(c, user32.MapVirtualKeyW(c, 0), 2, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("disc")
    ap.add_argument("out")
    ap.add_argument("timeline")
    ap.add_argument("--dolphin", default=DOLPHIN)
    ap.add_argument("--quit", type=float, default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    proc = subprocess.Popen([a.dolphin, "-b", "-e", os.path.abspath(a.disc)])
    t0 = time.time()
    items = []
    for it in a.timeline.split():
        t, _, keys = it.partition(":")
        items.append((float(t), keys.split("+") if keys else []))
    for t, keys in sorted(items):
        time.sleep(max(0.0, t0 + t - time.time()))
        hwnd = render_window(proc.pid)
        if not hwnd:
            print(f"{t:6.1f}s: no window yet")
            continue
        if keys:
            press(hwnd, keys)
            time.sleep(0.3)
        name = os.path.join(a.out, f"dolphin_{t:05.1f}.png")
        ImageGrab.grab(bbox=client_box(hwnd), all_screens=True).save(name)
        print(f"{t:6.1f}s: {'+'.join(keys) or 'shot'} -> {name}")
    if a.quit is not None:
        time.sleep(max(0.0, t0 + a.quit - time.time()))
    proc.terminate()


if __name__ == "__main__":
    main()
