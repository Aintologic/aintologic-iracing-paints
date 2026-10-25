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

"""Six-angle contact sheet straight out of the iRacing car viewer.

    python tools/contact.py scratch/preview.png [--no-reload] [--step 260]

Drives tools/view2.py: one reload + capture, then five more captures each
after a horizontal drag of --step px (the viewer keeps its orbit between
calls, so the drags accumulate into a walk around the car), then one from a
raised camera.  Crops each capture to the 3D pane and tiles them 3x2.

Used for releases/<car>/<version>/preview.png and for judging a build.
"""
import argparse, os, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIEW = os.path.join(HERE, "view2.py")
TMP = r"scratch\contact"


def shot(out, drag=0, dragy=0, reload=False):
    cmd = [sys.executable, VIEW, "--out", out,
           "--drag=%d" % drag, "--drag-y=%d" % dragy]
    if not reload:
        cmd.append("--no-reload")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if "OK" not in r.stdout:
        sys.exit("viewer capture failed: %s %s" % (r.stdout, r.stderr))
    return Image.open(out).convert("RGB")


def pane(im):
    """The 3D pane inside the Car Info dialog, by proportion of the window."""
    w, h = im.size
    return im.crop((int(w * 0.02), int(h * 0.17), int(w * 0.98), int(h * 0.86)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--step", type=int, default=260)
    ap.add_argument("--no-reload", action="store_true")
    ap.add_argument("--level", action="store_true",
                    help="pitch the camera level first (the viewer clamps: "
                         "--drag-y -600 is always level, +600 always top-down)")
    ap.add_argument("--pre", type=int, default=0,
                    help="horizontal drag before the first frame, to reach "
                         "the side view")
    a = ap.parse_args()
    os.makedirs(TMP, exist_ok=True)
    if a.level or a.pre:
        shot(os.path.join(TMP, "pre.png"), drag=a.pre,
             dragy=(-600 if a.level else 0))
    # MEASURED: a 260px drag is ~90 deg of orbit, so 130 is ~45.  Frames:
    # side, front 3/4, front, far side, rear 3/4, rear.
    s = a.step // 2
    drags = [0, s, s, 2 * s, s, s]
    frames = []
    for i, d in enumerate(drags):
        frames.append(pane(shot(os.path.join(TMP, "%d.png" % i), drag=d,
                                reload=(i == 0 and not a.no_reload))))
    # put the camera back where it started (one more 45 closes the circle)
    shot(os.path.join(TMP, "reset.png"), drag=2 * s)
    tw = 640
    th = int(frames[0].height * tw / frames[0].width)
    sheet = Image.new("RGB", (tw * 3, th * 2), (20, 20, 20))
    for i, f in enumerate(frames):
        sheet.paste(f.resize((tw, th), Image.LANCZOS), ((i % 3) * tw, (i // 3) * th))
    sheet.save(a.out)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
