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

"""Numbered colour bands MASKED to one UV island, over the live livery.

    python tools/probe_bands.py team_l79 out/tpl/lotus 0:X:0:520:25 1:X:40:610:50 0:Y:0:480:40
    python tools/probe_bands.py team_l79 out/tpl/lotus 1:X:40:610:50 line:1,10:1259 blocks

Each spec is IDX:X|Y:start:stop:step - bands every `step` texels along x (or
y) of island IDX (indices as `tools/probe_islands.py ... list` prints them),
8-colour cycle, each band labelled with its START texel.  `line:I,J,..:ROW`
draws a white 11-texel line along texture row ROW on those islands (a centre
line check); `blocks` paints the build's NUMBER_BLOCKS magenta so the sim's
stamp can be read over them.

Why: `probe_islands.py` answers "which island is this surface"; this answers
"which texel of this island is this point on the surface" - a ruler you can
read from a dead-front, dead-rear or top frame.  Written for the Lotus 79
(2026-09-17): it proved the nose / engine-cover centre row (1259) and found
that the rear wing's rear face is the LOW-x end of the wing island, where a
trailing-edge band drawn on the top surface had been invisible from behind.
The build module must expose build(spec=False), PAINT_DIR, CUSTOMER and
(for `blocks`) NUMBER_BLOCKS.
Any paint file already there is backed up into out/backup/ first.
"""
import importlib, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "src"))
import probe_islands as P
from paintfolder import save_tga


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    B = importlib.import_module(sys.argv[1])
    lab, isl = P.islands(sys.argv[2])
    by = {k: l for k, l, x, y, w, h, a in isl}
    bbox = {k: (x, y, w, h) for k, l, x, y, w, h, a in isl}
    a = np.asarray(B.build(spec=False).convert("RGB")).copy()
    labels = []
    for spec in sys.argv[3:]:
        if spec == "blocks":
            for x, y, w, h in B.NUMBER_BLOCKS.values():
                a[y:y + h, x:x + w] = (255, 0, 255)
            continue
        if spec.startswith("line:"):
            _, idxs, row = spec.split(":")
            m = np.zeros(lab.shape, bool)
            for i in idxs.split(","):
                m |= lab == by[int(i)]
            box = np.zeros_like(m)
            box[int(row) - 5:int(row) + 6, :] = True
            a[box & m] = (255, 255, 255)
            continue
        idx, axis, s0, s1, st = spec.split(":")
        idx, s0, s1, st = int(idx), int(s0), int(s1), int(st)
        m = lab == by[idx]
        bx, byy, bw, bh = bbox[idx]
        for k, v in enumerate(range(s0, s1, st)):
            box = np.zeros_like(m)
            if axis.upper() == "X":
                box[:, v:v + st] = True
                spots = [(v + st // 2, byy + bh // 4), (v + st // 2, byy + 3 * bh // 4)]
            else:
                box[v:v + st, :] = True
                spots = [(bx + bw // 4, v + st // 2), (bx + 3 * bw // 4, v + st // 2)]
            a[box & m] = P.PAL[k % 8]
            labels += [(str(v), sx, sy, st) for sx, sy in spots]
        print("island %d: %s bands %d..%d step %d" % (idx, axis, s0, s1, st))
    img = Image.fromarray(a, "RGB")
    d = ImageDraw.Draw(img)
    for t, cx, cy, st in labels:
        f = ImageFont.truetype(P.FONT, max(11, min(34, int(st * 1.4 / max(1, len(t))))))
        bb = f.getbbox(t)
        d.text((cx - (bb[2] - bb[0]) / 2 - bb[0], cy - (bb[3] - bb[1]) / 2 - bb[1]),
               t, font=f, fill=(0, 0, 0))
    out = os.path.join(B.PAINT_DIR, "car_%s.tga" % B.CUSTOMER)
    save_tga(img, out)
    print("wrote probe to", out, "- rebuild the livery afterwards")


if __name__ == "__main__":
    main()
