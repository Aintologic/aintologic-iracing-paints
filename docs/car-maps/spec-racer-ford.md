# SCCA Spec Racer Ford (#23) — panel map

Status: **approved on track 2026-09-28** (tested, accepted and raced —
started 26th, finished 4th) and **locked as `v1.0`**. Approved as first built,
with no changes. Any pixel change is a v1.1, never an edit of v1.0.
Spec is the B3 "Satin-True" set carried over without a per-car A/B.

## Identity

| | |
|---|---|
| car id | **#23** — read in Car Info, the dialog is titled **"Car Info: SCCA Spec Racer Ford"** |
| template | your iRacing SRF template `23_template_SRF.zip` → **`Spec Racer.psd`**, 2048×2048 — the only SRF / Spec Racer template iRacing ships |
| paint folder | `%USERPROFILE%\Documents\iRacing\paint\specracer\` (created by the sim) |
| file | `car_<id>.tga` — the build writes one paint for the iRacing customer ID you pass with `--id` |
| build | `src/team_srf.py` |
| release | locked as `v1.0` once approved |

This is the older, open-cockpit SRF with the tall roll hoop (the car iRacing
ships as "SCCA Spec Racer Ford"), not the Gen 3.

The generator ships this as an example scheme (papaya / black / white). You
personalize it with your own iRacing customer ID (`--id`), driver name
(`--driver`) and two logo images (`--logo1`, `--logo2`); with no flags the
output carries a neutral `YOUR LOGO` placeholder in both logo slots and a blank
driver strip.

## The rule of this UV

Mirror-symmetric about texture row **1183.5**:

    right y = 2367 − left y,  x identical

Measured by mask correlation on eleven island pairs (1/0, 2/3, 6/7, 9/8,
12/13, 14/15, 18/17, 20/19, 22/21, 26/25, 30/29), all 98.8–99.9 % overlap,
median 2367 (`tools/mirror_row.py <tpl> 2355 2380 ...`).

- **rows > 1183 = the car's LEFT side**, rendered **UPRIGHT** from a level left view
- **rows < 1183 = the car's RIGHT side**, rendered **ROTATE_180**
- **on BOTH sides texture +x is REARWARD** — unwrapped as if from above, like
  the HPD. Proved with a whole-texture 128-texel coordinate grid: the left
  flank reads `1,15 → 13,14` nose to tail upright, the right flank reads the
  same columns upside down.
- From the centre row outward each side goes: centre island → shoulder (the
  broad fender / cockpit-side top surface) → a crease → the vertical flank.

So side geometry is drawn once in LEFT texture space and mirrored; text is
composited afterwards with `place()` (playbook Rule 4). The template's Mask
layer is **inverted** (opaque over the background); `tools/probe_islands.py`
handles it. The Wire layer has green outlines this time.

## Islands that matter

`python tools/probe_islands.py team_srf <tpl> list` (73 islands).

| idx | bbox (x,y,w,h) | what it is |
|---|---|---|
| **5** | `(10,935,330,498)` | **nose front face**, x 10 = chin → 338 = top edge; y lateral; the radiator mouth is a hole in it |
| **10** | `(352,1003,404,362)` | **nose top** between the front fenders, pointed at x 352. Carries the nose number (config 3) on the centre line |
| 11 | `(759,967,525,433)` | cockpit surround (the opening is its hole); 29/30/33/34/35/42/48/50/55 are interior bits inside its bbox |
| **4** | `(1326,998,561,371)` | **rear deck / engine cover**, ~250 texels wide at x 1712. A shut line at x 1528..1542 is its own thin islands (59/60) |
| — | `(~40,16,~830,250)` | **tail face** — NOT in the island list (its green outline leaks into the background, like the Ferrari's hood). Three vent slots at x 75..195, 345..572, 722..841, y 78..121 (islands 57/67, 40/44, 58/68). Tail centre x **458** by slot symmetry. Renders upright from dead rear |
| 1 / 0 | `(74,1260,781,434)` / `(75,674,780,434)` | LEFT / RIGHT **front shoulder**: front-fender top → cockpit side, x 75..855 |
| 6 / 7 | `(810,1420,521,285)` / `(810,662,521,286)` | shoulder beside the cockpit |
| 2 / 3 | `(1325,1372,537,332)` / `(1325,664,537,331)` | **rear fender tops** (shoulder over the rear wheel) — logo slot 2 |
| 14 / 15 | `(13,1768,841,270)` / `(13,329,841,271)` | front-fender side face + a thin strip under the crease above island 12 + the panel strip at x 817..853 |
| 12 / 13 | `(485,1806,329,219)` / `(485,343,329,219)` | lower flank ahead of the door (behind the front wheel) — the sash |
| **9 / 8** | `(857,1772,566,258)` / `(856,337,567,259)` | **the door** — the flat vertical panel between the wheels. AÏNTOLOGIC |
| 18 / 17 | `(1337,1735,513,171)` / `(1337,462,513,171)` | rear quarter behind the rear wheel — carries the side number |

The grey strip along the bottom of each flank (the sill) and the undertray are
**not on this texture** — they render grey whatever the paint is.

## Number blocks — three configurations, the sim uses config 3

The PSD has three "Sponsor Number Package" groups, each with its own
`Number Blocks config N` layer. Probed: all three outlined in different colours
(1 magenta, 2 orange, 3 green) on the coordinate grid — the stamped number
rendered inside the **green** boxes only.

| block | config 3 rect | where |
|---|---|---|
| REAR | `(208,57,123,82)` | tail face, left of centre (same in all configs) |
| NOSE | `(572,1100,118,167)` | nose top, ON the centre line |
| SIDE_L | `(1683,1745,129,93)` | left rear quarter, behind the rear wheel |
| SIDE_R | `(1683,530,129,93)` | right rear quarter |

Configs 1 and 2 put the side number on the door. **If you change the number
package in Paint Shop, re-probe — the door wordmark would collide.**
`src/team_srf.py` keeps all three configs in `NB_CONFIGS`; the guard checks
config 3. `tools/checkblocks.py` is MX-5-only — use the build's guard.

## The sash — three islands, three mappings

Measured with `tools/probe_bands.py team_srf <tpl> 14:X:480:880:20
12:X:480:880:20 1:X:480:880:20`, read from a level left view:

- island 1 (shoulder) and island 14 (the strip under the crease) line up in
  x across the crease;
- island 14's strip is only ~45 rows tall in texture but renders ~2.5× taller
  per row than island 12 (≈0.85 vs 0.34 px/row at the viewer's working zoom);
- island 12 is **offset in x** from island 14: the same car position is
  island-14 x = x12 + 0.19 × (730 − x12), and it renders 0.46 px/texel
  against 0.54.

**Tried and rejected:** one texture-space parallelogram through all three
islands (v1). The render showed two steps — one at the crease and a bigger
one at the 14/12 seam. The build now keeps a texture tilt on the shoulder
(it reads from above) and evaluates the flank per texel in a common car
frame, so the band is one straight leaning line from a level side
(`_sash_flank()`; island IDs in `assets/srf-sash-islands.png`).

**Tried and rejected:** shoulder tilt 0.22 — from above the two sash crowns
made a flat transverse bar through the nose number, a "+" with the centre
stripe. 0.45 makes them a forward chevron pointing at the number.

## Where everything is placed (v1.0)

All named constants at the top of `src/team_srf.py`.

- **Centre stripes** white | papaya | white (34 / 17 / 6) about row 1183.5:
  nose face x 10..339, nose top x 352..556 up to the nose number panel;
  deck x 1326..1885 through the **AÏ roundel node** (d 150 at x 1712, ring gap
  6, ring 12), letters reading from behind. Masked to islands 5/10/4
  (`assets/srf-centre-mask.png`), so the pointed nose top tapers them.
- **The node is on the deck, not the nose** — the nose number sits on the
  centre line of the nose top (the RSR / Ferrari lesson).
- **Front-fender sash** (44 / 22 / 7), crease centre x 640, just behind the
  front wheel, shoulder tilt 0.45, flank lean 0.30 (screen).
- **AÏNTOLOGIC** 460 px on each door, centred (1126, 1905) LEFT space.
- **Driver strip** (your `--driver` name) 120 px at (880, 1826), door
  top-front; blank with no `--driver`.
- **Logo slot 2** (`--logo2`) 300 px on each rear fender top, centred
  (1600, 1580) LEFT space.
- **Tail face:** AÏNTOLOGIC 210 px above the centre slot (458, 47); **logo
  slot 1** (`--logo1`) 96 px at (647, 92) — the mirror spot of the rear number
  panel, between the centre and right slots.
- **Number panels** white on all four config-3 blocks, margin 8.
- **Spec:** the B3 "Satin-True" values, carried over; no per-car A/B.

## Traps on this car

1. **Three number configurations.** Probe which one the sim stamps; don't
   trust the first layer you find.
2. **The tail face is missing from the island list** (leaky outline). Draw
   on it unmasked, check it on the render.
3. **The front-fender side is three islands with three different mappings**
   (see "The sash"). Anything that must be continuous across the crease or the
   14/12 seam needs the car-frame treatment.
4. **The sill and undertray are not paintable** — the grey strip is the sim's.
5. The 12-frame `walk.ps1` takes ~110 s here — run it detached and poll.

## How to edit this car later

1. `python src/team_srf.py` writes colour + spec and refuses to write if
   artwork lands in a config-3 number block.
2. Every placement is a named constant at the top of `src/team_srf.py`. Side
   placements are LEFT texture space (y > 1183); `place()` does the right.
3. Re-probe: extract your `23_template_SRF.zip` to a scratch folder `<tpl>`,
   run `python tools/template_layers.py <zip> <tpl>`, then
   `python tools/probe_islands.py team_srf <tpl> list`; for any
   "which texel is this", `python tools/coord_grid.py team_srf 128`.
4. Masks are **not shipped** — regenerate them from your own template with:
   `python tools/body_mask.py <tpl> assets/srf-centre-mask.png 5 10 4`,
   `python tools/body_mask.py <tpl> assets/srf-side-mask.png 0 1 6 7 2 3 12 13 14 15 9 8 18 17`,
   `python tools/island_id_mask.py <tpl> assets/srf-sash-islands.png 1=1 14=14 12=12`.

## Known and accepted in v1.0

- Sash seam at the 14/12 join: straight to within a few px from a level
  left view; right side checked from its level view only.
- The px/row and px/texel ratios in the sash car frame were read at one zoom
  from one level-left frame; they are ratios, so zoom-independent, but a
  3/4 view may show residual bend.
- Spec map not A/B-validated on this car (accepted on track).
- No safety furniture added beyond the driver strip — the sim's own decal
  layer draws small marks near the rear wheels; not yet reviewed.
