# AÏntologic iRacing paints
# Copyright (C) 2026 AÏntologic
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License
# for more details. You should have received a copy of the GNU Affero General
# Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Reload the paint in iRacing's car viewer, optionally move the camera, and
take a screenshot of the iRacing window.

    python tools/view2.py --out out/viewer/a.png
    python tools/view2.py --no-reload --drag 900 --out out/viewer/b.png
    python tools/view2.py --no-reload --drag-y -600 --out out/viewer/level.png
    python tools/view2.py --no-reload --wheel 4 --out out/viewer/zoom.png

Open the car first (iRacing -> My Content -> View Car -> Car Model), so the 3D
view is on screen. Then this tool, in order:

  1. finds the iRacing window, un-minimises it and brings it to the front. If
     Windows does not really hand it the focus, it STOPS (prints NOFOCUS) - it
     never clicks or types into some other window;
  2. clicks once inside the 3D view so the view has keyboard focus;
  3. unless --no-reload: presses Ctrl+R, waits 2.5 s, presses Ctrl+R again and
     waits 4 s. One reload is not always enough; the second one and the wait
     make sure the screenshot shows the NEW paint, never a stale one;
  4. --drag X / --drag-y Y: drags the camera X px sideways (orbit; 260 is about
     90 degrees) and Y px up or down (pitch; it clamps, so -600 always ends
     level and +600 always top-down);
  5. --wheel N: N mouse-wheel ticks over the car (+ zooms in, - zooms out);
  6. saves a PNG of the whole iRacing window and prints "OK <file> <w>x<h>".
     Without --out it goes to out/viewer/shot.png in the project folder (git
     ignores out/, so nothing in it is ever committed), whichever folder you
     run this from.

The camera stays where it is between runs, so drags add up - and Ctrl+R does
NOT reset it (checked 2026-10-24: a reload leaves the pose exactly as it was).
One drag can be undone with the same drag reversed (--drag -260 after
--drag 260); undoing a whole sweep drifts a degree or two, so re-capture
rather than assume you are back. Windows only; needs Pillow, nothing else.
The process is made DPI-aware, so the click points and the screenshot use the
same real screen pixels even with display scaling.
"""
import argparse
import ctypes
import os
import sys
import time
from ctypes import wintypes

from PIL import ImageGrab

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "out", "viewer")  # default home of every capture

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


def _dpi_aware():
    """Real screen pixels for every coordinate this process sees or sets."""
    try:  # Windows 10 1703+: per-monitor v2
        user32.SetProcessDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        if user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)):
            return
    except AttributeError:
        pass
    try:  # Windows 8.1+: per-monitor
        ctypes.WinDLL("shcore").SetProcessDpiAwareness(2)
        return
    except (AttributeError, OSError):
        pass
    user32.SetProcessDPIAware()


_dpi_aware()

# --- Win32 plumbing ----------------------------------------------------------
ULONG_PTR = ctypes.c_size_t


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD), ("dwExtraInfo", ULONG_PTR)]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD), ("time", wintypes.DWORD),
                ("dwExtraInfo", ULONG_PTR)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD)]


class _INPUTUNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", _INPUTUNION)]


INPUT_MOUSE, INPUT_KEYBOARD = 0, 1
MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP, MOUSEEVENTF_WHEEL = 0x0002, 0x0004, 0x0800
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL, VK_R = 0x11, 0x52
SW_RESTORE = 9
GA_ROOT, GA_ROOTOWNER = 2, 3
GW_OWNER = 4

# Every drag is 30 cursor steps, DRAG_STEP_MS apart, on a fixed clock. 45 ms is
# the real pace of the PowerShell tool this replaces (its "20 ms" pauses took
# ~45 ms each, 1.34 s per drag, measured 2026-10-24); from the same pose its
# 260 px drag and this one gave pixel-identical frames, so the calibrations in
# the car maps (260 px is ~90 degrees) still hold. A 20 ms pace landed within a
# fraction of a degree of it - speed barely matters, but matching it costs 0.7 s.
DRAG_STEP_MS = 45
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsIconic.argtypes = [wintypes.HWND]
user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.GetForegroundWindow.restype = wintypes.HWND
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.WindowFromPoint.argtypes = [wintypes.POINT]
user32.WindowFromPoint.restype = wintypes.HWND
user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetAncestor.restype = wintypes.HWND
user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetWindow.restype = wintypes.HWND
user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
user32.SendInput.argtypes = [wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = wintypes.UINT
user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]
user32.MapVirtualKeyW.restype = wintypes.UINT
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                                wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]


class ViewerError(Exception):
    """Raised with the one-word status the old tool printed (NOWINDOW, NOFOCUS...)."""


def _sleep_ms(ms):
    time.sleep(ms / 1000.0)


def _send(*inputs):
    arr = (INPUT * len(inputs))(*inputs)
    if user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT)) != len(inputs):
        raise ViewerError("NOINPUT")


def _mouse(flags, data=0):
    return INPUT(type=INPUT_MOUSE,
                 u=_INPUTUNION(mi=MOUSEINPUT(0, 0, data & 0xFFFFFFFF, flags, 0, 0)))


def _key(vk, up=False):
    return INPUT(type=INPUT_KEYBOARD,
                 u=_INPUTUNION(ki=KEYBDINPUT(vk, user32.MapVirtualKeyW(vk, 0),
                                             KEYEVENTF_KEYUP if up else 0, 0, 0)))


def _exe_name(hwnd):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not h:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(1024)
        n = wintypes.DWORD(len(buf))
        if not kernel32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            return ""
        return os.path.basename(buf.value)
    finally:
        kernel32.CloseHandle(h)


def find_window():
    """The iRacing UI window (the one the car viewer lives in), or None.

    Only main windows of an iRacing program count, so a browser tab or a folder
    whose title happens to contain "iRacing" is never picked, nor a pop-up."""
    found = []

    def cb(hwnd, _):
        if user32.IsWindowVisible(hwnd) and not user32.GetWindow(hwnd, GW_OWNER):
            n = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(n + 1)
            user32.GetWindowTextW(hwnd, buf, n + 1)
            if "iracing" in buf.value.lower():
                exe = _exe_name(hwnd).lower()
                if exe.startswith("iracing"):
                    found.append((exe != "iracingui.exe", hwnd))
        return True

    user32.EnumWindows(WNDENUMPROC(cb), 0)
    # iRacingUI.exe first; otherwise the topmost iRacing window (stable sort)
    return sorted(found, key=lambda f: f[0])[0][1] if found else None


def _owns(hwnd, x, y):
    """True when the point (x, y) shows hwnd, not a window lying on top of it."""
    at = user32.WindowFromPoint(wintypes.POINT(x, y))
    return bool(at) and hwnd in (user32.GetAncestor(at, GA_ROOT),
                                 user32.GetAncestor(at, GA_ROOTOWNER))


def focus(hwnd, tries=6):
    """Bring hwnd to the front and confirm Windows really gave it the focus."""
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, SW_RESTORE)
        _sleep_ms(800)
    for _ in range(tries):
        user32.SetForegroundWindow(hwnd)
        _sleep_ms(400)
        if user32.GetForegroundWindow() == hwnd:
            return
        # Windows refuses a plain SetForegroundWindow from a background
        # process; joining the current foreground thread's input lifts that.
        fg = user32.GetForegroundWindow()
        other = user32.GetWindowThreadProcessId(fg, None) if fg else 0
        mine = kernel32.GetCurrentThreadId()
        if other and other != mine and user32.AttachThreadInput(mine, other, True):
            try:
                user32.BringWindowToTop(hwnd)
                user32.SetForegroundWindow(hwnd)
            finally:
                user32.AttachThreadInput(mine, other, False)
            _sleep_ms(400)
            if user32.GetForegroundWindow() == hwnd:
                return
    raise ViewerError("NOFOCUS")


def _click(hwnd, x, y):
    if not _owns(hwnd, x, y):
        raise ViewerError("COVERED")
    user32.SetCursorPos(x, y)
    _sleep_ms(200)
    _send(_mouse(MOUSEEVENTF_LEFTDOWN))
    _sleep_ms(80)
    _send(_mouse(MOUSEEVENTF_LEFTUP))
    _sleep_ms(400)


def _reload(hwnd):
    for wait in (2500, 4000):
        if user32.GetForegroundWindow() != hwnd:
            raise ViewerError("NOFOCUS")
        _send(_key(VK_CONTROL), _key(VK_R), _key(VK_R, up=True), _key(VK_CONTROL, up=True))
        _sleep_ms(wait)


def _drag(hwnd, x, y, dx, dy):
    if not _owns(hwnd, x, y):
        raise ViewerError("COVERED")
    user32.SetCursorPos(x, y)
    _sleep_ms(250)
    _send(_mouse(MOUSEEVENTF_LEFTDOWN))
    _sleep_ms(200)
    try:
        t0 = time.perf_counter()
        for i in range(1, 31):
            user32.SetCursorPos(x + round(dx * i / 30), y + round(dy * i / 30))
            # on a fixed clock, so one slow step does not slow the whole drag
            time.sleep(max(0.0, t0 + i * DRAG_STEP_MS / 1000.0 - time.perf_counter()))
        _sleep_ms(150)
    finally:
        _send(_mouse(MOUSEEVENTF_LEFTUP))
    _sleep_ms(1200)


def _wheel(hwnd, x, y, ticks):
    if not _owns(hwnd, x, y):
        raise ViewerError("COVERED")
    user32.SetCursorPos(x - 4, y)  # a small hover so the view sees the mouse
    _sleep_ms(150)
    user32.SetCursorPos(x, y)
    _sleep_ms(250)
    for _ in range(abs(ticks)):
        _send(_mouse(MOUSEEVENTF_WHEEL, 120 if ticks > 0 else -120))
        _sleep_ms(350)
    _sleep_ms(800)


def capture(out, drag=0, drag_y=0, reload=True, wheel=0):
    """Focus iRacing, click into the 3D view, reload twice unless told not to,
    drag/zoom, then save the window to `out`. Returns (out, width, height);
    raises ViewerError("NOWINDOW" / "NOFOCUS" / "COVERED" / "NOINPUT")."""
    hwnd = find_window()
    if not hwnd:
        raise ViewerError("NOWINDOW")
    focus(hwnd)
    r = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(r))
    w, h = r.right - r.left, r.bottom - r.top
    # the same point the PowerShell tool used: 45% across, 42% down the window
    cx, cy = r.left + round(w * 0.45), r.top + round(h * 0.42)
    _click(hwnd, cx, cy)  # click once inside the viewer so it has keyboard focus
    if reload:
        _reload(hwnd)
    if drag or drag_y:
        _drag(hwnd, cx, cy, drag, drag_y)
    if wheel:
        _wheel(hwnd, cx, cy, wheel)
    if user32.GetForegroundWindow() != hwnd:
        raise ViewerError("NOFOCUS")
    shot = ImageGrab.grab(bbox=(r.left, r.top, r.right, r.bottom), all_screens=True)
    folder = os.path.dirname(os.path.abspath(out))
    os.makedirs(folder, exist_ok=True)
    shot.save(out, "PNG")
    return out, w, h


EXPLAIN = {
    "NOWINDOW": "iRacing is not running (no iRacing window found).",
    "NOFOCUS": "Windows would not bring iRacing to the front, so nothing was "
               "clicked or typed. Click the iRacing window once and run it again.",
    "COVERED": "another window is lying over the car view; move it away and run it again.",
    "NOINPUT": "Windows blocked the simulated mouse/keyboard input.",
}


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Reload the paint in iRacing's car viewer and take a screenshot.")
    ap.add_argument("--out", default=os.path.join(OUT_DIR, "shot.png"),
                    help="where to save the PNG (default: %(default)s)")
    ap.add_argument("--drag", type=int, default=0,
                    help="drag the camera this many px sideways (260 is ~90 degrees)")
    ap.add_argument("--drag-y", type=int, default=0,
                    help="drag the camera this many px up/down (-600 level, +600 top-down)")
    ap.add_argument("--wheel", type=int, default=0,
                    help="mouse-wheel ticks over the car (+ zooms in, - zooms out)")
    ap.add_argument("--no-reload", action="store_true",
                    help="do not press Ctrl+R (just move the camera and capture)")
    a = ap.parse_args(argv)
    try:
        out, w, h = capture(a.out, a.drag, a.drag_y, not a.no_reload, a.wheel)
    except ViewerError as e:
        print(e.args[0])
        print(EXPLAIN.get(e.args[0], ""), file=sys.stderr)
        return 1
    print("OK %s %dx%d" % (out, w, h))
    return 0


if __name__ == "__main__":
    sys.exit(main())
