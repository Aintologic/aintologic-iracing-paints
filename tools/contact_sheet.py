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

"""Tile the numbered frames of a tools/walk.py sweep into one labelled sheet.

    python tools/contact_sheet.py out/viewer/w_ 12 out/viewer/w_sheet.jpg [cols] [tile_width]

Reads <prefix><i>.jpg for i in 0..N-1, stamps the frame number on each tile
(so a frame can be named when picking the level side / dead front / top),
and writes one JPEG.  Companion of walk.py; tools/sheet.py is the older
variant that takes explicit file names and crops by box.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

if len(sys.argv) < 4:
    sys.exit(__doc__)
pre, n, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
tw = int(sys.argv[5]) if len(sys.argv) > 5 else 480
FONT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fonts", "ArchivoBlack-Regular.ttf")
ims = [Image.open("%s%d.jpg" % (pre, i)).convert("RGB") for i in range(n)]
th = int(ims[0].height * tw / ims[0].width)
rows = (n + cols - 1) // cols
sheet = Image.new("RGB", (tw * cols, th * rows), (30, 30, 30))
f = ImageFont.truetype(FONT, 28)
for i, im in enumerate(ims):
    t = im.resize((tw, th), Image.LANCZOS)
    ImageDraw.Draw(t).text((8, 4), str(i), font=f, fill=(255, 0, 0))
    sheet.paste(t, ((i % cols) * tw, (i // cols) * th))
sheet.save(out, quality=85)
print("wrote", out, sheet.size)
