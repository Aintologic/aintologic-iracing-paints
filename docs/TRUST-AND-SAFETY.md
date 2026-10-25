# Trust and safety

## What and why

Before you let a tool near your computer and your iRacing setup, you should
know what it does. This page says plainly what this project reads, what it
writes, and what it never touches. Everything here can be checked against the
code in `src/` and `tools/`; if you ever find it isn't true, that's a bug
worth [reporting privately](../SECURITY.md).

## What "done" looks like

The short version:

- **It never asks for your iRacing login,** and never reads account or
  password files.
- **The tools don't connect to the internet** and upload nothing.
- **It doesn't install anything.** If something is missing, it says what and
  where to get it, and you install it.
- **Building a paint writes into the project's `out` folder.** You, or your
  AI assistant after you say yes, copy the files into iRacing.
- **Before a measuring tool replaces a file in iRacing's paint folder, it
  backs up the one that's there,** and tells you where the copy is.
- **The viewer tools move your mouse** inside iRacing's car viewer. They only
  run when you start them, or when your AI assistant does after asking you.

The details follow.

## What it reads

- The project's own files: its code, fonts and images.
- Logo images you choose with `--logo1` and `--logo2`.
- Your saved settings in `profiles/<name>.json`, if you use `--profile`.
- An iRacing paint template you point it at, for a car's one-time setup step
  or for measuring a new car.
- Whether your iRacing paint folder exists (`tools/check_setup.py`), and
  whether a file is already there before a measuring tool replaces it, so it
  can be backed up.
- For the viewer tools: the titles of the open windows, to find iRacing's
  (nothing is kept), and then a screenshot of the iRacing window.
- `src/calibrate.py` reads an `IRACING_CUSTOMER_ID` setting, if you have made
  one, to name its test file.

It never reads your iRacing login, password or account files, your browser's
history or data, or anything else in your `Documents\iRacing` folder.

## What it writes

| where | what | which tools |
|---|---|---|
| `out` in the project folder | finished paints, previews, screenshots, contact sheets (several screenshots tiled into one picture), test pictures, backups and working files | the builders in `src/` and the tools in `tools/` (`check_setup.py` writes nothing) |
| `src/` and `assets/` in the project folder | the panel shapes for six cars, made from your own copy of their iRacing template | `tools/first_run.py` (the one-time setup step), and the four tools it runs (`f4_islands_gen.py`, `island_edges.py`, `body_mask.py`, `island_id_mask.py`) if you run them yourself |
| iRacing's paint folder for one car | a test-pattern paint or a test finish, while a car is being measured | the measuring tools, listed below. They back up first. |

If you choose another folder (for example with `--out`), the tools write
there instead. Python itself also keeps compiled copies of the code in
`__pycache__` folders inside `src/` and `tools/`; git ignores them, and they
are safe to delete.

## Your paint is backed up before anything replaces it

The builders write into the project's `out` folder, not into iRacing's paint
folder. The only tools that write there themselves are the measuring tools,
which paint test patterns onto the car so its panels can be read in the car
viewer: `tools/probe.py`, `probe_affine.py`, `probe_bands.py`,
`probe_islands.py`, `probe_multi.py`, `probe_ruler.py`, `probe_ticks.py`,
`coord_grid.py`, `spec_flat.py` and `spec_ladder.py`.

Before one of them replaces a file, it copies the one that's there into the
project's `out\backup` folder, in a folder named after the car's paint folder,
with the date and time added to its name. For example, a
`car_CUSTOMERID.tga` in the MX-5's paint folder is saved as:

```
out\backup\mx5 mx52016\car_CUSTOMERID.20261025-101500.tga
```

The tool prints where the copy is. **To put it back,** copy that file into the
car's paint folder and rename it to its original name, without the date and
time. Then close the car viewer and open it again.

As shipped, the measuring tools only ever write `car_CUSTOMERID.tga` and
`car_spec_CUSTOMERID.tga`, so they never touch a paint named with your own
customer ID. (That is also why they don't work as described yet; see the
known issues in the [change log](../CHANGELOG.md).) They look for iRacing's
paint folder in the `Documents` folder inside your user folder. Until that's
fixed, `AGENTS.md` tells your AI assistant, while it measures a new car, to
copy each test pattern over your own `car_<your ID>.tga` with
`paintfolder.copy_in()`. The first copy saves your paint into
`out\backup\<paint folder>\`; it stays replaced until you put that copy back
or copy a finished paint in, and the assistant tells you where it is.

`spec_flat.py none` takes the finish file `car_spec_CUSTOMERID.tga` back out
of the MX-5's paint folder, together with the `.mip` file iRacing made from
it. It moves both into `out\backup` the same way and prints where they went.

There's one exception to the copying. When a measuring tool runs again, the
file in the paint folder is usually the test pattern it wrote a moment ago.
That isn't yours, so it isn't copied again; the first copy is still there.
The tool says so when it happens. It only skips the copy when the file is
exactly, byte for byte, the one the project wrote, so nothing of yours can be
lost that way.

The builders and `src/calibrate.py` don't make backups, because they write
into `out`. If you point `--out` (or `--here`) at iRacing's paint folder
yourself, they replace what's there without a copy, so build into `out` and
copy the files in.

[`AGENTS.md`](../AGENTS.md) tells your AI assistant to follow the same rule
when it copies a finished paint into iRacing for you: ask first, back up any
file with the same name into `out\backup`, and tell you where the copy is.

## The viewer tools move your mouse

`tools/view2.py`, `walk.py`, `walk_top.py` and `contact.py` take screenshots
of the car in iRacing's car viewer, so a paint can be checked from several
angles. Building a paint never needs them, and they never start on their own.

For each screenshot, the tool:

1. finds the iRacing window and brings it to the front;
2. clicks once inside the car viewer;
3. presses Ctrl+R twice, which reloads the paint: `view2.py` does this unless
   you add `--no-reload`, `contact.py` before its first screenshot only, and
   `walk.py` only with `--reload`; `walk_top.py` never does;
4. drags the mouse to turn the camera around the car, or scrolls to zoom, if
   asked;
5. saves a screenshot of the iRacing window into `out`.

A walk around the car repeats this for every frame, so it clicks once per
screenshot.

Before it clicks, drags or presses a key, it checks that the iRacing window
is the one that will get it. If iRacing isn't running, won't come to the
front, or has another window over the spot where it clicks, it stops and says
why. It never clicks or types anywhere else.

A screenshot shows everything on screen where the iRacing window is,
including any other window lying over part of it, such as a chat window. Keep
other windows clear of iRacing while it runs, and look at the pictures before
you share one.

**To stop one,** click the window it's running in and press Ctrl+C, or close
that window. If your AI assistant is running it, use the assistant's stop
button. One screenshot takes a few seconds; a full walk around the car takes
about a minute.

## If you work with an AI assistant

The tools themselves don't connect to the internet, but an AI assistant
reads the files it works with, including previews and screenshots, and most
assistants send what they read to the company that runs them. Check your
assistant's privacy settings, and keep anything you don't want it to see out
of the project folder and off the screen while the viewer tools run.

## For the AI agent

- Never ask for, store or type iRacing credentials or account details.
- Before writing into the client's iRacing paint folder, back up what is
  there and tell them where the copy is. The measuring tools do it through
  `src/paintfolder.py`; use the same helper in any new tool that writes there,
  and `paintfolder.copy_in()` when you copy a finished paint in.
- Ask before running any tool that moves the mouse or presses keys, and say
  what it will do.
- Keep this page true. If you add or change a tool so that it reads or writes
  something new, update this page in the same change.
