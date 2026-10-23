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

"""One command to regenerate a car's template-derived geometry from your own
iRacing template, so the six template-geometry cars can be built from source.

    python tools/first_run.py <car> <your-template.zip> [--root DIR] [--tpl DIR] [--keep-tpl]

<car> is one of: f4 / ray / hpd / srf / sbf2000 / amv  (the full slugs work too).
The template zip is iRacing's and is not redistributed - download your own for
the car. The generated island-edge and mask files are written where the builder
reads them (under --root, default the repository root):

    f4       -> src/f4_islands.py
    ray      -> src/ray_islands.py
    hpd      -> assets/hpd-body-mask.png
    amv      -> assets/amv-centre-mask.png
    sbf2000  -> assets/sbf2000-centre-mask.png, assets/sbf2000-pod-islands.png
    srf      -> assets/srf-centre-mask.png, assets/srf-side-mask.png, assets/srf-sash-islands.png

Then build the car as usual, e.g.  python src/team_f4.py --id <id> --out .

It first extracts the template's layers with tools/template_layers.py (needs
psd-tools, numpy, scipy, Pillow), then runs the per-car extractors below. The
island indices are the ones tools/probe_islands.py prints for the reference
templates; if iRacing has repacked a template, confirm them (see
docs/REGENERATING-GEOMETRY.md and the car's docs/car-maps/ entry).
"""
import argparse
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)

# car -> (template-zip hint, [ (tool, output-relpath, [extra args]) ... ])
RECIPES = {
    "f4": ("148_template_iR04.zip", [
        ("f4_islands_gen", "src/f4_islands.py", []),
    ]),
    "ray": ("163_template_GR22.zip", [
        ("island_edges", "src/ray_islands.py",
         ["2053", "NOSE_TIP=7", "NOSE=4", "COWL=8", "DECK=20", "FLANK=2",
          "REAR=6", "LOWER=11", "POD=0", "SILL=13"]),
    ]),
    "hpd": ("39_template_ARX.zip", [
        ("body_mask", "assets/hpd-body-mask.png", ["0", "1", "6", "7"]),
    ]),
    "amv": ("206_template_AMGT3.zip", [
        ("body_mask", "assets/amv-centre-mask.png",
         ["3", "5", "14", "4", "6", "leak:1390,940,470,640"]),
    ]),
    "sbf2000": ("1_template_SBRS.zip", [
        ("body_mask", "assets/sbf2000-centre-mask.png",
         ["47", "3", "96", "6", "17", "18"]),
        ("island_id_mask", "assets/sbf2000-pod-islands.png", ["8=8", "5=5"]),
    ]),
    "srf": ("23_template_SRF.zip", [
        ("body_mask", "assets/srf-centre-mask.png", ["5", "10", "4"]),
        ("body_mask", "assets/srf-side-mask.png",
         ["0", "1", "6", "7", "2", "3", "12", "13", "14", "15", "9", "8", "18", "17"]),
        ("island_id_mask", "assets/srf-sash-islands.png", ["1=1", "14=14", "12=12"]),
    ]),
}

# accept the full release slugs too
ALIASES = {
    "fia-f4": "f4", "ray-ff1600": "ray", "hpd-arx-01c": "hpd",
    "spec-racer-ford": "srf", "skip-barber-formula-2000": "sbf2000",
    "aston-martin-vantage-gt3-evo": "amv",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("car", help="f4 / ray / hpd / srf / sbf2000 / amv (or the full slug)")
    ap.add_argument("template", help="your iRacing template .zip for this car")
    ap.add_argument("--root", default=ROOT, help="where to write src/ and assets/ (default: the repo)")
    ap.add_argument("--tpl", default=None, help="extracted-template folder (default: <root>/tpl/<car>)")
    ap.add_argument("--keep-tpl", action="store_true", help="keep the extracted template folder")
    a = ap.parse_args()

    car = ALIASES.get(a.car, a.car)
    if car not in RECIPES:
        sys.exit("unknown car %r; choose one of: %s" % (a.car, ", ".join(sorted(RECIPES))))
    if not os.path.isfile(a.template):
        sys.exit("no such template zip: %s" % a.template)
    hint, steps = RECIPES[car]
    if hint.split("_")[0] not in os.path.basename(a.template):
        print("note: expected a template like %s; got %s (continuing)"
              % (hint, os.path.basename(a.template)))

    root = os.path.abspath(a.root)
    tpl = os.path.abspath(a.tpl) if a.tpl else os.path.join(root, "tpl", car)
    os.makedirs(tpl, exist_ok=True)

    print("extracting template layers -> %s" % tpl)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "template_layers.py"),
                        os.path.abspath(a.template), tpl], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(os.path.join(tpl, "Wire.png")):
        sys.exit("template_layers did not produce Wire.png. Output:\n" + (r.stderr or r.stdout))

    written = []
    for tool, out_rel, extra in steps:
        out_abs = os.path.join(root, out_rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(out_abs), exist_ok=True)
        cmd = [sys.executable, os.path.join(TOOLS, tool + ".py"), tpl, out_abs] + extra
        print("  %s -> %s" % (tool, out_rel))
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.isfile(out_abs):
            sys.exit("%s did not run. Output:\n%s" % (tool, r.stderr or r.stdout))
        written.append(out_rel)

    if not a.keep_tpl:
        import shutil
        shutil.rmtree(tpl, ignore_errors=True)

    print("\nOK - regenerated %d file(s) for %s:" % (len(written), car))
    for w in written:
        print("    " + w)
    print("now build it, e.g.  python src/team_%s.py --id <id> --out ."
          % {"f4": "f4", "ray": "ray", "hpd": "hpd", "srf": "srf",
             "sbf2000": "sbf2000", "amv": "amv"}[car])


if __name__ == "__main__":
    main()
