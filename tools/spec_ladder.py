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

"""Spec-map ladder test.

Stop guessing global values. Paint a stepped ladder of (R,G,B) material values
along both flanks, load it, and read off the car which combination looks right.

Six bands per flank, nose to tail. Both flanks have raw-texture low x at the
NOSE, so band 1 is at the nose on both sides.

  RIGHT flank, B=255 (clear coat on):
    1 (0,0)    2 (0,64)   3 (0,128)  4 (0,255)  5 (128,32) 6 (255,32)
  LEFT flank, B=0 (clear coat off): same R,G pairs.

Channels per the painting tutorial: R = metallic, G = roughness (low = glossy),
B = clear coat.

Any spec map already there is backed up into out/backup/ first.
"""
import os, sys
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))
from paintfolder import save_tga

OUT = os.path.join(os.path.expanduser("~"), "Documents", "iRacing", "paint", "mx5 mx52016", "car_spec_CUSTOMERID.tga")
FLANK_R = (386, 1679, 884, 306)
FLANK_L = (386, 507, 884, 306)
BASE = (0, 128, 128)

PAIRS = [(0, 0), (0, 64), (0, 128), (0, 255), (128, 32), (255, 32)]

img = Image.new("RGB", (2048, 2048), BASE)
d = ImageDraw.Draw(img)
for rect, b in ((FLANK_R, 255), (FLANK_L, 0)):
    x, y, w, h = rect
    bw = w // len(PAIRS)
    for i, (r, g) in enumerate(PAIRS):
        d.rectangle([x + i * bw, y, x + (i + 1) * bw - 1, y + h - 1], fill=(r, g, b))

save_tga(img, OUT)
print("spec ladder ->", OUT)
print("bands nose->tail:", PAIRS)
print("right flank B=255, left flank B=0")
