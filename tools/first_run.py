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

Then build the car as usual, e.g.  python src/team_f4.py --id <id>

It first extracts the template's layers with tools/template_layers.py (needs
psd-tools, numpy, scipy, Pillow), then runs the per-car extractors below. The
island indices are the ones tools/probe_islands.py prints for the reference
templates; if iRacing has repacked a template, confirm them (see
docs/REGENERATING-GEOMETRY.md and the car's docs/car-maps/ entry).

The extracted layers are working files made from iRacing's template: they go
in out/setup/<car> under --root (git ignores out/, so nothing in it is ever
committed) and that folder is deleted at the end, even when a step fails,
unless --keep-tpl. --tpl puts them in a folder of your choice instead; then
only the files this run added to it are deleted.
"""
import argparse
import os
import shutil
import subprocess
import sys
import zipfile

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
    ap.add_argument("--tpl", default=None, help="extracted-template folder (default: <root>/out/setup/<car>)")
    ap.add_argument("--keep-tpl", action="store_true", help="keep the extracted template folder")
    ap.add_argument("--any-name", action="store_true",
                    help="use the zip even if its name doesn't start with this car's ID")
    a = ap.parse_args()

    car = ALIASES.get(a.car, a.car)
    if car not in RECIPES:
        sys.exit("unknown car %r; choose one of: %s" % (a.car, ", ".join(sorted(RECIPES))))
    if not os.path.isfile(a.template):
        sys.exit("no such template zip: %s" % a.template)
    hint, steps = RECIPES[car]
    name = os.path.basename(a.template)
    if name.split("_")[0] != hint.split("_")[0] and not a.any_name:
        sys.exit("This doesn't look like the template for this car: the %s setup needs\n"
                 "%s (car #%s), and this file is %s. Nothing was changed.\n"
                 "Using another car's template is the most expensive mistake in this\n"
                 "project. If you're sure it's the right one, run again with --any-name."
                 % (car, hint, hint.split("_")[0], name))
    if not zipfile.is_zipfile(a.template):
        sys.exit("%s isn't a complete zip file: download the template again\n"
                 "(templates/README.md says how). Nothing was changed." % name)

    root = os.path.abspath(a.root)
    own = not a.tpl                 # our own working folder: always cleaned up
    tpl = os.path.abspath(a.tpl) if a.tpl else os.path.join(root, "out", "setup", car)
    existed = os.path.isdir(tpl)
    before = set(os.listdir(tpl)) if existed and not own else set()
    os.makedirs(tpl, exist_ok=True)
    try:
        written = _regenerate(a, root, tpl, steps)
    finally:                        # on success and on failure alike
        if a.keep_tpl:
            print("kept the unpacked template in %s - it is iRacing's; delete it "
                  "when you're done" % tpl)
        else:
            _clean(tpl, own, existed, before)

    print("\nOK - regenerated %d file(s) for %s:" % (len(written), car))
    for w in written:
        print("    " + w)
    print("now build it, e.g.  python src/team_%s.py --id <id>   (the files go to "
          "out/ in the project folder)"
          % {"f4": "f4", "ray": "ray", "hpd": "hpd", "srf": "srf",
             "sbf2000": "sbf2000", "amv": "amv"}[car])


def _clean(tpl, own, existed, before):
    """Delete the unpacked template: all of our own working folder, but only
    what this run added to a folder the user chose with --tpl."""
    if own:
        shutil.rmtree(tpl, ignore_errors=True)
        return
    for name in set(os.listdir(tpl)) - before:
        p = os.path.join(tpl, name)
        if os.path.isdir(p):
            shutil.rmtree(p, ignore_errors=True)
        else:
            try:
                os.remove(p)
            except OSError:
                pass
    if not existed and not os.listdir(tpl):
        os.rmdir(tpl)


def _regenerate(a, root, tpl, steps):
    """Unpack the template into `tpl`, run the car's extractors, and return
    the files written (paths relative to `root`)."""
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
    return written


if __name__ == "__main__":
    main()
