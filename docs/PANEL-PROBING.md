# Panel probing — how to find out what a UV rect actually does

**Read this before you place ANYTHING from a design drawing onto a car.**

Every hour lost on this project has been lost the same way: reasoning about a
panel instead of measuring it. The playbook says "never guess a panel". This
file is the *how* — the specific probes, what each one answers, and the traps
that made each one necessary. All of them live in `tools/`.

The rule underneath all of it: **a probe is cheap, a wrong assumption is not.**
One probe render costs about a minute. Guessing wrong cost this project three
full rebuild passes on a single car.

---

## 0. FIRST: make sure the viewer is actually reloading

`tools/view2.py`, not a bare Ctrl+R.

The old reload silently did nothing whenever the iRacing window did not take
focus, so renders being judged were **stale**. Several "the fix didn't work"
conclusions were wrong for this reason alone, and led to changes that made
things worse. `view2.py` takes focus, verifies it took (prints NOFOCUS and
stops if not), clicks into the 3D pane, sends Ctrl+R twice, and waits before
capturing.

    python tools/view2.py --out out/a.png
    python tools/view2.py --no-reload --drag 900 --out out/b.png

If a change appears to have had no effect, **suspect the reload before you
suspect the code.**

---

## 1. The ruler probe — what does this rect cover?

`tools/probe_ruler.py <module> NAME:x,y,w,h:X:100` (and again with `:Y:50`), or
`tools/probe.py <module> rect x y w h --n 4`

Labelled gridlines every 100 in x and 50 in y, painted **over the live livery**,
read from a **level** camera (playbook Rule 3a — never top-down).

Answers: how much of the car the rect covers, where its origin is, and which
way its axes run.

**This is the number the car map was missing for months.** It recorded rects
and transforms but never *coverage*, so any size taken from a design drawing
had to be eyeballed. Result for the MX-5 flank:

| flank coord | on the car |
|---|---|
| x = 0 | 20.6% of car length back from the nose |
| x = 884 | 71.5% back |
| y = 0 | belt line |
| y = 271 | bottom of the sill |

i.e. the flank rect covers **the middle 51% of the car only**. Anything a side
drawing places outside that band physically cannot go on that panel — which is
why claw slashes at 80% of car length kept landing on the door.

**Always record coverage in `docs/car-maps/<car>.md`.**

---

## 2. The column probe — where does each part of a rect land?

`tools/probe_ruler.py <module> NAME:x,y,w,h:X:<step>` with a small step, or
`tools/probe.py <module> rect x y w h --n 10`

Fat bars of distinct colour at known x, read from the surface.

**Sample densely.** A five-column probe of the valance produced a scrambled
mapping — plate recess at x 0..70, one corner at 150..220, the other at
800..970 — and the rear stripe was painted as two patches on the corners on
the belief that there was no continuous run between them. A ten-bar probe across the
same rect showed **x 0..940 runs straight across the tail in order**. The
mapping was fine; the sampling was too sparse to see it.

If a mapping comes back looking scrambled or non-monotonic, **re-probe finer
before believing it.**

---

## 2b. The one tool that does all of it now — `tools/probe.py`

Since 2026-09-13. Car-agnostic: give it the build module and it paints the
probe OVER that build's live livery.

    python tools/probe.py team_mx5 grid --n 8                 # section 3
    python tools/probe.py team_mx5 rect 1024 0 512 512 --n 4  # sections 1-2
    python tools/probe.py team_mx5 bands 1280 1536 256 256 --n 8   # section 4

Every cell carries its label, a red bar on its texture-top edge and a blue
bar on its texture-left edge. Then `tools/contact.py` for six angles, and
`tools/zoom.py` to crop and upscale the one you need to read. The build
module only needs `build(spec=False)`, `PAINT_DIR` and `CUSTOMER`.
`probe.py` writes into the car's iRacing paint folder through
`src/paintfolder.py`, which first copies the file that's there into
`out/backup/<paint folder>/` and prints where; a rerun over its own test
pattern isn't copied again. Every probe and `coord_grid.py`, `spec_flat.py`
and `spec_ladder.py` do the same.

**Known problem (0.2.0):** the probes save their test pattern as
`car_CUSTOMERID.tga` (the builder's placeholder name), which iRacing doesn't
load, and look for the paint folder under the `Documents` folder in your
home folder. If a probe seems to have no effect, check the file name before
you blame the reload. Until it's fixed, copy the test pattern to
`car_<your customer ID>.tga` in the same folder after each probe, with
`paintfolder.copy_in()` so your own paint is backed up first.

**Camera:** `view2.py --drag 260` is ~90°. Pitch clamps, so `--drag-y -600`
is always level and `+600` always top-down — if a capture is top-down, that
is why. `contact.py --level` fixes it.

- **Ctrl+R does not reset the camera** (checked 2026-10-24: pixel-identical
  before and after a reload). ONE drag can be undone exactly: `--drag -260`
  after `--drag 260` returns a pixel-identical pose. A sequence cannot: two
  `+65` drags then two `-65` landed ~1° off, and two poses that look
  pixel-identical can answer the next drag differently, depending on how
  they were reached. So never undo a sweep and assume you are back —
  re-capture. When you compare two captures by pixels, compare the 3D pane
  only: the blurred car list below the Car Info dialog can shift between
  captures.

This is how both MX-5 rear quarters were finally found in the valance rect
(the car map has the story). Sections 1 to 5 are the questions it answers;
each names the command to use.

## 3. Elimination — the panel isn't in any rect you know

`tools/probe.py <module> grid --n 8`, then `--n 4`, or `tools/coord_grid.py <module>`

Labelled cells over the **whole 2048 texture**, over the live livery. Look at
the surface you care about, read which cell lands on it, then probe that region
finely with quadrants.

Use `--n 8` to locate, `--n 4` when the labels are too small to read on a
curved or distant panel (bigger cells, bigger type).

This is how the MX-5's nose was found in unclaimed space, and how the second
rear quarter was found at `(1280,1536,256,256)` after it turned out to be in no
mapped rect at all.

**The two rear quarters are not symmetric in this UV.** One is carried by the
valance rect's high-x columns; the other is a separate rect entirely. Do not
assume a left/right pair exists just because the car is symmetric.

---

## 4. The height probe — where in the rect is the right height?

`tools/probe.py <module> bands x y w h --n 5`, or `tools/probe_ruler.py` with axis `Y`

Several horizontal bands of distinct colour stacked down the rect. Read which
one lines up with the feature you are matching.

Also tells you whether the rect's y is inverted (it usually isn't, but the
spec map's blue channel is — different trap, playbook Rule 8).

---

## 5. The transform probe — text vs geometry

`tools/probe.py <module> rect x y w h --n 2`, or `tools/probe_multi.py`: every cell
is marked with a red bar on its texture-top edge and a blue bar on its
texture-left edge

Paste a full-panel test image with **no transform at all**: NOSE at low x, TAIL
at high x, red bar on the top edge, blue bar on the left edge. Whatever the car
shows *is* the panel's transform, read directly.

**The MX-5's far flank mirrors handedness.** That means:

> No single rigid transform of a whole side elevation can give both correct
> text and correct front-to-back placement.

- `FLIP_TOP_BOTTOM` → layout correct, **type mirrored**
- `ROTATE_180` → type correct, **layout reversed** (nose content at the tail)

Both were shipped and each looked like a regression of the other. The fix is
the split the playbook already describes:

    GEOMETRY mirrors with the panel   (Rule 4a, place_pic)
    TYPE is composited afterwards     (Rule 4, place)

So for a resampled elevation: erase the wordmark out of the source, mirror the
elevation, then draw the type in code on top at the mapped position.

---

## 6. Resampling a design flat instead of redrawing it

If a design comes as an orthographic elevation and the target rect is a linear
map of that surface, **resample the flat straight into the rect**. It removes
every opportunity to eyeball a size, which is where the errors come from.

The original working example was written for an early MX-5 builder that is
not part of this repo.

Things that still have to be handled in code, each learned the hard way:

- **The design's own number panel must be erased.** iRacing stamps at the
  block, which is rarely where a designer draws it. Paint a real panel on the
  block instead.
- **Wheels.** "Both wheels fall outside the panel" was true at true scale and
  stopped being true the moment the sampling window was widened — and a picture
  of a tyre got painted onto the bodywork. Inpaint them by copying a clean
  pixel column across the wheel's x range, and **only from the top of the band
  down**: copying the full column smears a slice of the lettering across the
  door, and filling above it erases the end of the wordmark.
- **Type**, per section 5.

---

## 7. Number blocks

The build guard exists because artwork drifts into them. But it must allow a
**deliberate flat panel** — a real racing number panel *is* a flat fill under
the stamped number, and painting one is how you get the design's look with the
sim's number. The build guard (see `src/teamscheme.py`) permits base colour or the
panel fill and fails on anything else.

Check every rect you paint against **every** block, not just the obvious ones —
N3 is a *front* bumper block that lives inside the *rear* valance rect.

---

## 8. The F4-era loop — template first, many probes per reload, sweep and pick (2026-09-14)

Everything above still applies; the F4 added the tools that make it fast on
a car with ~20 islands.

- **`tools/template_layers.py <zip> <dir>`** — opens the template, writes
  the wire, number-block and sponsor-block layers (invisible layers included)
  and an overview with a 256-px grid, and prints the block rects. Do this
  before any probe: it gives the number blocks for free and shows where the
  islands are. It never tells you which surface an island is — probe that.
- **`tools/probe_multi.py <module> NAME:x,y,w,h:cols,rows ...`** — many
  labelled rects in ONE reload, each cell with a name+index, a red top bar
  and a blue left bar. Three reloads mapped the whole F4 (8x8 elimination,
  6x2/8x2 island grids, 10x4/12x5 fine grids). Keep labels big; the 8-colour
  palette repeats.
- **`tools/walk.py` + `tools/contact_sheet.py`** — sweep the camera in
  fixed drags, crop the 3D pane proportionally, tile the numbered frames,
  pick the level side / dead front / top by eye. The drag→angle response is
  non-linear and the operator moves the camera between calls: sweep and
  pick, never assume a pose.
- **Island edges from the template's GREEN outlines** — the template draws
  each UV island's boundary in green and the mesh in white; label the
  regions enclosed by the green lines (`tools/f4_islands_gen.py`) and you get
  each island's top/bottom edge per column. That is how the F4's engine-cover
  stripes were hung from a sloped ridge edge and came out identical on both
  sides. Islands that touch merge — split them per column by their runs.
- **Straight-line clipping = off-island.** A mark that vanishes along a
  clean straight line is sitting on texture no mesh uses (the F4's logo slot 2
  mark fell in the gap between two engine-cover islands). Check the edge table
  before suspecting the code, the reload, or the sim.
- **The mirror may be one number.** The F4's whole right side is the left
  side reflected about texture row 1128.5 (right y = 2257 − left y); the
  MX-5's sides were not symmetric at all. Measure two or three island pairs
  from the outlines before deciding which kind of car you have.
- **Edge-band probes** (1×N bands down a rect) settle "which rows of this
  island are the ridge / the crease / the bottom" in one look from a level
  side; label the bands by colour order and check the palette before
  reading.

## 9. The RSR-era additions — widths, centres, and islands hiding inside islands (2026-09-14)

- **`tools/probe_ruler.py <module> NAME:x,y,w,h:X|Y:step[:c=v]`** — numbered
  bands along one axis of several rects in one reload, with a black line at
  `c=`. Answers "which texel column is the centre line / where does this
  panel end" (the hood, bumper, tail and engine cover on the RSR). Tell X
  bands from Y bands on the render by label size: single digits render big,
  double digits small on X bands; both the same on Y bands.
- **`tools/probe_ticks.py <module> NAME:a,b:X|Y:centre:step`** — thin ticks
  ACROSS the live stripe every `step` texels (every 4th cyan and labelled),
  so a top-down or dead-front frame gives the rendered width of the stripe
  per texture column (`<scratch>\measure.py` reads it off). This is how
  the RSR's per-panel stripe widths were found to be guesses: the hood, roof
  and cover all render the same px per texel, so ONE recipe serves them all.
- **A rainbow of thin bands is the fastest orientation probe** for a small
  island: 8-texel bands in an ordered 8-colour cycle, read the order and the
  spacing on the render. Found the RSR's louvre-lip mapping in one reload.
- **Islands can live INSIDE another island's bbox.** The RSR's windscreen
  banner (Z) sits inside the roof island's bbox, and the two louvre lips sit
  inside the hood island's bbox. A rect drawn across a bbox paints them
  too, and they render somewhere else. When a mark shows up where nothing
  was aimed, list the components inside the rect you painted.
- **Judge centres from DEAD front / rear frames only.** A 3/4 frame moved the
  RSR's tail stripe the wrong way once; the fix came from the light bar /
  exhaust centre in a true dead-rear frame.
- **The viewer's top-down pose crops the nose at working zoom.** Zoom out
  (`python tools/view2.py --no-reload --wheel -4`) to see the whole hood
  from above; wheel ticks are sometimes swallowed — check the frame, repeat
  if unchanged.
- **When the geometry defeats the recipe, say so early.** Five passes went
  into forcing a constant-width stripe through the RSR's hood louvres before
  the designer changed the hood to a V. If a panel's openings, lips or recesses
  eat a band, show the operator the options on the second pass, not the fifth.

## 10. The Ray-era additions — probe the ISLAND, not the rect (2026-09-14)

- **`tools/probe_islands.py <module> <tpl-dir> list`** inventories every UV
  island the template's green wire outlines enclose — index, bbox, area,
  centroid — sorted by area. Do this straight after
  `tools/template_layers.py`; it replaces squinting at the wire picture.
- **`tools/probe_islands.py <module> <tpl-dir> 4:E:10,1 2:B:5,6 ...`** paints a
  labelled grid **masked to one island**, so every painted texel is
  attributable. A plain rect probe cannot be: on the Ray FF1600, island 13
  lives entirely inside island 2's bbox and islands 17 and 32 inside island
  0's, exactly like the RSR's louvre lips. Masking removes the whole class of
  "a mark appeared where nothing was aimed" error.
  - `IDX:NAME:cols,1` is a ruler along the car; `IDX:NAME:1,rows` is a ruler
    across it (which rows are the panel's top / face / underside);
    `IDX:NAME:1,1` floods one island with one colour and one big label —
    **that last form is the fastest way to name twenty islands in one
    reload.** Read it from a level side AND a top-down.
- **`tools/island_edges.py <tpl-dir> <out.py> <mirror> NAME=idx ...`**
  generalises `tools/f4_islands_gen.py`: a per-column `(y_top, y_bottom)`
  table for any island of any car, so a band can hang off a sloping island
  edge (the Ray's tail-spine stripes) instead of a constant row.
- **Measure the mirror row, don't read it off bboxes.** Flip each candidate
  island pair's mask about every M in a range and take the M that maximises
  overlap. On the Ray, twelve pairs all peaked at 2051–2052 with 98–100 %
  overlap — a definite answer, where the bboxes alone gave 2051 / 2052 / 2054
  / 2055 depending on which pair you looked at.
- **An island whose green outline has a gap merges with the BACKGROUND** and
  therefore never appears in the island list. The Ray's LEFT sidepod does
  exactly this. Symptom: one side of a mirrored pair is missing from the
  inventory while its number/sponsor blocks clearly exist. It is still painted
  correctly by the whole-half mirror — just don't try to mask to it.
- **Painting only one half's islands leaves the other side of the car black.**
  That is the mirror working, not a dead island. Two sweeps were misread as
  "island 6 renders nothing" before the camera had been swung right round.

## 11. The Ferrari 296 Challenge additions (2026-09-16)

- **Two templates share a car name.** `173_template_F296.zip` is the 296
  GT3; `203_template_F296C.zip` is the 296 Challenge. The Car Info `#203`
  and the PSD name settled it — as rule 1 says, every time.
- **A whole hood can be missing from the island list** — its green outline
  leaks into the background. Probe it with a plain rect grid
  (`tools/probe_multi.py`) stacked on the masked island probe: build a tiny
  module whose `build()` returns the TGA already in the paint folder and pass
  it to `probe_multi.py` after `probe_islands.py` has written.
- **`tools/island_runs.py <tpl> y:X:Y0:Y1 x:Y:X0:X1`** prints which island
  owns every run of one texture column or row. It sized the tail band
  before painting (only 38 rows tall at the centre column) and explained two
  defects the render showed: a rear-arch cutout that clipped the logo slot 2
  mark, and a driver strip sitting on no island at all.
- **A vent on the centre line turns a stripe into ladder rungs** (the RSR's
  louvres again): the slat tops take the paint. The 296 Challenge stops the
  stripe at the vent and resumes behind it — a clean black gap — rather
  than painting through.
- **Judge text orientation from full-resolution crops, never from a
  contact-sheet tile.** The wing wordmark was "fixed" to the wrong
  orientation from a 480-px tile, then proved right on a full-res crop of
  the same render.
- **The Car Info / Car Model tabs ignore a bare `mouse_event` click** —
  move the cursor over the target first, then press.

## 12. The Lotus 79 additions (2026-09-17)

- **An unowned car still takes custom paint in the viewer.** The Car Info
  dialog says "License Required", but `car_<id>.tga` in the sim-created paint
  folder renders on Ctrl+R. Map first; buy later.
- **Which half is which side is per car.** The Lotus's LOWER half (y > 1259)
  is the car's LEFT side — the opposite of the Ray. Settle it from a top-down
  frame with the nose pointing one way: the side at the bottom of the frame
  is the LEFT side when the nose points left. (Heading left, the car's left
  hand points toward the bottom of the image and toward the camera in a
  level side view.) Getting this backwards once cost a re-read.
- **`probe_islands.py` flood labels are NAME + cell number** — a 1x1 flood
  named `4` renders "41". Name floods with letters, or read the trailing 1
  as the cell index.
- **A wing is a closed profile unwrapped in one island.** On the Lotus the
  top runs leading edge -> trailing edge along +x, and the rear face of the
  flap continues from the trailing edge at the OTHER end of the island.
  A band at the top-surface trailing edge was invisible from dead rear. Probe
  the chord with x bands and read them from a dead-rear and a dead-front frame.
- **Long walks exceed the bridge's 60 s.** A 12-frame walk with `--reload`
  took 65.5 s on 2026-10-24. Run `python tools/walk.py` in the background
  and wait for its `DONE 12 frames` line, or split the walk.
- `tools/template_layers.py` also accepts `Number Block Locations` /
  `Sponsor Block Locations` as block-layer names.

## The habit

1. Probe before you design, not after the third rebuild.
2. Read from a level camera.
3. Sample densely; a scrambled result usually means too few samples.
4. Write coverage and mapping into `docs/car-maps/<car>.md` immediately.
5. If a fix appears to do nothing, check the reload first.
6. Never re-derive something in this file. If you find yourself working it out
   again, it belongs here — add it.

## 13. The HPD ARX-01c additions (2026-09-17)

- **A template's Wire layer can be completely blank.** The HPD's has no green
  island outlines at all, so `tools/probe_islands.py` falls back to the Mask
  layer: connected components of its opaque area, eroded a texel so touching
  islands split. The HPD's Mask is also **inverted** — opaque over the
  non-paintable background — which the tool detects from the canvas border.
  Same indices, bboxes and masks either way, so every tool built on it works.
- **The single most productive probe on this car was a whole-texture labelled
  coordinate grid.** `<scratch>\coord.py`: tint every 128-texel cell in a
  4-colour checker, stamp its own `col,row` in it, plus the usual red
  texture-top / blue texture-left bars. One reload and a 12-frame walk then
  answer *any* "what texel is this point on the car" question, instead of a
  probe per question. On a car with 34 islands that is worth doing first.
- **Measure which islands mirror, don't assume the whole texture does.** Flip
  every island's mask about the measured row and see which island it lands on.
  On the HPD only 0, 1, 6 and 7 (plus self-symmetric 8) mirror; the
  engine-cover flanks, the wing, the endplates, the splitter and the cockpit
  fins are packed independently. A whole-half mirror would have splattered
  paint across all of them — hence `assets/hpd-body-mask.png`, the union of the
  islands that do mirror, committed and used to mask the mirrored layer.
- **+x is not always "forward on one side, rearward on the other".** The HPD
  is unwrapped as if from above: x longitudinal, y lateral from one centre row,
  and **+x REARWARD on BOTH flanks**. The right side renders ROTATE_180, which
  is what makes that consistent. Establish it from the coordinate grid read on
  a level left AND a level right view — the same `col,row` sequence reads nose
  to tail on both, upright on one and upside down on the other.
- **A TOP-DOWN FRAME LIES ABOUT TEXT ORIENTATION.** The logo slot 2 mark on the
  HPD's engine-cover flank read upside down from above and correct from a level
  side; acting on the top-down reading flipped it the wrong way and cost a pass.
  This is Rule 3a again, and it applies to *type*, not just to panel shape.
- **An island's bbox is not its visible area, and on some islands almost none
  of it is visible.** The HPD's islands 6/7 are 607×339 but only a narrow strip
  around the number block can be seen from outside; a sash drawn there never
  appeared. Flood the island and look before designing onto it.
- **A surface can be too thin to carry anything.** Probe the wing's chord with
  a 1×3 band probe and read it from a DEAD REAR frame: on the HPD the
  rear-facing band is a ~2 px edge, so a stripe there showed only as two specks
  at the endplate mounts. The Lotus's wing rear face was usable; this one is
  not. Measure it, don't assume the last car's answer.
- **Endplates can be different islands with different sizes.** The HPD's left
  endplate outer face is 111×160 texels (island 11), the right is 130×174
  (inside island 3). Each island also carries the *inner* face beside the outer
  one, so centring a mark on the island puts half of it on the wrong face.
  Find the outer-face sub-rect by reading a 2×2 / 6×3 grid from a level view of
  **each** side, then place per side.
- **`tools/checkblocks.py` is hardwired to the MX-5's number blocks** and
  reports a false FAIL on any other car. Use the build module's own guard.

## 14. The Spec Racer Ford additions (2026-09-27)

- **A template can ship several number-block configurations.** The SRF's PSD
  has three "Sponsor Number Package" groups (`Number Blocks config 1..3`), and
  `tools/template_layers.py` finds none of them (no layer is called "Number
  Blocks"). Outline all of them in different colours on one coordinate-grid
  reload and see which boxes the stamped number lands in — on this account
  the sim uses **config 3** (nose top, tail, rear quarters), not the door
  numbers of configs 1/2. Record which one, and re-probe if the package is
  ever changed in Paint Shop.
- **Two islands that meet on the car can disagree about x.** The SRF's
  lower front flank (island 12) is offset from the strip above it (island 14)
  by up to ~40 texels and renders at a different px/texel, and island 14's
  strip renders ~2.5× taller per row than island 12. A single texture-space
  parallelogram came out with two steps. Probe with X bands on every island
  the mark crosses (`tools/probe_bands.py <mod> <tpl> 14:X:.. 12:X:.. 1:X:..`),
  read the colour order across each seam from a level frame, write the
  offset and the scale ratios down, and evaluate the mark per texel in a
  common car frame (`_sash_flank()` in `src/team_srf.py`).
- **`tools/island_id_mask.py`** writes an island-ID PNG (each chosen island
  its own value), for a build that needs to treat islands differently —
  `tools/body_mask.py` only gives a union.
- **Find the tail centre from the vents.** The SRF tail face has no badge or
  light to centre on; its three slots are symmetric, and their midpoint (x
  458) is the car's centre on that face. It also leaks out of the island list
  (like the Ferrari hood), so it is drawn unmasked and checked on the render.

## 15. The Skip Barber Formula 2000 additions (2026-10-08)

- **A car can have two mirror rows.** The Skip Barber's side islands mirror at
  2695 (row 1347.5) but its centre islands (nose, scuttle, spine, tail) are each
  self-symmetric at 2691 (row 1345.5). Run `tools/mirror_row.py` on side PAIRS
  and on centre islands against THEMSELVES (`3/3 17/17`); use one row for the
  side mirror and the other for centre stripes.
- **A wing top can carry a forced sim decal.** The sim draws BFGoodrich on the
  rear-wing top over any paint. Paint the wing black and look before planning a
  wing wordmark.
- **Stamped numbers can default to different colours per block.** The nose
  number stamped dark, the two endplate numbers white — invisible on white
  panels until you set the Car Number chips. Look at every stamp.
- **A tapering panel defeats a constant-width centre stripe.** The engine-cover
  spine narrows from 219 to 38 rows. Read its half-width per column with
  `tools/island_runs.py`, scale the band set to stay inside it, and carry the
  end width onward — jumping back to full width on the next panel read as
  broken blocks from dead rear.
- **The visible part of a flank can end above the island's edge.** A sidepod
  top's rounded inboard edge hid the lowest ~40 rows of the tub flank from a
  level side; a wordmark sized to the island bbox lost its lower third. Read a
  Y ruler from the level view.
- **3D hardware sits on the paint.** A nose latch (its own small island) and a
  mirror-stalk foot both landed on marks. They show only on the render.
- **The car viewer's 3D pane can collapse to zero height** after a Car Info →
  Car Model tab switch. Closing the dialog and reopening the car fixes it.

## 16. The Aston Martin Vantage GT3 EVO additions (2026-09-28)

- **Check every number block for a mesh before panelling it.** The Aston's
  PSD has one `Number Blocks` layer with six blocks; two of them (N1, N3) sit
  on texture no mesh uses (`tools/island_runs.py` returns only background
  there) and the sim never stamps them. The magenta-block walk found the four
  live ones in one reload.
- **A leaky island can also be mapped off-centre.** The Aston's rear deck
  leaks out of the island list like the Ferrari's hood, and on top of that its
  car centre is NOT the texture centre row: a Y-band ruler (20-texel bands,
  labelled) read from a true dead rear against the badge and the deck's own
  edges put the centre at row ~1248 ahead of a seam at x ~1700 and ~1258
  behind it, where the body's centre row is 1260. A stripe on 1260 jogged at
  the seam. Measure the centre on every leaky panel; do not inherit it.
- **`tools/body_mask.py ... leak:x,y,w,h`** adds the texels of a rect that
  belong to no listed island, so a build can paint a leaky panel through a
  committed mask without touching the real islands packed beside it.
- **An open rear window is a hole, not glass to paint round.** The stripe
  ends at the roof's rear edge and resumes behind the window frame; the
  frame's inside (x 1480..1550 on the Aston) read as a floating patch.
- **A wing's top can be the low-x half of its island.** Band the chord and read
  it from above before placing the wordmark: x 1960 on the Aston was the
  underside and rendered nothing.
- A `+` wheel tick zooms the car viewer IN; ticks are
  sometimes swallowed — check the frame.
