# Change log

What changed in each version of iRacing Paints, newest first. How the version
numbers work is explained in the README's [Versions](README.md#versions)
section.

## 0.2.0 (2026-10-25)

Still an early preview. This version is about newcomers: getting started
without writing code, knowing exactly what the tools touch on your computer,
and getting only the files you need. The ready-made paints are unchanged,
byte for byte.

### What's new

- **A getting-started guide,**
  [`docs/GETTING-STARTED.md`](docs/GETTING-STARTED.md), for anyone who has
  never written code. It has three ways in: just the paints (nothing to
  install), a few commands, or an AI assistant. It also says which computers
  work: building a paint works anywhere Python runs, but seeing it in iRacing
  needs a Windows PC. And it shows where the iRacing app keeps your customer
  ID, and where your paint folder is. The menu names were checked in the app,
  and `templates/README.md` now says where to download a car's template.
  ([#3](https://github.com/Aintologic/aintologic-iracing-paints/issues/3))
- **A setup check.** `python tools/check_setup.py` says in plain words what's
  installed and what's missing: Python, the four add-ons, your iRacing paint
  folder, and the one-time setup step for six cars. It only looks. It never
  installs anything; for anything missing, it says what it is and where to
  get it.
  ([#3](https://github.com/Aintologic/aintologic-iracing-paints/issues/3))
- **A trust and safety page,**
  [`docs/TRUST-AND-SAFETY.md`](docs/TRUST-AND-SAFETY.md): what the tools read
  and write, that they never ask for your iRacing login, never connect to the
  internet and never install anything, and what the viewer tools do with your
  mouse.
  ([#4](https://github.com/Aintologic/aintologic-iracing-paints/issues/4))
- **Backups before anything in iRacing's paint folder is replaced.** The
  measuring tools paint test patterns onto a car so its panels can be read in
  the car viewer. They used to replace the file there (`car_CUSTOMERID.tga`)
  without keeping a copy. Now they save it to `out\backup` first, and say
  where it is and how to put it back.
  ([#4](https://github.com/Aintologic/aintologic-iracing-paints/issues/4))
- **A way to report security problems privately,** in
  [`SECURITY.md`](SECURITY.md).
  ([#4](https://github.com/Aintologic/aintologic-iracing-paints/issues/4))

### What changed

- **An MX-5 build now writes two files instead of six.** It used to write
  four extra finish files, `car_spec_<id>_B1.tga` to `_B4.tga`, next to your
  paint. They were left over from choosing the MX-5's finish during
  development and made it hard to tell which file to use. Now it writes only
  the paint and its finish file, like the other nine cars always did. Add
  `--finish-tests` if you want the four test finishes to compare. The paint
  and finish files themselves haven't changed, byte for byte.
  ([#11](https://github.com/Aintologic/aintologic-iracing-paints/issues/11))
- **Working files stay in the `out` folder.** `tools/contact.py` used to keep
  its working pictures in a `scratch\contact` folder under whichever folder
  you ran it from. Now they go to `out\contact` in the project folder (or a
  folder you choose with `--work-dir`). The other viewer tools' screenshots,
  the setup step's unpacked template, and the test paints from
  `src/calibrate.py` moved into `out` the same way. The builders now write to
  the project's `out` folder even when you run them from somewhere else;
  before, they made a new `out` folder wherever you were.
  ([#15](https://github.com/Aintologic/aintologic-iracing-paints/issues/15))
- **`src/calibrate.py` starts again.** It needed a file the project doesn't
  ship, so it stopped with an error before doing anything. It doesn't need
  that file any more.
- **One unusable tool removed.** `tools/extract_band.py` read a picture from
  an early design that was never part of this project, so it couldn't run.
- **The iRacing steps were checked in the app.** The README and the zip's
  `INSTALL.txt` now say where to find your customer ID and how to open the
  car viewer. The old step "make sure custom paints are turned on" is gone:
  the app has no such switch, and the car viewer showed a custom paint
  without one.
- **Three guide corrections.** The Skip Barber car map no longer says a
  reload can reset the viewer's camera (it never does). `AGENTS.md` now says
  plainly that previews, screenshots and check pictures go in the `out`
  folder, which git ignores, so nothing in it is ever committed. It also no
  longer lists the MX-5 logo spot 2 problem, which was fixed in 0.1.0.
  ([#16](https://github.com/Aintologic/aintologic-iracing-paints/issues/16))

### Known issues

- **Measuring a new car doesn't work as the guides describe yet.** The
  measuring tools save their test pattern as `car_CUSTOMERID.tga`, a name
  iRacing doesn't load, so the car viewer keeps showing the old paint. They
  also look for iRacing's paint folder only under the `Documents` folder in
  your home folder, so they miss it if Windows has moved Documents, for
  example into OneDrive. Building the ten measured cars isn't affected.
  Until it's fixed, `AGENTS.md` tells your AI assistant how to work around
  the file name; if Windows has moved your Documents folder, measuring a new
  car doesn't work yet.
- Choosing your own colors isn't in yet. Every car carries the example black,
  papaya and white design.
  ([#5](https://github.com/Aintologic/aintologic-iracing-paints/issues/5))

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
