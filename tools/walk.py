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

"""Walk the camera around the car in iRacing's car viewer and save every frame.

    python tools/walk.py --prefix out/viewer/w_ --step 65 --frames 12 --drag-y -600
    python tools/walk.py --prefix out/viewer/w_ --reload --drag-y -600

Frame 0 is captured where the camera is (after --drag-y: -600 = level, +600 =
top-down; --reload first reloads the paint - it does NOT move the camera).
Every following frame first drags the camera --step px sideways, so the walk
ends (frames - 1) x step px round from where it started. Each frame is one
tools/view2.py capture, with all its safety checks.

Writes <prefix><i>.png (the whole iRacing window) and <prefix><i>.jpg (just the
3D view, cropped PROPORTIONALLY - the iRacing window changes size). Tile the
.jpg frames into one sheet with tools/contact_sheet.py. Without --prefix they
go to out/viewer/ in the project folder (w_0.png, w_0.jpg, ...; git ignores
out/, so nothing in it is ever committed), whichever folder you run this from.

F4 lesson (2026-09-14): with a 1728-px-wide window 65 px is ~30 deg on average
but non-linear - sweep 12 frames and pick, never assume a pose. A frame takes
about 5 s, so 12 frames is just over a minute (65 s with --reload, measured
2026-10-24); if your tool bridge cuts calls off at ~60 s, run it in the
background and wait for its "DONE" line, or split the walk.
"""
import argparse
import os
import sys

from PIL import Image

import view2

# the 3D view inside the window, as fractions: left, top, width, height
CROP = (0.03, 0.18, 0.94, 0.69)


def crop_pane(png, jpg, crop):
    """Cut the 3D view out of a window capture, by proportion of its size."""
    with Image.open(png) as im:
        w, h = im.size
        x, y = round(w * crop[0]), round(h * crop[1])
        box = (x, y, x + round(w * crop[2]), y + round(h * crop[3]))
        im.convert("RGB").crop(box).save(jpg, "JPEG", quality=75)


def sweep(prefix, step, frames, drag_y=0, reload=False, crop=CROP):
    """Capture `frames` frames `step` px apart, then crop each one."""
    for i in range(frames):
        out = "%s%d.png" % (prefix, i)
        if i == 0:
            res = view2.capture(out, drag_y=drag_y, reload=reload)
        else:
            res = view2.capture(out, drag=step, reload=False)
        print("OK %s %dx%d" % res, flush=True)
    for i in range(frames):
        crop_pane("%s%d.png" % (prefix, i), "%s%d.jpg" % (prefix, i), crop)
    print("DONE %d frames" % frames)


def run(argv, description, defaults, crop, with_reload):
    """The command line shared by walk.py and walk_top.py."""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("--prefix", default=defaults["prefix"],
                    help="frames are written as <prefix><i>.png/.jpg (default: %(default)s)")
    ap.add_argument("--step", type=int, default=65,
                    help="sideways drag between frames, px (default: %(default)s)")
    ap.add_argument("--frames", "-n", type=int, default=defaults["frames"],
                    help="how many frames (default: %(default)s)")
    ap.add_argument("--drag-y", type=int, default=defaults["drag_y"],
                    help="up/down drag before frame 0: -600 level, +600 top-down "
                         "(default: %(default)s)")
    if with_reload:
        ap.add_argument("--reload", action="store_true",
                        help="reload the paint (Ctrl+R twice) before frame 0")
    a = ap.parse_args(argv)
    try:
        sweep(a.prefix, a.step, a.frames, a.drag_y,
              getattr(a, "reload", False), crop)
    except view2.ViewerError as e:
        print(e.args[0])
        print(view2.EXPLAIN.get(e.args[0], ""), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(run(None, "Walk the camera around the car and save every frame.",
                 {"prefix": os.path.join(view2.OUT_DIR, "w_"), "frames": 12,
                  "drag_y": 0},
                 CROP, with_reload=True))
