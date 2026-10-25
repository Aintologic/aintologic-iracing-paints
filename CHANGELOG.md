# Change log

What changed in each version of iRacing Paints, newest first. How the version
numbers work is explained in the README's [Versions](README.md#versions)
section.

## 0.1.0 (2026-10-25)

The first public preview. It covers everything the project offers today. The
tools and the ten ready-made paints work, but the project isn't finished, and
things may still change from one version to the next.

Version 1.0.0 will come when a newcomer can choose their own colors and
design, paint a car the project hasn't measured yet by following a plain
start-to-finish guide, get started from a guide written for people who don't
code, and work with the AI like a paint shop: a design brief, a mock-up to
approve or change, then the finished paint.

### What's in it

- **Tools that measure and paint any iRacing car.** They read the panel
  outlines from iRacing's own paint template for a car and check them in
  iRacing's car viewer, so stripes, names and logos land in the right place on
  both sides. They aren't tied to a fixed list of cars.
- **Ten measured cars with ready-made paints.** Formula cars, a prototype, GT
  cars, a sports racer and a road-based cup car, picked as worked examples.
  Each one has a ready-made paint in the example design in `paints/`, with a
  blank name strip and "YOUR LOGO" in both logo spots.
- **Your own name and two logos** on the example design, on any measured car,
  with the files named for your iRacing customer ID.
- **Plain-language instructions for AI assistants** in
  [`AGENTS.md`](AGENTS.md), so you can read exactly what the AI is told.
- **A plain message when the one-time setup step is skipped.** Six cars need a
  short setup step that reads your own copy of the car's iRacing template. If
  it hasn't been done, the build stops and tells you which files are missing
  and the exact command to run, instead of failing with a Python error.
- **Logos fitted to their spot.** A logo taller than its spot is shrunk to fit
  inside it, keeping its shape, instead of running off the panel. This applies
  to every car.
- **Viewer tools in Python.** The tools that drive iRacing's car viewer used to
  be PowerShell scripts, and running them meant telling Windows to skip a
  safety check each time. They are Python now, like the rest of the project,
  and nothing asks you to skip that check.

### Known issues

- `tools/contact.py` keeps its working pictures in a `scratch\contact` folder
  under whichever folder you run it from, instead of in the project's `out`
  folder, which is never uploaded.
  ([#15](https://github.com/Aintologic/aintologic-iracing-paints/issues/15))
- Two lines in the guides are out of date: the Skip Barber car map says a
  reload can reset the viewer's camera (it doesn't), and `AGENTS.md` doesn't
  say plainly that screenshots and check pictures belong in the `out` folder.
  ([#16](https://github.com/Aintologic/aintologic-iracing-paints/issues/16))
- Choosing your own colors isn't in yet. Every car carries the example black,
  papaya and white design.
  ([#5](https://github.com/Aintologic/aintologic-iracing-paints/issues/5))
