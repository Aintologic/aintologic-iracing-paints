# Change log

What changed in each version of iRacing Paints, newest first. How the version
numbers work is explained in the README's [Versions](README.md#versions)
section.

## 0.3.0 (2026-10-26)

Still an early preview. This version is about making the car yours: your own
colors, finishes, stripe style and team name, on every measured car. GitHub
now also checks every change automatically. The ready-made paints are
unchanged, byte for byte.

### What's new

- **Your own colors and team name.** A design settings file, a small text
  file, sets the car's body, stripe, trim and lettering colors, how each part
  takes the light (gloss, satin, matte, metallic, pearl, chrome or brushed),
  which stripes are drawn, what goes in the two logo spots, and your team
  name in place of the big AÏNTOLOGIC lettering, with a small "made with
  AÏNTOLOGIC" line under it. Add `--design` to build any of the ten measured
  cars with it; the same file works on all of them. Four samples to start
  from are in `examples/designs/`, and the new guide,
  [`docs/YOUR-OWN-DESIGN.md`](docs/YOUR-OWN-DESIGN.md), explains every
  choice. Anything you leave out keeps the example design, and with no design
  every car builds exactly the same paint as before. The build also warns you
  when a color will be hard to see. The number panels stay white, with their
  own finish, because iRacing prints the number on them. `TRADEMARKS.md` now
  also says you may race a paint you built with the tools on your own car,
  the "made with AÏNTOLOGIC" line included.
  ([#5](https://github.com/Aintologic/aintologic-iracing-paints/issues/5))
- **Automatic checks on every change.** Each time a change is pushed or
  offered as a pull request, GitHub now checks it on Windows and on Linux:
  nothing that looks private in the files or their history, every license in
  place, and the cars built with their default settings match the ready-made
  paints byte for byte. A design check builds each car again with every
  sample design: the example-scheme sample must make exactly the default
  paint, and every other sample a different one. The badge at the top of the
  README shows the latest result, and you can run the same checks yourself:
  `tools/privacy_check.py`, `tools/license_check.py` and
  `tools/check_builds.py` (see `CONTRIBUTING.md`).
  ([#12](https://github.com/Aintologic/aintologic-iracing-paints/issues/12))

### What's fixed

- **The measuring tools' test patterns now show on the car.** They saved
  their test pattern as `car_CUSTOMERID.tga`, a name iRacing doesn't load, so
  the car viewer kept showing the old paint. Now each one takes your customer
  ID with `--id` (or from an `IRACING_CUSTOMER_ID` setting) and saves the test
  pattern as `car_<your ID>.tga`, the name iRacing loads. Without an ID they
  stop and say what they need instead of writing a file iRacing ignores.
  While a car is measured, the test patterns replace your own paint for that
  car, so your paint is still backed up into `out\backup` first, and the tool
  says where. They also refuse an ID that one of your saved profiles lists
  under `protect_ids`. This covers `tools/probe.py`, `probe_affine.py`,
  `probe_bands.py`, `probe_islands.py`, `probe_multi.py`, `probe_ruler.py`,
  `probe_ticks.py`, `coord_grid.py`, `spec_flat.py` and `spec_ladder.py`.
  ([#17](https://github.com/Aintologic/aintologic-iracing-paints/issues/17))
- **They find your paint folder if Windows has moved Documents,** for example
  into OneDrive. They ask Windows where Documents is, the same way
  `tools/check_setup.py` does.
  ([#17](https://github.com/Aintologic/aintologic-iracing-paints/issues/17))
- `AGENTS.md` no longer tells your AI assistant to copy each test pattern by
  hand; the guides show the `--id` option instead.

### Known issues

- **The logo spots stay where they are.** Each car has its two logo spots in
  fixed places: a design picks what goes in them, not where they are. The
  stripes keep each car's layout too; a design picks their colors and which
  ones show.
  ([#5](https://github.com/Aintologic/aintologic-iracing-paints/issues/5))
- **GitHub builds four of the ten cars:** the MX-5, the Porsche 911 RSR, the
  Ferrari 296 Challenge and the Lotus 79. The other six need their one-time
  setup step, which reads iRacing's own paint template, and iRacing's
  templates can't be published. Those six are checked on a computer with the
  templates before each release.
  ([#12](https://github.com/Aintologic/aintologic-iracing-paints/issues/12))

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
