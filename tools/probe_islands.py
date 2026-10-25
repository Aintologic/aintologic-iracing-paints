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

"""Labelled-cell probe that paints ONLY inside a real UV island.

    python tools/template_layers.py <zip> out/tpl/ray      # once
    python tools/probe_islands.py team_ray out/tpl/ray list
    python tools/probe_islands.py team_ray out/tpl/ray 4:A:4,2 7:B:3,2 ...

`list` prints every island the template's GREEN wire outlines enclose, sorted
by area, with its index, bbox and centroid.  Each later spec is
INDEX:NAME:cols,rows - the island's bbox is divided into a grid and each cell
is painted **masked to the island**, labelled NAME+n (row-major, 1-based),
with a RED bar on its texture-TOP edge and a BLUE bar on its texture-LEFT
edge (playbook Rule 3).

Why this and not probe_multi: on a car whose UV packs islands inside other
islands' bounding boxes (the RSR's windscreen banner and louvre lips, and the
Ray FF1600 where island 0's bbox swallows two more), a plain rect probe paints
those neighbours too and they render somewhere else entirely.  Masking to the
island makes every painted texel attributable to one island.  Written for the
Ray FF1600, 2026-09-14.

The build module must expose build(spec=False), PAINT_DIR and CUSTOMER.
Read the result from a LEVEL camera (playbook Rule 3a).
Any paint file already there is backed up into out/backup/ first.
"""
import importlib, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
FONT = os.path.join(ROOT, "fonts", "ArchivoBlack-Regular.ttf")
PAL = [(255, 0, 220), (0, 255, 90), (255, 230, 0), (0, 200, 255),
       (255, 120, 0), (255, 255, 255), (150, 0, 255), (0, 255, 220)]
MIN_AREA = 900


def islands(tpl_dir, erode=1):
    """(label image, [(index, label, x, y, w, h, area)]) from Wire.png.

    HPD ARX-01c (2026-09-17): its Wire layer is all white - no green island
    outlines at all - so when the wire has (almost) no green, the islands are
    taken from the template's Mask layer instead: connected components of the
    mask's opaque area, eroded `erode` texels so islands that touch split.
    Same indices / bboxes / masks either way, so every tool built on this
    (probe_bands, island_runs, island_edges, mirror_row) works unchanged."""
    a = np.asarray(Image.open(os.path.join(tpl_dir, "Wire.png"))).astype(int)
    al = a[..., 3] > 40
    green = al & (a[..., 1] > 150) & (a[..., 0] < 120) & (a[..., 2] < 120)
    if green.sum() < 2000:
        m = np.asarray(Image.open(os.path.join(tpl_dir, "Mask.png")).convert("RGBA"))[..., 3] > 0
        # polarity: the HPD's Mask is OPAQUE over the non-paintable background
        # and transparent on the islands.  Whichever state the canvas border is
        # mostly in is the background.
        border = np.concatenate([m[0], m[-1], m[:, 0], m[:, -1]])
        if border.mean() > 0.5:
            m = ~m
        if erode:
            m = ndimage.binary_erosion(m, iterations=erode)
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        rows = []
        for i, sl in enumerate(ndimage.find_objects(lab)):
            if sizes[i] < MIN_AREA:
                continue
            ys, xs = sl
            rows.append((int(sizes[i]), i + 1, xs.start, ys.start,
                         xs.stop - xs.start, ys.stop - ys.start))
        rows.sort(reverse=True)
        return lab, [(k, l, x, y, w, h, area)
                     for k, (area, l, x, y, w, h) in enumerate(rows)]
    lab, n = ndimage.label(~ndimage.binary_dilation(green, iterations=1))
    sizes = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
    rows = []
    for i, sl in enumerate(ndimage.find_objects(lab)):
        if sizes[i] < MIN_AREA:
            continue
        ys, xs = sl
        if xs.start == 0 and ys.start == 0 and xs.stop > 2000 and ys.stop > 2000:
            continue                                  # the background
        rows.append((int(sizes[i]), i + 1, xs.start, ys.start,
                     xs.stop - xs.start, ys.stop - ys.start))
    rows.sort(reverse=True)
    return lab, [(k, l, x, y, w, h, area)
                 for k, (area, l, x, y, w, h) in enumerate(rows)]


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    B = importlib.import_module(sys.argv[1])
    lab, isl = islands(sys.argv[2])
    if sys.argv[3] == "list":
        print("%-4s %6s %6s %6s %6s %9s  %s" % ("idx", "x", "y", "w", "h", "area", "centroid"))
        for k, l, x, y, w, h, area in isl:
            cy, cx = ndimage.center_of_mass(lab == l)
            print("%-4d %6d %6d %6d %6d %9d  (%d,%d)" % (k, x, y, w, h, area, cx, cy))
        return
    # imported here, not at the top: body_mask, island_runs, mirror_row and
    # island_id_mask import this module only for islands()
    from paintfolder import save_tga
    by_idx = {k: (l, x, y, w, h) for k, l, x, y, w, h, a in isl}
    img = B.build(spec=False).convert("RGB")
    a = np.asarray(img).copy()
    labels = []
    ci = 0
    for spec in sys.argv[3:]:
        idx, name, grid = spec.split(":")
        l, x, y, w, h = by_idx[int(idx)]
        cols, rows = map(int, grid.split(","))
        mask = lab == l
        cw, ch = w / float(cols), h / float(rows)
        for r in range(rows):
            for c in range(cols):
                x0, x1 = int(x + c * cw), int(x + (c + 1) * cw)
                y0, y1 = int(y + r * ch), int(y + (r + 1) * ch)
                box = np.zeros_like(mask)
                box[y0:y1, x0:x1] = True
                m = box & mask
                if m.sum() < 60:
                    ci += 1
                    continue
                a[m] = PAL[ci % 8]
                edge = np.zeros_like(mask)
                edge[y0:y0 + max(3, (y1 - y0) // 9), x0:x1] = True
                a[edge & mask] = (255, 0, 0)                  # texture TOP
                edge = np.zeros_like(mask)
                edge[y0:y1, x0:x0 + max(3, (x1 - x0) // 9)] = True
                a[edge & mask] = (0, 0, 255)                  # texture LEFT
                cyc, cxc = ndimage.center_of_mass(m)
                labels.append(("%s%d" % (name, r * cols + c + 1), cxc, cyc,
                               min(x1 - x0, y1 - y0)))
                ci += 1
        print("island %s -> %s %dx%d at (%d,%d,%d,%d)" % (idx, name, cols, rows, x, y, w, h))
    img = Image.fromarray(a, "RGB")
    d = ImageDraw.Draw(img)
    for t, cx, cy, sz in labels:
        fs = max(11, min(int(sz * 0.75), int(sz * 2.2 / max(2, len(t)))))
        f = ImageFont.truetype(FONT, fs)
        bb = f.getbbox(t)
        d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
               t, font=f, fill=(0, 0, 0))
    out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
    save_tga(img, out)
    print("wrote probe to", out)


if __name__ == "__main__":
    main()
