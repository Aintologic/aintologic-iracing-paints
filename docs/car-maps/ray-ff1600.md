# Panel map — Ray FF1600

- iRacing car ID: **163** (Car Info panel shows `#163`, verified 2026-09-14)
- Template: your own iRacing template — `163_template_GR22.zip` ->
  **`Ray FF1600.psd`**, 2048x2048. (The zip code is `GR22` — the Ray GR-series
  chassis — but the PSD names the car, so this is the right file.) Layer names
  differ again from the F4 and the RSR: `base` (lower case), `Car Mandatory`
  (space, not underscore), `Car_decal`, `Number Blocks`, `Sponsor Blocks`,
  `Wire`, `Mask`, plus a `Car Patterns` group and a `Custom Spec Map` group.
  `tools/template_layers.py` now matches layer names case- and
  separator-insensitively because of this.
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\raygr22\` (existed and
  was empty).
- Paint file: `car_<id>.tga` (your iRacing customer ID).
- Build: `src/team_ray.py`.
- Status: **LOCKED as `releases/ray-ff1600/v1.0-2026-09-14/`** (approved on the
  render 2026-09-14; on-track verification pending — a change is a new version,
  never an edit of v1.0).

**Chassis note: a Formula Ford has NO WINGS.** There are no endplates, so the
F4's logo slot 1 placement does not exist here, and there is no rear-wing or
front-wing surface to leave black. The paintable car is: a long pointed nose
cone, a narrow tub with a cockpit surround, two low sidepods, a rear body that
tapers to the tail, and a roll hoop.

Every row below was read off the car in iRacing's car viewer from labelled
probes (`tools/probe_islands.py`, 2026-09-14) unless it says otherwise.

## Template anchor blocks (from the PSD layers)

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| N1 | 1688 | 625 | 106 | 95 | **RIGHT** rear body side, ahead of the rear wheel (island 6) |
| N2 | 454 | 974 | 95 | 106 | nose top, astride the centre line, just behind the tip (island 4) |
| N3 | 1688 | 1332 | 106 | 95 | **LEFT** rear body side (island 5, the mirror of 6) |

Sponsor blocks (magenta, the template author's suggested spots):
`(964,237,433,52)` R sidepod + `(964,1766,433,52)` L; `(1088,618,323,61)` R
tub flank + `(1007,1373,323,62)` L; `(380,961,39,132)` and `(282,969,91,115)`
on the nose tip.

The sim's own `Car_decal` layer covers `(441,43)..(2045,1740)` — check what it
already draws before adding safety furniture.

## THE RULE OF THIS UV — mirror about texture row 1026

**Left side = right side reflected about row 1026: `left y = 2052 - right y`,
x identical.** Measured by maximising mask overlap between twelve island pairs
(`6/5, 2/1, 13/12, 15/14, 17/16, 20/19, 23/22, 28/27, 31/30, 11/10, 32/33,
39/40`) over candidate mirror rows: every pair peaks at 2051 or 2052 with
98.4–100 % overlap. The number blocks say 2051 exactly (625+1426 = 719+1332);
**2052 is used in the build** and the 1-texel difference is invisible.

**Islands with y < 1026 are the car's RIGHT side.** Proved from a dead-front
frame: the nose island's row-1 cells (y 894..1026) render on the viewer's LEFT
half of the nose, which is the car's right.

From a level RIGHT-side view the right islands render **ROTATE_180**:
texture **+x = REARWARD**, **+y = UP the car**. The left islands read upright.
So `src/team_ray.py` draws everything in RIGHT texture space, mirrors the
geometry in one operation, and composites text afterwards — ROTATE_180 on the
right, upright at the mirrored row on the left (playbook Rule 4).

**One island leaks.** The LEFT sidepod's green outline has a gap in the
template wire, so its region merges with the background and it does **not**
appear in the island list. It is still painted correctly, because the whole
right half (rows 6..1026) is mirrored as a block. Do not try to mask to it.

## Islands (RIGHT side unless noted; left = mirror). Edges per column in `src/ray_islands.py`

Indices are the ones `python tools/probe_islands.py team_ray <tpl> list` prints
(sorted by area). Names are the ones used in `src/ray_islands.py`.

| idx | name | bbox | what it is |
|---|---|---|---|
| 7 | NOSE_TIP | (33,908,390,237) | the nose cone's tip, pointed at x 33 (y 1024..1024) and widening to 911..1141 by x 393. Symmetric about 1026. |
| 4 | NOSE | (426,894,506,265) | the nose cone top and upper sides, near-constant 246 rows tall, symmetric about 1026. **N2 sits in it at x 454..549.** The top ridge is row 1026; each ~33 rows out from it is one band further down the nose's side. |
| 8 | COWL | (879,944,416,165) | the scuttle in front of the cockpit — pointed at x 879, widening rearward. Mostly hidden under the dash; only its front reads. |
| 2 | TUB | (528,434,813,351) | the tub / cockpit flank — the biggest side-facing panel on the car. Visible band ≈ y 540..730. Its top edge steps from 434 to 594 at x≈848 because island 13 takes over above it from there. **Island 13's bbox lives inside island 2's bbox.** |
| 13 | MID | (824,434,517,161) | the strip above the tub flank aft of x 824 (cockpit rim / shoulder) |
| 0 | POD | (893,12,886,492) | the **RIGHT sidepod**, wrapping: rows ~319..500 are the pod's TOP (read from above), rows ~196..319 the OUTER FACE (read from a level side), rows 12..196 not visible from outside. Front edge ≈ x 900..980; the bottom edge steps up after x≈1421, so the pod's usable length is x 900..1480. |
| 6 | REAR | (1344,611,701,229) | the rear body side, behind the cockpit — carries N1 at x 1688..1794, y 625..720 |
| 15 | REAR_LOW | (1345,527,333,90) | the panel below the rear body side |
| 17 | SILL | (1426,235,355,90) | the sill / lower rear body edge |
| 20 | DECK | (1359,897,487,128) | the **rear deck / tail spine, right half**: a tapering sliver whose HIGH-y edge is the car's centre line (1024 at x 1359) and which narrows to a point at x≈1843. Island 19 is its mirror. |
| 11 | NOSE_LOW | (70,436,455,165) | the lower nose side |
| 9 | HOOP | (548,117,302,211) | roll-hoop fairing / headrest surround |
| 24 | — | (287,286,232,97) | mirror housing (probed white, reads on the stalk) |
| 3 | — | (37,1867,814,162) | covered by `Car Mandatory` (grey in the overview) — not paintable |
| 23, 28, 31, 25, 35, 21, 26, 38, 46 | — | — | probed 2026-09-14; nothing readable landed on a surface you look at from the level / top sweeps. Leave black. |

Wheels, suspension, floor, exhaust, engine, cage: `Car Mandatory`, not paintable.

## Viewer loop — Ray specifics (2026-09-14)

- `tools/view2.ps1`, `tools/walk.ps1`, `tools/walk_top.ps1`,
  `tools/contact_sheet.py` and `tools/zoom.py` all work unchanged. Window
  1728 px wide.
- **Ctrl+R does NOT reset the camera pose** on this car either — it is
  cumulative, and you drive it too. Sweep and pick, never assume a pose.
- A horizontal drag of ~55 px is roughly 25–30°, non-linear; `-DragY -600` is
  always level, `+600` always top-down.
- The car is small in the pane at the default zoom: `tools/view2.ps1 -Wheel 4`
  fills it for a level side; back out ~3 ticks for a top-down that shows the
  whole car.
- Reading the probes: on a level RIGHT-side view every label is upside down
  (the islands render ROTATE_180). Zoom before concluding anything about
  order — a reversed reading order is the rotation, not a mirrored UV.

## New tools written for this car (reusable)

- **`tools/probe_islands.py`** — labelled-cell probe **masked to a real UV
  island**, plus a `list` mode that inventories every island the template's
  green wire outlines enclose. Needed here because island 13 sits inside
  island 2's bbox and islands 17 and 32 sit inside island 0's bbox: a plain
  rect probe paints those neighbours too and they render somewhere else.
- **`tools/island_edges.py`** — generalises `tools/f4_islands_gen.py`: writes a
  per-column `(y_top, y_bottom)` table for any named set of islands, so
  artwork can hang off a sloping island edge. `src/ray_islands.py` is its
  output for this car.
- `tools/template_layers.py` now finds layers case- and
  separator-insensitively (`Car Mandatory` vs `Car_Mandatory`, `base` vs
  `Base`).

## How to edit this car later — the breadcrumbs (v1.0, 2026-09-14)

**Locked:** `releases/ray-ff1600/v1.0-2026-09-14/` (approved on the render;
on track pending). Restore with
`python src/restore.py v1.0-2026-09-14 --car ray-ff1600`. Do not change the
design on a whim; anything experimental goes on a branch and a new release
folder, never over v1.0.

**Build entrypoint:** `python src/team_ray.py` (writes `car_<id>.tga` +
`car_spec_<id>.tga` into `%USERPROFILE%\Documents\iRacing\paint\raygr22\`;
`--here` for the cwd, `--png` for a flat PNG, `--no-spec`). Personalize it with
`--id <your iRacing customer ID>`, `--driver "<name>"` (the driver strip),
`--logo1 <image>` (logo slot 1) and `--logo2 <image>` (logo slot 2); with no
flags the output carries a neutral `YOUR LOGO` placeholder in each slot and a
blank driver strip. It imports `src/teamscheme.py` (palette + marks),
`src/sponsors.py` (logo slot 2, driver strip, logo slot 1 loader) and
`src/ray_islands.py` (the island edge table, generated from the template by
`tools/island_edges.py`). **The island edge table is not shipped** — regenerate
it from your own iRacing template with `tools/island_edges.py` before the first
build. Rebuilding with the same Pillow/font reproduces the release bytes
(`06b10eb4…` / `82edcb46…`, checked at lock time); on another Pillow/font it
will not — the release TGA is the lock.

**Every placement is a constant at the top of `src/team_ray.py`, in RIGHT
texture coordinates (y < 1026).** Side geometry is drawn once on the right and
mirrored (`mirror_geometry`, rows 6..1026 → 1026..2046); text is composited
afterwards (`place`, ROTATE_180 on the right). Centre-line islands (nose tip,
nose, scuttle) are symmetric about row 1026 and drawn once.

### ⚠ THE ONE DELIBERATE ASYMMETRY — do not "correct" it

**The AÏNTOLOGIC side wordmark is intentionally NOT mirrored at identical
coordinates. LEFT `TUB_WM_CXY` x = 1095. RIGHT `TUB_WM_CXY_R` x = 1330.**

A fairing blister stands proud of the RIGHT flank over texture x ≈ 800..1090;
there is no equivalent obstruction on the left, so a mirrored placement buries
letters behind it. The left side was approved where it is, under the rule for
this car (2026-09-14): *do not force exact mirrored coordinates side-to-side on
this car; optimise each side for visible fit.* The right-side mark is pushed
rearward until its forward edge sits at 1095 — exactly the blister's rear edge
— which carries its aft half across the TUB → REAR island seam;
`place_across_seam()` cuts it at `TUB_REAR_SEAM` 1342 and steps the aft half by
`TUB_REAR_DY` 5.

Record of both sides:
`releases/ray-ff1600/v1.0-2026-09-14/closeups-wordmark-asymmetry.jpg`.
**A future rebuild that restores matching coordinates is a regression, not a
fix.**

## The design — locked v1.0 (2026-09-14)

Everything is a constant at the top of `src/team_ray.py`, in RIGHT texture
coordinates.

| element | constant(s) | lands on |
|---|---|---|
| nose centre stripes | `NOSE_X` (96..930), `NOSE_CS` (46, 23, 6), `NOSE_TAPER_X` 300 | NOSE_TIP + NOSE, centred on row 1026; the three bands **taper into the tip** instead of running off the point |
| nose number panel | `NOSE_NUM` = N2 + 8, `NOSE_NUM_GAP` 14 | NOSE; the stamp lands centred on it |
| AÏ roundel node | `NOSE_BADGE_D` 132, `NOSE_BADGE_CX` 742, `RING_GAP` 6, `RING_W` 13, art ROTATE_270 so it reads from the FRONT | NOSE, behind the number panel |
| scuttle stripes | `COWL_X` (940..1180), `COWL_CS` (30, 15, 5) | COWL, between the nose and the cockpit |
| sidepod sash | `POD_SASH` (xc 1046, tilt 0.30, 54/27/6), `POD_SASH_Y` (30..500) | POD — crosses the pod TOP and wraps down the OUTER FACE, leaning top-forward |
| rear deck stripes | `DECK_X` (1372..1826), `DECK_CS` (gap 3, orange 17, mid 4, white 9), hung off DECK's centre-line (high-y) edge per column | DECK + its mirror: twin papaya lines down the tail spine, tapering with it |
| AÏNTOLOGIC — **the two sides are NOT at the same x** | `TUB_WM_W` 470; LEFT `TUB_WM_CXY` (1095, 642); RIGHT `TUB_WM_CXY_R` (1330, 642) with `TUB_REAR_SEAM` 1342 and `TUB_REAR_DY` 5 | LEFT: TUB flank, approved there 2026-09-14. RIGHT: pushed rearward past the fairing blister, which takes it across the TUB → REAR island seam; `place_across_seam()` cuts it at 1342 and steps the aft half. See the blister note below. |
| logo slot 2 | `POD_LOGO2_W` 250, `POD_LOGO2_CXY` (1340, 262) | POD outer face |
| logo slot 1 | `POD_LOGO1_D` 92, `POD_LOGO1_CXY` (1332, 420) | **POD TOP**, aft of the sash — the Ray's clean, flat, readable secondary panel (the F4's endplates do not exist on a Formula Ford) |
| driver strip | `TUB_DRIVER_W` 118, `TUB_DRIVER_XY` (1180, 700) | TUB, cockpit rim |
| rear number panels | N1 / N3 + `NUM_MARGIN` 8 | rear body sides |

**Not painted and why:** the roll hoop and headrest (black, restraint); the
sills and lower rear panels; the nose underside; the mirror housings; the
tail's cut-off rear face (it is mostly engine and gearbox from behind).

## Spec map — VALIDATED 2026-09-14, B3 unchanged

A/B at one lit pose, spec TGA present vs parked
(`releases/ray-ff1600/v1.0-2026-09-14/closeups-spec-ab.jpg`), measured on a
patch of plain bodywork on the engine-cover crown: with B3 it reads an even
satin (mean RGB 54/48/44, sd 14.5); with no spec map the same patch blows out
to a specular hotspot (mean 64/60/61, sd 58.8) and the black reads
navy-glossy. No ladder was needed on this car. The sim writes
`car_spec_<id>.mip` a couple of seconds after the TGA lands; that .mip is
what Trading Paints takes.

**Number chip setting:** all three Car Number chips `#0C0C0D` in Paint Shop →
Paint Your Car (per car).

**To probe again:** `python tools/probe_islands.py team_ray <tpl-dir> list`,
then `... 4:E:10,1 2:B:5,6 ...` (masked island grids), `tools/probe_ruler.py`
(numbered bands, centre lines and where a blister sits),
`tools/island_edges.py` to regenerate `src/ray_islands.py`, and
`tools/mirror_row.py` to re-measure the mirror; then `tools/walk.ps1` /
`tools/walk_top.ps1` + `tools/contact_sheet.py` + `tools/zoom.py`, read from
level sides / dead front / dead rear / top. `tools/template_layers.py <zip>
<dir>` regenerates the wire / block pictures.

## Tried / to remember

- Painting only the y < 1026 islands leaves the LEFT side of the car entirely
  black. That is the mirror working as designed, not a missing island — two
  early sweeps were read as "island 6 renders nothing" before the camera had
  been swung to the other side.
- The first nose stripe recipe (34/17/5) was invisible from a level side
  because the nose top is narrow; 46/23/6 wraps far enough onto the nose
  shoulders to read from the side as well as from above and dead front.
- The nose stripe must taper: at x < ~300 the tip island is narrower than the
  full band set, so a constant-width stripe swallows the whole tip.
- **The mirror fairing eats the middle of the tub flank.** Measured with
  `tools/probe_ruler.py team_ray TUB:528,560,812,180:X:50` read from a level
  right view: the blister that carries the mirror stands proud of the flank
  and occludes texture **x ≈ 838..1078** at the wordmark's rows (~655 and up).
  The clean runs either side are 528..838 (310 texels) forward and 1078..1340
  (262) rearward. The AÏNTOLOGIC wordmark is 470 texels wide, so **no
  full-size placement on this island is completely clear of it** — 1095 is as
  far rearward as the island allows, and leaves only the trailing letters
  grazing the fairing's shoulder. Getting it fully clear needs either a
  smaller mark (~260 wide, centred in the rear panel) or a different panel.
  There is no vertical escape: the wordmark's rows (596..688) already sit on
  the island's lower edge (594).
- **So the right-side wordmark crosses the TUB → REAR seam, and the two sides
  are deliberately NOT mirrored** (the rule for this car: do not force exact
  mirrored coordinates on this car; optimise each side for visible fit).
  LEFT stays at 1095 — it was approved there. RIGHT is at 1330, which puts its
  forward edge at 1095, exactly on the blister's rear edge, and its aft half
  on island REAR.
- **The seam step had to be tuned on the render, not taken from the edge
  table.** The island edges say REAR's rows are +21 at the join (TUB 599..754
  at x 1340, REAR 620..777 at x 1344, heights 155 / 157). Drawing the aft half
  at +21 put it ~16 texels too HIGH on the car — a plainly visible step
  through the middle of the word. `TUB_REAR_DY = 5` lines the two halves up.
  The bbox-derived offset is not the rendered offset; measure it on the car.
- Anything else that has to span x ≈ 1342 on the flank needs the same
  treatment — or a fitted per-island affine (`tools/probe_affine.py` +
  `fit_affine.py`), which is the proper tool if a future mark needs to land
  exactly across it.
