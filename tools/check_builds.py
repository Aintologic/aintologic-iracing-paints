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

"""Build the measured cars and check each one matches its ready-made paint.

    python tools/check_builds.py                 # every car this computer can build
    python tools/check_builds.py --all           # all ten; a car that can't be built fails
    python tools/check_builds.py --only lotus-79 --only porsche-911-rsr
    python tools/check_builds.py --keep          # keep the built files in out/check-builds
    python tools/check_builds.py --no-designs    # skip the design check (below)
    python tools/check_builds.py --paints DIR    # compare with DIR/<car>/ instead of paints/

Why: the ready-made paints in paints/ are what people download. Each one must
be exactly what the code makes with its default settings, so anyone can make
the same file themselves and trust it. This builds each car with its defaults,
in a fresh Python, and compares both files it makes, car_CUSTOMERID.tga and
car_spec_CUSTOMERID.tga, with the ones in paints/<car>/, byte for byte (by
SHA-256 hash).

Then the design check: every car it built is built again once with each
sample design in examples/designs/ (the --design settings files).
example-scheme.json writes the example design out in full, so it must make
exactly the same two files as the default build. Every other sample must
build without an error, make the same two files, and make a different paint
from the default one; a paint that comes out unchanged means the car's
builder is not reading the design. The design check compares builds made on
this computer with each other, so the Pillow and numpy versions don't matter
to it. Add --no-designs to skip it.

Six cars need their one-time setup step first (tools/first_run.py), which
reads iRacing's own paint template for the car. iRacing's templates can't be
published, so on a computer without them, such as GitHub's, those six are
skipped, and it says so. Before every release they are checked on a computer
that has the templates, with --all.

Byte for byte also means the same versions of Pillow and numpy: the
ready-made paints were made with the versions in tools/requirements-checks.txt.
Other versions can change a few pixels.

It writes only under out/check-builds/, and removes what it built there when it
finishes unless you add --keep. It never connects to the internet. Exit code:
0 when every car it built matches and passes the design check; 1 when any
differs, fails to build (or, with --all, can't be built here) or fails the
design check; 2 for a mistake in the options.
"""
import argparse
import glob
import hashlib
import os
import platform
import re
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True      # write nothing outside out/check-builds

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.join(ROOT, "out", "check-builds")
PINS = os.path.join(ROOT, "tools", "requirements-checks.txt")
sys.path.insert(0, os.path.join(ROOT, "src"))
import setup_check                  # noqa: E402  standard library only

FILES = ["car_CUSTOMERID.tga", "car_spec_CUSTOMERID.tga"]
SHOWN = {"pillow": "Pillow", "numpy": "numpy"}
DESIGNS = os.path.join(ROOT, "examples", "designs")
EXAMPLE_DESIGN = "example-scheme.json"     # the example design written out: same as no design

# car (its folder in paints/) -> builder in src/, and its one-time setup step
# (a key in src/setup_check.py) or None when it needs none
CARS = [
    ("mx5-2016-global-cup", "team_mx5", None),
    ("fia-f4", "team_f4", "f4"),
    ("porsche-911-rsr", "team_rsr", None),
    ("ray-ff1600", "team_ray", "ray"),
    ("ferrari-296-challenge", "team_f296c", None),
    ("lotus-79", "team_l79", None),
    ("hpd-arx-01c", "team_hpd", "hpd"),
    ("spec-racer-ford", "team_srf", "srf"),
    ("skip-barber-formula-2000", "team_sbf2000", "sbf2000"),
    ("aston-martin-vantage-gt3-evo", "team_amv", "amv"),
]

SKIP_REASON = ("needs the one-time setup step, which reads iRacing's own template; "
               "checked on a computer with the templates before every release")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pins():
    """{add-on: exact version} from tools/requirements-checks.txt."""
    found = {}
    try:
        with open(PINS, encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"\s*([A-Za-z0-9._-]+)\s*==\s*([0-9][0-9A-Za-z.]*)", line.split("#", 1)[0])
                if m:
                    found[m.group(1).lower()] = m.group(2)
    except OSError:
        pass
    return found


def versions():
    """{'python', 'pillow', 'numpy', 'freetype'}: what this computer has (None if missing)."""
    from importlib import metadata
    have = {"python": platform.python_version()}
    for name in ("pillow", "numpy"):
        try:
            have[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            have[name] = None
    try:
        from PIL import features
        have["freetype"] = features.version("freetype2")
    except Exception:           # Pillow missing or built without FreeType
        have["freetype"] = None
    return have


def build(slug, builder, design=None):
    """Run one builder with its defaults, or with one sample design (its file
    name in examples/designs/). Returns (problem or None, folder)."""
    name = slug if design is None else "%s--%s" % (slug, design[:-5])
    rel_out = "out/check-builds/" + name
    folder = os.path.join(WORK, name)
    if os.path.isdir(folder):
        shutil.rmtree(folder)       # an earlier run's files must not count
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    cmd = [sys.executable, "-B", "src/%s.py" % builder, "--out", rel_out]
    if design is not None:
        cmd += ["--design", "examples/designs/" + design]
    try:
        r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, errors="replace",
                           env=env, timeout=900)
    except subprocess.TimeoutExpired:
        return "the build took longer than 15 minutes and was stopped", folder
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-4:]
        indent = " " * 13
        return "the build stopped with an error:\n" + "\n".join(indent + l for l in tail), folder
    made = sorted(os.listdir(folder)) if os.path.isdir(folder) else []
    if made != sorted(FILES):
        return ("the build should make exactly %s, but made: %s"
                % (" and ".join(FILES), ", ".join(made) or "nothing")), folder
    return None, folder


def samples():
    """The sample design files in examples/designs/, example-scheme.json first."""
    names = [os.path.basename(p) for p in glob.glob(os.path.join(DESIGNS, "*.json"))]
    return sorted(names, key=lambda n: (n != EXAMPLE_DESIGN, n))


def check_designs(slug, builder, default, designs, tally, built):
    """Build one car once with each sample design and compare each build with
    the car's default build, made a moment ago in the folder default."""
    want = {name: sha256(os.path.join(default, name)) for name in FILES}
    for design in designs:
        problem, folder = build(slug, builder, design)
        built.append(folder)
        label = "design " + design
        if problem:
            print("  FAILED     %s: %s" % (label, problem))
            tally["design failed"] += 1
            continue
        changed = [n for n in FILES if sha256(os.path.join(folder, n)) != want[n]]
        if design == EXAMPLE_DESIGN:
            if changed:
                print("  CHANGED    %s: should make exactly the default paint, but %s differ%s"
                      % (label, " and ".join(changed), "" if len(changed) > 1 else "s"))
                tally["design wrong"] += 1
            else:
                print("  OK         %s: the same as the default build, as it should be" % label)
                tally["design ok"] += 1
        elif changed:
            print("  OK         %s: builds, and differs from the default build" % label)
            tally["design ok"] += 1
        else:
            print("  IGNORED    %s: makes exactly the default paint, so the builder isn't "
                  "reading the design" % label)
            tally["design wrong"] += 1


def main(argv=None):
    try:
        sys.stdout.reconfigure(errors="backslashreplace", line_buffering=True)
    except (AttributeError, ValueError):
        pass
    slugs = [c[0] for c in CARS]
    ap = argparse.ArgumentParser(
        description="Build each measured car with its default settings and check that both "
                    "files match its ready-made paint in paints/ byte for byte. Then build "
                    "each one again with every sample design in examples/designs/ and check "
                    "that the car reads it.",
        epilog="Cars that need the one-time setup step are skipped when its files aren't "
               "here, unless --all is given. Writes only under out/check-builds. Exit code 0 "
               "when every car built matches and passes the design check, 1 otherwise, 2 for "
               "a mistake in the options.")
    ap.add_argument("--all", action="store_true",
                    help="check all ten cars: a car whose setup step hasn't been run here is a "
                         "failure instead of skipped (use this before a release, on a computer "
                         "with the templates)")
    ap.add_argument("--only", action="append", default=[], metavar="CAR",
                    help="check only this car, by its folder name in paints/ (can be given "
                         "more than once): " + ", ".join(slugs))
    ap.add_argument("--keep", action="store_true",
                    help="keep the built files in out/check-builds instead of removing them")
    ap.add_argument("--no-designs", action="store_true",
                    help="skip the design check (building each car with the sample designs "
                         "in examples/designs/)")
    ap.add_argument("--paints", default=None, metavar="DIR",
                    help="compare with the ready-made paints in DIR/<car>/ instead of paints/ "
                         "in the project folder")
    args = ap.parse_args(argv)
    unknown = [s for s in args.only if s not in slugs]
    if unknown:
        ap.error("unknown car %s; the cars are: %s" % (", ".join(unknown), ", ".join(slugs)))
    if args.paints is not None and not os.path.isdir(args.paints):
        ap.error("--paints: there is no folder %s" % args.paints)
    paints = os.path.abspath(args.paints) if args.paints else os.path.join(ROOT, "paints")
    shown = args.paints.replace("\\", "/").rstrip("/") if args.paints else "paints"
    cars = [c for c in CARS if not args.only or c[0] in args.only]
    designs = [] if args.no_designs else samples()

    have = versions()
    print("Build check: %d car%s, %s" % (len(cars), "" if len(cars) == 1 else "s",
                                        "all required (--all)" if args.all else
                                        "skipping any that need the setup step"))
    if args.paints:
        print("Comparing with the paints in %s/" % shown)
    if args.no_designs:
        print("Design check: skipped (--no-designs)")
    elif designs:
        print("Design check: each car built again with the %d sample design%s in "
              "examples/designs/" % (len(designs), "" if len(designs) == 1 else "s"))
    else:
        print("Design check: there are no sample designs in examples/designs/, so nothing "
              "to check")
    print()
    tally = {"match": 0, "skipped": 0, "different": 0, "failed": 0, "no setup": 0,
             "design ok": 0, "design wrong": 0, "design failed": 0}
    out_existed = os.path.isdir(os.path.dirname(WORK))
    built = []
    for slug, builder, setup_key in cars:
        print("%s  (src/%s.py)" % (slug, builder))
        gone = setup_check.missing(setup_key) if setup_key else []
        if gone:
            if args.all:
                print("  FAILED     its one-time setup step hasn't been run here (missing: %s)"
                      % ", ".join(gone))
                tally["no setup"] += 1
            else:
                print("  SKIPPED    " + SKIP_REASON)
                tally["skipped"] += 1
            continue
        problem, folder = build(slug, builder)
        built.append(folder)
        if problem:
            print("  FAILED     " + problem)
            tally["failed"] += 1
            continue
        same = True
        for name in FILES:
            shipped = os.path.join(paints, slug, name)
            if not os.path.isfile(shipped):
                print("  DIFFERENT  %s  (%s/%s/ has no %s)" % (name, shown, slug, name))
                same = False
            elif sha256(shipped) == sha256(os.path.join(folder, name)):
                print("  MATCH      " + name)
            else:
                print("  DIFFERENT  " + name)
                same = False
        tally["match" if same else "different"] += 1
        if designs:
            check_designs(slug, builder, folder, designs, tally, built)

    if not args.keep:
        for folder in built:
            shutil.rmtree(folder, ignore_errors=True)
        for folder in (WORK, os.path.dirname(WORK) if not out_existed else None):
            try:
                if folder:
                    os.rmdir(folder)    # only when nothing else is in it
            except OSError:
                pass

    print()
    print("Summary: %d match, %d skipped, %d different, %d failed."
          % (tally["match"], tally["skipped"], tally["different"],
             tally["failed"] + tally["no setup"]))
    checked = tally["design ok"] + tally["design wrong"] + tally["design failed"]
    if checked:
        print("Design check: %d sample-design build%s right, %d wrong, %d failed."
              % (tally["design ok"], "" if tally["design ok"] == 1 else "s",
                 tally["design wrong"], tally["design failed"]))
    print("Versions: Python %s, Pillow %s, numpy %s (FreeType %s), on %s."
          % (have["python"], have["pillow"] or "not installed", have["numpy"] or "not installed",
             have["freetype"] or "unknown", platform.system() or "an unknown system"))
    if args.keep and built:
        print("The built files are in out/check-builds/ (a car built with a sample design "
              "is in <car>--<design>/).")
    print()
    if tally["different"]:
        wanted = pins()
        off = ["%s %s (the paints were made with %s)"
               % (SHOWN.get(n, n), have.get(n) or "missing", v)
               for n, v in sorted(wanted.items()) if have.get(n) != v]
        if off:
            print("Note: this computer has " + "; ".join(off) + ". Other versions of Pillow and "
                  "numpy can change a few pixels, so the difference may come from that rather "
                  "than from the code. tools/requirements-checks.txt lists the exact versions.")
        else:
            print("Note: Pillow and numpy are the versions the paints were made with, so the "
                  "difference comes from the code or the files it reads.")
        print()
    if tally["failed"] and not (have["pillow"] and have["numpy"]):
        print("Note: Pillow or numpy isn't installed here, so the builders can't run. "
              "tools/requirements-checks.txt lists the versions the paints were made with.")
        print()
    if tally["different"]:
        print("Result: not every car matches its ready-made paint. A paint that is meant to "
              "change must be updated in paints/ in the same change.")
        return 1
    if tally["failed"]:
        print("Result: %d car%s didn't build. The error is shown under the car's name."
              % (tally["failed"], "" if tally["failed"] == 1 else "s"))
        return 1
    bad = tally["design wrong"] + tally["design failed"]
    if bad:
        print("Result: %d build%s with a sample design went wrong; each is shown under its "
              "car's name. example-scheme.json must make exactly the default paint, and every "
              "other sample design must build and make a different one."
              % (bad, "" if bad == 1 else "s"))
        return 1
    if tally["no setup"]:
        print("Result: %d car%s couldn't be built here because the one-time setup step hasn't "
              "been run (tools/first_run.py). --all needs every car; run it on a computer "
              "with the templates." % (tally["no setup"], "" if tally["no setup"] == 1 else "s"))
        return 1
    if tally["match"] == 0:
        print("Result: nothing was built here (every car checked needs the setup step).")
        return 0
    if checked:
        print("Result: every car built here matches its ready-made paint, byte for byte, and "
              "passes the design check.")
    else:
        print("Result: every car built here matches its ready-made paint, byte for byte.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
