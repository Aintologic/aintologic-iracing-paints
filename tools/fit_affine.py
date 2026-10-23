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

"""Fit texture -> screen for one UV island from a probe_affine.py capture.

    python tools/fit_affine.py capture.png 1297,600,355,200 5 4 --region x0,y0,x1,y1 [--out fit.json]

Finds each hue-coded cell's centroid inside --region (a box around the
panel in the capture, so tail lights, tyres and the orange stripes are not
mistaken for cells), least-squares fits

    screen_x = a*u + b*v + c
    screen_y = d*u + e*v + f

and prints the residual per cell.  Under ~5 px is a usable fit; a cell with
a large residual is usually partly hidden (an arch, a crease) - drop it by
tightening --region.  Cells with fewer than 300 pixels are ignored.
"""
import sys, json
import numpy as np
from PIL import Image

if len(sys.argv) < 5:
    sys.exit(__doc__)
cap = sys.argv[1]
x0, y0, w, h = map(int, sys.argv[2].split(","))
cols, rows = int(sys.argv[3]), int(sys.argv[4])
outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
im = Image.open(cap).convert("RGB")
hsv = np.asarray(im.convert("HSV")).astype(int)
H, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
if "--region" in sys.argv:
    rx0, ry0, rx1, ry1 = map(int, sys.argv[sys.argv.index("--region") + 1].split(","))
    mask = np.zeros(H.shape, bool); mask[ry0:ry1, rx0:rx1] = True
    V = np.where(mask, V, 0)
N = cols * rows
cw, ch = w // cols, h // rows
tol = max(3, int(255.0 / N / 2.2))
pts_t, pts_s = [], []
for r in range(rows):
    for c in range(cols):
        i = r * cols + c
        hue = int(round(255.0 * i / N))
        dh = np.abs(((H - hue + 128) % 256) - 128)
        ys, xs = np.where((dh <= tol) & (S > 140) & (V > 90))
        if len(xs) < 40:
            continue
        mx, my = np.median(xs), np.median(ys)
        keep = (np.abs(xs - mx) < 60) & (np.abs(ys - my) < 60)
        if keep.sum() < 300:
            continue
        pts_t.append((x0 + c * cw + cw / 2.0, y0 + r * ch + ch / 2.0))
        pts_s.append((xs[keep].mean(), ys[keep].mean()))
        print("cell %2d (%d,%d): tex (%.0f,%.0f) -> screen (%.1f,%.1f)  n=%d"
              % (i, c, r, pts_t[-1][0], pts_t[-1][1], pts_s[-1][0], pts_s[-1][1], keep.sum()))
if len(pts_t) < 4:
    sys.exit("fewer than 4 cells found - widen --region or check the capture")
T = np.array([[u, v, 1.0] for u, v in pts_t]); Sx = np.array(pts_s)
A = np.linalg.lstsq(T, Sx, rcond=None)[0]
err = np.sqrt(((T @ A - Sx) ** 2).sum(axis=1))
print("fit: screen_x = %.4f u + %.4f v + %.2f ; screen_y = %.4f u + %.4f v + %.2f"
      % (A[0, 0], A[1, 0], A[2, 0], A[0, 1], A[1, 1], A[2, 1]))
print("residual px: mean %.1f max %.1f  (%d cells)" % (err.mean(), err.max(), len(err)))
if outp:
    json.dump({"rect": [x0, y0, w, h], "A": A.tolist(),
               "cells": [[t, s] for t, s in zip(pts_t, pts_s)]}, open(outp, "w"), indent=1)
    print("saved", outp)
