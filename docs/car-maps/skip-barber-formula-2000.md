# Skip Barber Formula 2000 (#1) — panel map

Status: **Approved on the render 2026-10-08** ("approved", as first shown — no
changes) and the ready-made paint is in `paints/skip-barber-formula-2000/`. On track pending — the account
shows "License Required". Any pixel change is a v1.1, never an edit of v1.0.
Spec is the B3 "Satin-True" set carried over without a per-car A/B.

**Set all three Car Number chips to `#0C0C0D`** in Paint Shop. By default the
two rear-endplate numbers stamp white and vanish on the white number panels;
the nose number stamps dark.

Accepted at approval: the dead-rear view carries only the centre stripe — the
rear is gearbox, oil tank and exhaust, the rear-wing top carries the sim's own
**BFGoodrich** decal on any paint (probed on a black wing), and the endplates
are edge-on and carry the numbers. Same finding as the HPD.

Milestone-1 renders and probe sheets:
`paints/skip-barber-formula-2000/wip-2026-10-08-m1/`.

## Identity

| | |
|---|---|
| car id | **#1** — Car Info read 2026-10-08, dialog titled **"Car Info: Skip Barber Formula 2000"**, `#1` top right (`car-info-1.jpg`). The account shows **"License Required"**; the viewer takes custom paint anyway (Lotus lesson) |
| template | your own iRacing Skip Barber template, `1_template_SBRS.zip` → **`Formula Skip Barber 2000.psd`**, 2048×2048 — the only Skip Barber template in the iRacing collection. Extract it to a scratch folder to work from |
| paint folder | `%USERPROFILE%\Documents\iRacing\paint\rt2000\` — created by the sim when you first open the car; a coordinate grid written there rendered on the car, which settles it |
| file | `car_<id>.tga` — named for your iRacing customer ID (`--id`). The build writes this one file |
| build | `src/team_sbf2000.py` |
| layers | `Paintable Area` (`BaseColour`, `Car Patterns`, `Pitbox`, `Car_Decal`), `Turn Off Before Exporting TGA` (`Car_Mandatory`, `Sponsor Blocks`, `Number Blocks`, `license`, `Mask`, `Wire`), `Custom Spec Map`. `tools/template_layers.py` reads it unchanged |

**Chassis:** a 1990s-style Formula 2000 school car — long pointed nose with a
nose-top number, small front wing on two little endplates, a narrow tub with
a tall roll hoop, two low sidepods (flat top + vertical face, a horizontal
groove across the face's rear half), an engine-cover spine that tapers behind
the hoop into a tail cover with three vent slots, exposed gearbox and exhaust
at the rear, and a small rear wing whose two endplates carry the side/rear
numbers. **It has endplates, but they are full**: each outer face is 126×169
texels and the number block takes 123×87 of it.

## The rule of this UV

**Side islands mirror about texture row 1347.5:** `right y = 2695 − left y`,
`x` identical. Mask correlation (`tools/mirror_row.py`): 9/8 at 2695 with
100.0 % overlap; 29/27 2694, 31/30 2696, 33/32 2696, 37/40 2696, 38/39 2695,
59/60 2695 (98–100 %).

**The centre islands are symmetric about row 1345.5 (2691), not 1347.5.**
Islands 3, 6, 17, 18 each peak at 2691 against themselves (99.7–99.9 %), and so
do the near-centre pairs 28/26 and 54/55. The two mirrors differ by 4 texels.
Centre marks use `CENTRE = 1345.5`; side marks use `MIRROR = 2695`. A white
line drawn on row 1345 runs true down the nose and the spine on the render.

- **rows > 1347 = the car's LEFT side**, upright from a level left view;
  **rows < 1347 = RIGHT**, ROTATE_180 from a level right view.
- **On BOTH sides texture +x is REARWARD** — the coordinate grid reads
  `1,13 → 12,12` nose to tail upright on the left and the same columns upside
  down on the right (`probe-coord-grid-128.jpg`). Settled again from a top-down
  frame with the nose pointing left: the lower-half pod top (island 8) sat at
  the bottom of the frame, which is the car's left side.
- **Engine-cover side panels sit outside the main mirror:** 15 (left, y 208..387)
  and 16 (right, y 12..191) mirror each other locally, `right y = 398 − left y`
  (99.5 %). On the left +y runs down the panel (spine → outer edge); on the
  right it runs up.

## Islands that matter

`python tools/probe_islands.py team_sbf2000 <tpl> list` (79 islands). Named by
a 1×1 flood probe (`probe-island-flood.jpg`) and band rulers
(`probe-rulers.jpg`).

| idx | bbox (x,y,w,h) | what it is |
|---|---|---|
| **47** | `(22,1294,88,104)` | nose tip cap, pointed at x 22 |
| **3** | `(113,1231,606,230)` | **nose top**. Carries N3 on the centre line. At x 650 it narrows to rows 1279..1412 and island 6 wraps round it — the two share x and y (Y bands run straight across the curved seam) |
| 96 | `(671,1337,79,18)` | a strip on the centre line under the **chrome nose latch** (3D, stands over the paint; it covers x ~671..749) |
| **6** | `(513,1208,616,276)` | scuttle ahead of the cockpit + cockpit surround (the opening starts at x ~920 on the centre line) |
| **17** | `(1405,1235,426,222)` | **engine-cover spine** behind the roll hoop; filler cap island 93 `(1427,1327,45,38)`. **Tapers** from rows 1236..1455 at x 1480 to 1326..1364 at x 1830 |
| **18** | `(1834,1224,204,243)` | tail cover; three vent slots on the centre line at x 1926..1941, 1957..1972, 1987..2002 |
| 26 / 28 | `(1531,1378,300,92)` / `(1531,1222,300,92)` | strips beside the narrow rear of the spine (left / right) |
| **2 / 0** | `(511,1492,1320,174)` / `(511,874,1320,331)` | **tub flank**, left / right. Visible side from the cockpit rim (~1530 at x 1150, ~1500 at x 1500) down to ~1625 above the pod; rows 1625..1665 hide behind the pod top's rounded inboard edge. Island 0 also takes the right **lower front flank** (rows 875..995) |
| (leak) | left rows ~1697..1865, x 511..~1130 | **left lower front flank** — its outline is open, not in the list. Mirror of island 0's lower part |
| **8 / 9** | `(1091,1676,636,161)` / `(1091,860,636,160)` | **sidepod top**, left / right. Row 1676 = inboard edge, ~1810 = outer edge |
| **5** / (leak) | `(1138,1832,590,201)` / right rows ~663..863 | **sidepod face**, left / right (the right one leaks). Straight face from x ~1190 (rounded front 1138..1190) to ~1700. A wire seam = the 3D **groove** across it at rows ~1885..1915 from x ~1400 rearward; below it 1917..2030 at x 1550, 1926..1996 at x 1650. Islands 8 and 5 share texture x (bands line up across the ~21-row unmapped seam) |
| **15 / 16** | `(1021,208,723,179)` / `(1021,12,723,179)` | engine-cover side panels, left / right; local mirror 398 |
| **24 / 25** | `(435,257,126,169)` / `(863,256,126,169)` | **rear-wing endplate OUTER faces**, left / right; N1 / N2 fill them |
| 21 / 22 | `(725,254,130,174)` / `(574,256,130,173)` | endplate inner faces |
| 13 / 14 | `(526,8,463,115)` / `(526,125,464,110)` | rear wing elements; x runs along the SPAN (x 526 = right tip). **The sim draws BFGoodrich on the top on any paint** |
| 49 / 50 | `(157,334,135,71)` / `(16,250,135,70)` | front-wing endplates, right / left |
| 1 | `(971,411,840,242)` | not seen from outside in any sweep (floor / underside) |
| 7, 4, 10, 11, 12 | — | not seen on any surface you look at; leave black |

Leaky islands (green outline open — `tools/island_runs.py` returns −1 there):
the nose sides ahead of x 511 on both sides, the left lower front flank, the
right sidepod face. The whole-half mirror paints them.

## Number blocks — all three stamp

| block | rect | where | stamp |
|---|---|---|---|
| N1 | `(436,299,123,87)` | LEFT rear-wing endplate outer face (island 24) | reads from the left side; stamps **white** by default |
| N2 | `(864,299,123,87)` | RIGHT endplate outer face (island 25) | reads from the right; stamps white by default |
| N3 | `(333,1278,98,135)` | nose top, centred on row 1345.5 | reads from the **front**; stamps dark |

Probed 2026-10-08 with the blocks magenta (`tools/probe_bands.py ... blocks`):
the stamp lands inside every block. `tools/checkblocks.py` is MX-5-only — the
build's own guard checks these three.

## What the sim draws on any paint

- **BFGoodrich** on the rear-wing top (a dark grey decal over a black wing).
- Nothing else: the template's `Car_Decal` layer (Skip Barber Racing, RACER,
  the "Q" logos, the white nose oval) is the default livery, not forced — a
  flood probe shows none of it. **No cutoff triangle or extinguisher mark**,
  so the build adds them.

## Where everything is placed (v1.0, locked 2026-10-08)

All named constants at the top of `src/team_sbf2000.py`. Side placements are
LEFT texture space (y > 1347); `place()` does the right side
(ROTATE_180 at `2695 − y − h + 1`).

- **Centre stripes** white | papaya | white (36 / 18 / 6) on row 1345.5,
  masked to islands 47/3/96/6/17/18 (`assets/sbf2000-centre-mask.png`):
  - nose tip → nose number panel, **tapering linearly** from x 22 (0.35×) to
    full width at x 200;
  - behind the panel (12-texel body gap each side) under the chrome latch to
    the **AÏ roundel node** on the scuttle — badge 92, gap 5, white ring 10,
    gap 5, centred x 822, letters reading from the **front** (ROTATE_270) —
    and a short stub to the cockpit rim (x 916);
  - engine-cover spine x 1480..1831, the band set **scaled per column to stay
    inside the tapering spine** (5-texel margin, never below 0.4×), then the
    tail x 1834..1918 at the spine's end width, stopping before the vents —
    one tapering stripe from the hoop to the vents.
- **Sidepod sash** (40 / 20 / 6) across each pod's leading edge, wrapping from
  the pod top (island 8) down the pod face (island 5): centre x 1222 at the
  face's top row, lean 0.28 (top-forward / bottom-rearward), each island
  drawn from its own seam row so the lean is continuous over the unmapped
  seam. Island IDs `assets/sbf2000-pod-islands.png`. Drawn on the left and
  mirrored.
- **AÏNTOLOGIC** 380 px on each tub flank above the pod, centred (1352, 1578).
- **Driver strip** (your `--driver` name; blank by default) 118 px at
  (818, 1560), ahead of the mirror stalk; **cutoff triangle** 26 at
  (996, 1559) and **extinguisher E** 26 at (1034, 1559), behind it.
- **Logo slot 2** (`--logo2`; a neutral **YOUR LOGO** placeholder by default)
  250 px on each pod face, under the groove line, centred (1470, 1972).
- **Logo slot 1** (`--logo1`; **YOUR LOGO** placeholder by default) 100 px on
  each **pod top**, aft of the sash, centred (1528, 1744) — reads from above
  and every 3/4. Chosen because the endplates are full of number, the wing top
  carries the forced BFGoodrich decal, and the tail is a narrow vented cover.
- **Number panels** white on N1, N2, N3, margin 8.
- **Left black on purpose:** front wing and its endplates, rear wing,
  endplate inner faces, engine-cover side panels, nose sides, lower front
  flank, the spine beyond the stripe.
- **Spec:** B3 Satin-True, carried over, not A/B-validated (accepted at the lock).

## Tried and rejected (on the render, 2026-10-08)

1. **AÏNTOLOGIC on the sidepod face.** At the 4.47:1 wordmark aspect, a
   full-size mark is ~100 rows tall; below the groove the face is 70–120 rows
   and shrinking rearward. It moved to the tub flank (the Ray layout) and
   logo slot 2 took the face.
2. **AÏNTOLOGIC 440 px at (1388, 1601)** on the flank: its lower third hid
   behind the pod top's rounded inboard edge (visible flank ends ~1625), and
   on the right its first letters sat against the rear tyre. 380 px at
   (1352, 1578) is fully clear both sides.
3. **Spine stripe full width on the tail.** The spine taper then jumped back to
   full width at the spine / tail joint and read as broken blocks from dead
   rear. The tail now carries the spine's end width.
4. **Nose taper only to x 104** (just clearing the tip): a visible kink where
   the taper stopped. Linear taper to x 200 is smooth.
5. **Roundel node 100 px at x 790**: the chrome latch (over island 96,
   x 671..749) sat on the white ring. 92 px at x 822 clears it.
6. **Driver strip at x 928**: the mirror stalk lands on the flank at
   x ~965..980 on both sides and crossed the driver strip. Strip moved ahead
   of it, cutoff + E behind it.

## Traps on this car (also in `docs/PANEL-PROBING.md` section 15)

1. **Two mirror rows.** Side pairs mirror at 2695; the centre islands are
   self-symmetric at 2691. Measure both kinds; do not take the centre row from
   the side mirror.
2. **Endplates exist but are full.** Do not assume "no endplates" from the
   car class — and do not assume an endplate is free for a logo.
3. **The sim forces BFGoodrich on the rear-wing top.** Probe a black wing
   before planning a wing wordmark.
4. **Endplate stamps default to white**, the nose stamp to dark — the chip
   colour is per stamp, so a white panel can swallow a number until you set
   the chips.
5. **A tapering spine defeats a constant-width stripe.** Scale the band set
   per column from the island's own edges (`SPINE_HW`, read with
   `tools/island_runs.py`), and carry the end width onward.
6. **The visible flank is shorter than the island.** The pod top's rounded
   inboard edge hides the flank's lowest ~40 rows from a level side — read the
   Y ruler from the level view, not the bbox.
7. **Hardware on the paint:** the nose latch (island 96) and the mirror stalk
   foot (flank x ~970) are 3D parts over the texture. Place marks around them.
8. **Viewer quirks:** switching Car Info → Car Model once collapsed the 3D
   pane to zero height; closing the dialog and reopening the car from the shop
   list fixed it. Keep the viewer window maximised and unobstructed so captures
   are clean. A reload sometimes resets the camera to a front 3/4, sometimes
   not — sweep and pick.

## How to edit this car later

1. `python src/team_sbf2000.py` writes colour + spec and refuses to write if
   artwork lands in a number block.
2. Every placement is a named constant at the top of the file.
3. Re-probe: `python tools/template_layers.py <zip> <scratch>\sbf2000\tpl`,
   then `python tools/probe_islands.py team_sbf2000 <scratch>\sbf2000\tpl list`;
   for any "which texel is this", `python tools/coord_grid.py team_sbf2000 128`.
4. Masks: `python tools/body_mask.py <tpl> assets/sbf2000-centre-mask.png 47 3 96 6 17 18`,
   `python tools/island_id_mask.py <tpl> assets/sbf2000-pod-islands.png 8=8 5=5`.
5. Mirror: `python tools/mirror_row.py <tpl> 2670 2715 9/8 29/27 31/30 3/3 17/17`
   (sides 2695, centre 2691); `python tools/mirror_row.py <tpl> 385 415 15/16` (398).
