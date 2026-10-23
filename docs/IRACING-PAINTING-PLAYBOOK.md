# iRacing Painting Playbook

**Read this in full before painting any car. Every rule here cost a pass to learn.**

Written after the Global Mazda MX-5 Cup (#67), which went from nothing to an
approved, on-track-verified livery with a working spec map. Most of that time was
spent discovering things that are written down here now. A second car should not
need to rediscover any of it.

### How the example scheme personalizes

The generator ships an **example team scheme** (the papaya / black / white
livery described throughout this file). You make it yours with three flags on
the build:

- `--id <customerId>` — your iRacing customer ID, which names the output file
  `car_<id>.tga`.
- `--driver "<name>"` — fills the driver strip.
- `--logo1 <image>` / `--logo2 <image>` — your own artwork for the car's two
  **logo slots** (logo slot 1 and logo slot 2, at the positions this file and
  each car map name).

With no flags the output carries a neutral **"YOUR LOGO"** placeholder in both
slots and a **blank driver strip** — nothing personal ships in the repo. No logo
is mandatory; drop one slot and the scheme reads fine without it.

The template-derived island/mask files for the F4, Ray, HPD, Spec Racer Ford,
Skip Barber and Aston are **not shipped** — regenerate them from your own
iRacing template with the tools in `tools/`. The MX-5 is the fully worked
reference.

---

## Order of operations

Do these in order. Skipping ahead is what causes rework.

1. **Confirm the car ID.** Rule 1.
2. **Scope the tooling** to the repo, the iRacing paint folder, and a temp dir.
3. **Stand up the viewer loop** before painting anything. Rule 2.
4. **Probe the panels you intend to paint.** Rule 3. Do not design first.
5. **Write the panel map down** in `docs/car-maps/<car>.md` as you go.
6. **Build the colour map.** Verify every panel in the viewer, from a level camera.
7. **Only then** build the spec map. Rule 8.
8. **Lock the build** as soon as you approve it on the render. Rule 10.
9. **Verify on track** (when you race it), not just the viewer. Rule 9.
   Clean → update the `releases/INDEX.md` row to "on track verified, <date>".
   A problem → fix it as the next version; the locked one stays as it is.

---

## Rule 1 — Get the RIGHT template. Still the #1 failure.

Template zips are named `<carId>_template_<CODE>.zip`. The car ID is **not**
guessable from the name, and similar cars have similar codes.

Find the car ID inside iRacing:
`Racing -> My Content -> My Licensed Cars -> View Car -> Car Info`.
The ID is top-right of the Car Info panel as `#67`.

| car | ID | template |
|---|---|---|
| Global Mazda MX-5 Cup (2016) | 67 | `67_template_MX16.zip` |
| [Legacy] Mazda MX-5 Cup & Roadster (2010) | 35 | `35_template_MX5.zip` |
| FIA F4 (= the re-badged Formula iR-04; paint folder still `formulair04`) | 148 | `148_template_iR04.zip` — there is no "F4"-named zip in the collection; Trading Paints calls the same file `148_template_F4.zip` |
| Porsche 911 RSR | 102 | `102_template_RSR.zip` ("Porsche 911 RSR.psd"; paint folder `porsche991rsr`) — confirmed in Car Info 2026-09-14 |
| Ray FF1600 | 163 | `163_template_GR22.zip` → **`Ray FF1600.psd`**; paint folder `raygr22` — confirmed in Car Info 2026-09-14. The zip's code is the chassis (Ray GR-series), not the car name; the PSD is what settled it |
| Ferrari 296 Challenge | 203 | `203_template_F296C.zip` → **`Ferrari 296 Challenge.psd`**; paint folder `ferrari296challenge` — confirmed in Car Info 2026-09-16. **Not** `173_template_F296.zip`, which is `Ferrari 296 GT3.psd` |
| Lotus 79 | 25 | `25_template_L79.zip` → **`Lotus 79.psd`**; paint folder `lotus79` — confirmed in Car Info 2026-09-17 (the account showed "License Required"; the viewer loads custom paint anyway) |
| HPD ARX-01c | 39 | `39_template_ARX.zip` → **`Honda Performance Development ARX01C.psd`**; paint folder `hpdarx01c` — confirmed 2026-09-17 (the viewer titles the dialog "Car Info: HPD ARX-01c"). Its **Wire layer is blank** — islands come from the Mask layer instead, see `docs/PANEL-PROBING.md` section 13 |

Different cars, completely different UV layouts. Painting one with the other's
template scatters graphics across random panels — logos half on one panel, half
on another, some upside down.

**Check:** the PSD filename should name the car. `Mazda MX5 2016.psd` = right.
`Mazda MX5.psd` (with Cup/Roadster layer groups) = the legacy car.

## Rule 2 — Stand up the viewer loop FIRST.

`Racing -> My Content -> My Licensed Cars -> View Car -> Car Model`.
**Ctrl+R reloads the paint instantly.** Overwrite the TGA, press Ctrl+R, look.
That loop is the entire job. Everything else is arranging to run it faster.

Automate it. Keep these in a scratch folder:

- `view.ps1` — focuses the iRacing window, sends Ctrl+R, optionally drags to
  rotate (`-Drag`, `-DragY`) or scrolls to zoom (`-Wheel`), then captures the
  window to a PNG. One call per iteration.
- `crop2.ps1` — crops and upscales a region of a capture, for reading detail.

Two gotchas worth keeping:

- `mouse_event`'s wheel delta must be declared `int`, not `uint`, or negative
  (zoom-out) scrolls throw.
- Capture the **window rect**, not the whole screen. The iRacing window moves.

If your shell/file bridge returns PNG/JPG directly, no base64 plumbing is
needed. If it starts erroring with "session expired" on images, the payload is
too big: downscale or build a contact sheet first. The bridge is fine; only the
image path is size-sensitive.

## Rule 3 — Never guess a panel. Probe it, and probe it ON the livery.

Do not reason about which blob in the template is the hood. Paint a labelled
grid into the candidate region, load it, read it off the car.

`src/calibrate.py` does this standalone (`grid`, `rects`, `zones` modes). Each
patch carries a big label, a **red bar on its texture-TOP edge** and a **blue bar
on its texture-LEFT edge**, so rotation and mirroring are readable in one look:

| what you see | transform |
|---|---|
| label upright, red on top, blue on left | none |
| label upside down, red on bottom, blue on right | 180° |
| label on its side, red on right, blue on top | 90° CW |
| label mirrored | UV-mirrored (usually the far side) |

**Better: overlay the probe on top of the real livery** rather than replacing it.
A standalone test texture tells you where a rect lands; an overlay tells you
where it lands *relative to the artwork you already have*, which is the question
you actually have. That is how the rear quarter and the deck got solved.

### Rule 3a — READ PANELS FROM A LEVEL CAMERA. Never top-down.

This wasted a whole cycle on the MX-5. Read from a steep or top-down angle,
foreshortening turns clean rectangles into what look like skewed diagonal bands,
and you will write "this panel's UV is badly stretched" into the map. It isn't.
Get the camera level with the panel first, then read.

### Rule 3b — Do not trust panel rects you didn't verify yourself.

Two rects in the MX-5 map were fiction, inherited from an earlier session:

- `(683,887,614,751)` labelled "front bumper" actually lands on the rear shoulder.
- `(1341,1741,690,299)` labelled "rocker/sill" renders **nothing visible at all**.

If a rect has not been verified by probe, treat it as a guess. Mark unverified
rows in the car map explicitly.

### Rule 3c — Visible area is NOT the same as rect area.

Rects contain UV that is never seen from outside the car. Two ways this bites:

- **The deck.** Only columns 2-3 and rows Q-R of the MX-5's `DECK` rect land on
  the visible boot lid. Centring artwork on the *rect* centre put the wordmark
  half over the edge, which reads as skew. Find the *visible* centre and use it.
- **Hidden geometry.** The valance band's outer flats sat at local y=150 and
  produced no visible line at all — that y is on quarter geometry you cannot see
  from outside. Proved it by rebuilding with the edge as a fat magenta line:
  only the diagonal showed. **If artwork doesn't appear, draw it 20x thicker in a
  screaming colour before assuming the code is wrong.**

### Rule 3d — Find a panel by elimination when the map has no answer.

`calibrate.py grid --n 8` paints the whole texture as labelled cells. Look at the
surface you care about, read which cells land on it, then probe that region
finely. That is how the MX-5's nose was found in unclaimed texture space at
`(768,1024,1280,384)` after two named rects turned out to be wrong.

### Rule 3e — Check the full extent of a panel, both ends.

The nose band was fixed twice and still wrong. Starting at x=1024 width 768 left
BOTH bumper corners short. Widening only the high-x end fixed one corner and left
the other bare — visibly lopsided head-on, and I reported it as fixed. **When a
band spans a symmetric panel, check both ends before declaring it done.**

## Rule 4 — The two flanks. This is the subtlest trap in the whole job.

**The old advice in this playbook was wrong and caused a real bug. Read this
version.**

On the MX-5 both flanks have raw-texture **low x = the NOSE**, and the left panel
renders its content **ROTATE_180**. That combination means:

> `fl_left = fl.transpose(ROTATE_180)` does NOT give you the same livery on both
> sides. It moves the design's front content to the car's rear.

Symptom on the MX-5: the sill wedge rose toward the tail on one side and toward
the nose on the other, and the AI mark landed on the left front fender directly
on top of iRacing's stamped number.

**The fix — compose the flank per side, in two parts:**

```python
# geometry mirrors, because a real car's two flanks ARE mirror images
right = design                            # car-space, x=0 at the nose
left  = design.transpose(FLIP_TOP_BOTTOM) # renders as design mirrored in x

# text and marks must NOT mirror, so composite them AFTER that transform
def place(panel, element, cx, cy, left):
    if left:
        panel.alpha_composite(element.transpose(ROTATE_180),
                              (cx, PANEL_H - cy - element.height))
    else:
        panel.alpha_composite(element, (cx, cy))
```

Both land the same distance from the nose, upright, on both sides.

### Rule 4a — TEXT does not mirror. PICTURES DO. They need different code.

The `place()` above is written for text, and for text it is right: `ROTATE_180`
on the left flank leaves letters upright and the same distance from the nose.

Apply it to a **picture** and you get a bug that is easy to miss. A rotation is
not a mirror. Anything with a direction — claw marks, a paw, an animal that
faces somewhere, an arrow — ends up pointing at the nose on one flank and at the
tail on the other. On one car a directional logo raked forward on the right and
backward on the left, and the animal in it faced the wrong way, and it took a
level side-on look at BOTH flanks to see it.

A real car's two flanks are mirror images, so a picture has to mirror:

```python
def place_pic(panel, element, x, y, left):
    """Directional artwork. FLIP_TOP_BOTTOM composes with the panel's own
    ROTATE_180 to give a clean FLIP_LEFT_RIGHT on the car."""
    if left:
        panel.alpha_composite(element.transpose(Image.FLIP_TOP_BOTTOM),
                              (x, FH - y - element.height))
    else:
        panel.alpha_composite(element, (x, y))
```

Same positioning, same distance from the nose. Only the transform differs. Sort
every element into one of the two before you place it.

**Always verify both flanks in the viewer.** Never assume symmetry — that is the
whole point of this rule.

## Rule 5 — Panels can be rotated 90°, and size masquerades as orientation.

The MX-5 hood renders rotated 90° CW; build in car-space then `ROTATE_90`.

The trap: the hood mark looked wrong for three iterations and I changed the
**rotation** each time. The rotation (`ROTATE_180` before the panel's `ROTATE_90`
compensation) had been correct from the start. The actual defect was **size** —
at 470px wide on a 706px panel it ran off the front of the bonnet and read as a
cropped slab. At 300px it reads perfectly.

**Before changing a transform, check whether the element simply doesn't fit.**

## Rule 6 — Number blocks are reserved. Enforce it in code.

The template's `Number Blocks` layers mark where the sim stamps the number. They
must be **completely clear** in the colour map, and plain non-metallic gloss in
the spec map — a stamped number inherits whatever material sits under it.

Do not mask them at the end. **Design the geometry to clear them, and make the
build refuse to write if it doesn't:**

```
number blocks:
  N1 clean  0/12915 px
  N2 clean  0/12915 px
  N3 clean  0/6586 px
  RESULT: PASS
```

That guard fired for real during the MX-5 build and caught a tail band clipping
N3. `tools/checkblocks.py` checks a built TGA standalone.

**Number blocks turn up in surprising places.** N3 (a *front* bumper block) sits
inside the *rear* valance rect on the MX-5, at local `(761..850, 203..277)`.
iRacing packs unrelated panels into shared regions. Check every rect you paint
against every block, not just the obvious ones.

### The stamped number's colour

Set in **Paint Shop → Paint Your Car → Car Number**, three chips. Which chip
drives which number is **per car and not documented**. On the MX-5, chip 1 drives
the hood number and **chip 3 drives the flank number** — I guessed chip 2 twice
and was wrong both times.

**Prove it, don't reason about it:** paint the number blocks bright magenta on
top of the livery and reload. The stamp renders over the magenta and you can read
its exact position and colour in one look.

## Rule 7 — File format.

24-bit TGA, RLE compressed, 2048x2048, `car_<customerId>.tga` (the `--id` flag
sets the customer ID), in `%USERPROFILE%\Documents\iRacing\paint\<car folder>\`.
32-bit only for cars needing alpha.

    im.save(path, compression="tga_rle")   # PIL, image in RGB mode

Verify the header: **byte 2 must be `10`** (RLE true-colour), **byte 16 must be
`24`**.

Companions: `car_spec_<id>.tga` (Rule 8), `car_num_<id>.tga` (custom numbers —
only displays with "Hide Car Numbers" on, and Trading Paints charges Pro for it),
`car_decal_<id>.tga`.

## Rule 8 — The spec map. THE BLUE CHANNEL IS INVERTED.

Three attempts failed before this worked, all for the same reason.

| channel | controls | values |
|---|---|---|
| **R** | metallic | **binary.** 0 = not metal, 255 = metal. Nothing meaningful between |
| **G** | roughness | 0 = mirror smooth, 255 = dead flat |
| **B** | **clear coat, INVERTED** | 0-15 = OFF (pre-2023 look). **16 = MAXIMUM shine.** 125 = medium. **255 = dullest** |

**B=255 reads like "clear coat on" and is the dullest possible setting.** That
single wrong assumption washed the car to olive-brown twice and laid a dirty film
over it a third time. Metallic took the blame across two attempts and was
innocent.

Two more rules that matter:

- **Metals need a light albedo.** Metallic darkens the base colour. The MX-5's
  marks read as chrome because they are bone. Nothing dark should ever be
  metallic — it just goes muddy.
- **Decals are not chrome.** Sticker faces at `G=0` blow out and their text
  becomes unreadable. Semi-matte (`G≈95`) reads as vinyl. Only marks get mirror.

### Method — never guess global values

1. `tools/spec_ladder.py` — paints six (R,G) steps along each flank, B=255 on one
   side and B=0 on the other. One load gives you twelve data points.
2. `tools/spec_flat.py R G B` — uniform fill, to sweep one axis at a time
   **against a no-spec-map control**. The control matters: if your spec map looks
   worse than none, you have the channels wrong.

### Values that work on a near-black car

    body      (0,  40, 16)   non-metal, smooth, max clearcoat — deep and wet
    satin     (0, 110, 16)   separates from gloss black as a MATERIAL change
    gold line (255, 15, 16)  real metal. It's gold, so render it as gold
    bone line (0,   0, 16)   non-metal, mirror smooth — reads bright and wet
    marks     (255, 12, 16)  polished metal, the P-51 chrome look
    dots      (255, 22, 16)  polished copper — small warm accents glow
    decals    (0,  95, 16)   semi-matte vinyl
    numbers   (0,  40, 16)   plain non-metallic gloss

The satin-vs-gloss contrast is what reads best in motion — a material change,
not just a colour change.

### Values APPROVED on the team scheme (MX-5 v4.1, 2026-09-14) — use these first

    body black     (0, 170, 200)  satin-matte: dull coat kills the hotspot, no grey-out
    white bands    (0,  55,  30)  crisp, catches light, a step behind the orange
    papaya         (0,  35,  16)  the pop: max coat, smooth; + a 3-texel halo on small marks
    logo faces     (0, 120, 150)  semi-matte vinyl
    number blocks  (0,  60, 110)

Found by laddering B against a control in the viewer (`SPEC_VARIANTS` in
`src/team_mx5.py` keeps B1–B4 as the history). What the ladder showed: in
the viewer the clearcoat channel is what makes or kills the gleam, roughness
barely registers; B 235 starts to lift the black to grey, B 0 (coat off)
reads dusty; metallic on papaya turns it rust-red.

### Trading Paints wants the .mip, not the spec TGA

iRacing never uploads `car_spec_<id>.tga` anywhere. The sim converts it to
`car_spec_<id>.mip` in the same paint folder the first time it loads the car
with the TGA present (the car viewer does this too — Ctrl+R regenerates it).
Trading Paints takes **`car_<id>.tga` + `car_spec_<id>.mip`** as two
separate uploads — the TGA in My Paints, the .mip via Paint Options → Add
spec map. **Not the zip** — Trading Paints rejected it when tried
(confirmed 2026-10-10); the release zip is a backup bundle only. Lock the .mip
in the release next to the TGA that produced it (check its mtime is later
than the TGA's — for v4.1 the sim wrote it 1 s after the final TGA), and once it is
uploaded take the spec TGA out of the paint folder, or the sim keeps
regenerating the .mip locally on top of whatever Trading Paints serves.
Source: help.tradingpaints.com → "How do I create a spec map file".

## Rule 9 — Verify on track, and check banding numerically.

The car viewer does not represent in-game appearance; the painting tutorial's
author says so outright. Gloss and clearcoat are exactly the properties most
likely to differ. Get screenshots from a replay before calling a paint done.

**When (decided 2026-09-26): lock first, track second.** A car is
locked as soon as you approve it on the render — that protects the approved
pixels. The on-track check comes later, whenever you race it. If the track is
clean, update the car's `releases/INDEX.md` row to "on track verified,
<date>". If the track shows a problem, the fix is the **next version**; the
locked one is never edited. (Five cars were locked this way before the rule was
written down; this makes the docs match the practice.)

**Banding:** iRacing recompresses to 8-bit in game. Gradients band; flat colour
does not. If the livery is flat colour you are almost certainly fine, but measure
rather than squint — sample the dark bodywork and count unique values per channel
plus the longest identical horizontal run:

    R uniq=181  G uniq=120  B uniq=129 | longest flat run 17px of 2303

Healthy. Banding shows as **few unique values and long runs (50-200px)**. If it
appears, the fix is a subtle HSV noise pass over the gradient before export.

## Rule 10 — Lock every approved build.

A git tag alone is **not** enough. A tag says "rebuild from this source", which
does not guarantee the same pixels — rebuilding an older MX-5 commit from
unchanged source produced ~18,000 differing pixels because Pillow's text
antialiasing had moved. Fonts, Pillow and the code all drift.

Freeze three things per approved build, in `releases/<car>/<version>-<date>/`:

1. **The exact TGA bytes**, with a sha256. This is what gets restored.
2. **A preview image** — a six-angle contact sheet — so a build is recognisable
   on sight without loading it.
3. **A git tag** on the source, for reading and branching, not for rebuilding.

`src/restore.py --list` / `src/restore.py <version>` copies the frozen artifact
back into the paint folder. Add a row to `releases/INDEX.md` so builds can be
recalled by date and picked by picture.

## Rule 11 — Artwork is source code.

Keep the livery as a script plus vector marks so it retargets to the next car by
changing only the panel map. A flattened PSD cannot be reused.

Put reusable marks in `src/marks.py` (brand marks) and `src/furniture.py`
(race-car furniture: roundels, tech plates, decal text). Both take colours as
parameters, which is what lets the same code emit the colour map and the spec map
from one geometry pass — pass brand colours for one, material values for the other.

## Rule 12 — The render is the truth. The MX-5 v4 loop, distilled (2026-09-14).

The approved MX-5 (v4.1) took a day of one-region-at-a-time passes. Every
pass that went wrong went wrong the same way: something was reasoned about
that should have been measured on the rendered car. The next car — the F4,
with completely different geometry — should run this loop from the start:

1. **Template and islands first.** Open the official template, list the UV
   islands and which body surface each covers, before drawing a line.
2. **Sides by what the viewer shows.** Rect names lie. On the MX-5 the
   `(386,507)` "left" flank renders on the car's RIGHT, and `+x` on it is
   FORWARD. Establish this with a probe and write it down in the car map.
3. **Probe anything uncertain.** Labelled grids (`tools/probe.py`), tick
   rulers across a seam, hue-coded cells with a fitted texture→screen affine
   (`tools/probe_affine.py` + `tools/fit_affine.py`) for anything that must
   land exactly. Read them from LEVEL side / dead front / dead rear frames;
   a three-quarter view foreshortens and will lie to you.
4. **Render early.** Ctrl+R after every change. Nothing is known until it
   has been looked at on the car.
5. **Validate from several angles**, in the poses you judge from.
   The viewer camera is cumulative and non-linear: sweep in small steps and
   pick frames; never assume the camera is where you left it (you
   may have moved it).
6. **Judge continuity from the FINAL render**, not from texture geometry.
   Identical texel widths do NOT give identical rendered widths (the MX-5's
   hood, fender and quarters all render at different px/texel and with
   different anisotropy). A straight texture line kinks across a real body
   crease from most viewpoints; tune the join on the render.
7. **Calibrate left and right independently.** The hood island was not
   mirror-symmetric (per-edge trims of −5 / +10 px), nor were the flanks
   (+15 texels one side), nor were the rear quarters (different islands
   entirely). Expect it.
8. **Same rendered size and place both sides for sponsors**: define them as
   SCREEN rectangles through the fitted affine and inverse-map, instead of
   placing per island by eye; measure the result on both sides.
9. **Fix only the defective region.** Keep approved regions byte-identical;
   check with a hash or a texel span readout. When a state was right once,
   keep the screenshot and use it as the target (a sign error once undid an
   approved state; the screenshot brought it back).
10. **Checklist per stripe**: continuity, width (rendered), alignment,
    tangent/direction at the crossing, behaviour at every panel seam.
11. **Spec map last, laddered.** In the viewer the clearcoat channel (B,
    inverted) makes or kills the gleam and roughness barely shows; ladder B
    against a control before believing any value. Small orange marks need a
    material halo (texture filtering averages them away). Nothing dark
    metallic. Check the hierarchy — calm body, crisp white, popping orange —
    in a lit pose.
12. **Not finished until the rendered result passes your visual
    review from screenshots you took yourself**, then on track.

---

## Working practice

- **Show the car, don't describe it.** A described livery is worthless; a
  screenshot is everything. Render, look, judge.
- **Lead with what's wrong.** Not three sentences of preamble.
- **Verify, don't infer.** Every rule above exists because something got inferred
  that should have been measured. When something looks wrong, build the probe.
- **Write the map down as you go**, in `docs/car-maps/<car>.md`, including what
  was *tried and rejected* and why. "Do not re-litigate" notes save whole cycles.
- **Correct the docs when they're wrong.** This file carried bad flank advice
  (Rule 4) and a "front bumper" rect that pointed at the rear shoulder. Fix them
  in place with a note, don't leave the wrong version sitting there.

## Appendix — Global Mazda MX-5 Cup (#67), verified

Full detail in `docs/car-maps/mx5-2016-global-cup.md`. Summary:

| panel | rect | transform |
|---|---|---|
| RIGHT flank | `(386,1679,884,306)` | upright |
| LEFT flank | `(386,507,884,306)` | ROTATE_180 — see Rule 4 |
| hood | `(12,880,706,732)` | 90° CW; draw ROTATE_90 |
| rear deck | `(1132,130,747,456)` | upright; visible area is cols 2-3, rows Q-R |
| rear valance + quarters | `(16,11,1179,441)` | upright; outer columns are the QUARTERS |
| nose / front fascia | `(768,1024,1280,384)` | upright; far end also paints the mirror caps |
| number blocks | N1 `(493,577,123,105)`, N2 `(493,1810,123,105)`, N3 `(777,214,89,74)` | keep clear |

Side mirror axis: `left_y = 2492 - (right_y + height)`.

**Rects in the old map that are WRONG:** `(683,887,614,751)` "front bumper" lands
on the rear shoulder. `(1341,1741,690,299)` "rocker" renders nothing visible.
`QUARTER` rects `(1297,600,355,200)` / `(1652,800,355,200)` show only slivers.
