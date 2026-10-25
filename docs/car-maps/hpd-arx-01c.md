# HPD ARX-01c (#39) — panel map

**Re-mapped from scratch 2026-09-17 (session 3).** The two earlier HPD sessions
are abandoned; every number below was measured again on this car, from the
template and from the render. Nothing here is inherited from the MX-5, F4, RSR,
Ray, Ferrari or Lotus.

Status: **Approved 2026-09-17.** The ready-made paint is in `paints/hpd-arx-01c/`.
Any pixel change is a v1.1, never an edit of v1.0. Spec map is the unmodified
B3 "Satin-True" hierarchy, carried over without a per-car A/B. On-track
verification still pending.

## Identity

| | |
|---|---|
| car id | **#39** (paint folder and template both confirm it) |
| template | your own iRacing template — `39_template_ARX.zip` → **`Honda Performance Development ARX01C.psd`**, 2048×2048 |
| paint folder | `%USERPROFILE%\Documents\iRacing\paint\hpdarx01c\` (created by the sim) |
| file | `car_<id>.tga` and `car_spec_<id>.tga` (the finish), written for the iRacing customer ID you pass with `--id` |
| build | `src/team_hpd.py` |

The car viewer titles the dialog **“Car Info: HPD ARX-01c”**, which is what
confirms the template belongs to this car.

## The rule of this UV

The **body** is mirror-symmetric about texture row **1197**:

    right y = 2394 − left y,  x identical

Measured by mask correlation on three island pairs (7/6, 15/14, 23/24), all at
**99.8–99.9 % overlap**, plus islands 0, 1 and 8 which are self-symmetric about
the same row. `tools/mirror_row.py <tpl> 2380 2410 7/6 15/14 23/24` (where
`<tpl>` is the scratch folder you extracted the template into).

- **rows > 1197 = the car's LEFT side**, rendered **UPRIGHT** from a level left view
- **rows < 1197 = the car's RIGHT side**, rendered **ROTATE_180**
- **on BOTH sides texture +x is REARWARD**, and texture +y runs from the centre
  line outwards and then down the flank

Proved with a whole-texture coordinate grid (`tools/coord_grid.py`, 128-texel
cells labelled `col,row`): the left flank reads `9,12 → 10,12 → 11,12` nose to
tail **upright**; the right flank reads the same sequence **upside down** at
rows 6-ish. Independently confirmed by island 0's texture-top edge marker
landing on the car's RIGHT front fender in a dead-front frame.

So side geometry is drawn once in LEFT texture space and mirrored; text is
composited afterwards with `place()` (playbook Rule 4). **Only islands 0, 1,
6 and 7 obey the mirror** — everything else is packed independently.

## Islands that matter

`tools/probe_islands.py team_hpd <tpl> list`. The template's **Wire layer is
all white** — no green island outlines at all — so the island finder falls back
to the Mask layer (that fallback is already in `tools/probe_islands.py`).

| idx | bbox (x,y,w,h) | what it is |
|---|---|---|
| **0** | `(9,576,992,1243)` | **FRONT BODY** — nose top and sides, both front fenders, scuttle. Self-symmetric about 1197. x runs from the nose tip rearward; y is lateral |
| **1** | `(941,717,1093,962)` | **REAR / SIDE BODY** — both sidepod flanks, engine-cover top, rear deck, rear fenders. Self-symmetric. Same axis convention |
| 2 | `(725,17,760,493)` | front splitter / front diffuser |
| 3 | `(9,9,782,261)` | **rear wing main plane + the RIGHT endplate** (see below) |
| 4 | `(1321,1596,650,440)` | LEFT engine-cover flank + left rear quarter |
| 5 | `(1426,299,601,548)` | RIGHT engine-cover flank + right rear quarter. **Not a mirror of 4** (62 % overlap) |
| 6 / 7 | `(154,367,607,339)` / `(154,1689,607,339)` | the panel ahead of each sidepod that carries the flank number, plus the front fender's outer face. True mirrors (99.9 %) |
| 8 | `(1129,1122,643,151)` | rear centre panel between the fins. Self-symmetric |
| **11** | `(1818,1848,222,160)` | **LEFT endplate** — `x 1818..1929` inner face, `x 1929..2040` OUTER face |
| 12 / 13 | `(1048,503,253,198)` / `(780,503,253,198)` | the two cockpit fins. Packed side by side, not mirrored |

Number blocks (PSD “Number Blocks”): **N1 `(442,408,100,52)`**,
**N2 `(232,610,52,100)`**, **N3 `(442,1934,100,52)`**. N1/N3 are the mirrored
flank pair and live on islands 6/7; N2 is a portrait block near the front.
`tools/checkblocks.py` is **hardwired to the MX-5's blocks and reports a false
FAIL on this car** — use `python src/team_hpd.py`'s own guard, which uses the
rects above and reports `0 bad px` on all three.

`assets/hpd-body-mask.png` is the union of islands 0, 1, 6 and 7, dilated 3
texels. **It is not shipped — regenerate it from your own iRacing template
with:**

    python tools/body_mask.py <tpl> assets/hpd-body-mask.png 0 1 6 7

`mirror_geometry()` in the build masks the
mirrored layer with it so a stripe drawn in left space cannot land on the
engine-cover flanks, the endplates or the splitter, which are **not** mirrors.

## The rear wing — measured, and mostly unusable

Island 3's main plane is `x 14..525` (span) unwrapped into three chordwise
bands, settled with a `3:C:1,8` / `3:R:1,3` chord probe read from a **dead
rear** and a **top-down** frame:

| rows | surface |
|---|---|
| `y 9..96` | leading edge / underside |
| `y 96..183` | **TOP surface** — carries AÏNTOLOGIC |
| `y 183..270` | trailing / rear face |

**TRIED AND REJECTED:** a white \| papaya \| white band on the rear face.
Unlike the Lotus 79, the HPD's wing has essentially **no rear-facing area** —
dead astern it is a ~2 px dark edge, and the band only showed as two specks
where the profile thickens at the endplate mounts. The dead-rear read comes
from the engine-cover centre stripes instead.

The wordmark on the top surface reads from above and from every high rear 3/4,
and its letter tops point rearward so it also reads the right way up from
behind. No rotation is applied in code.

### The endplates are asymmetric — per-side coordinates

| | island | OUTER face rect | inner face |
|---|---|---|---|
| LEFT | 11 | `(1929,1848,111,160)` | `x 1818..1929` |
| RIGHT | 3 | `(530,9,130,174)` | `x 660..790` |

Different islands, different sizes, different aspect. **Both outer faces take
UPRIGHT artwork.** The first pass centred the logo on the *island* instead of on
the *outer face*, so half of each one landed on the inner face and the render
showed a cropped logo — this is the per-side placement rule earning its keep.

## Where everything is placed (first concept, v-draft 2026-09-17)

All of it is in `src/team_hpd.py` as named constants.

- **Centre stripes** white \| papaya \| white about row 1197: island 0 `x 46..700`
  (nose tip → scuttle) through the **AÏ roundel node** (d 168 at `x 330`), then
  island 1 `x 1180..2010` on the engine cover with a skip at `x 1330..1470` for
  the airbox mouth — a gap, not painted through (the Ferrari's rule).
- **Front-fender sash** on island 0, LEFT space, `xc 430`, tilt 0.30,
  `y 1520..1815`, bands 54/27/8. Reads as a strong chevron from above and from
  every front 3/4; from a level side it is a thin crown line, which is correct
  for a fender crown on this body.
- **AÏNTOLOGIC** 455 px on each sidepod flank, centred `(1310, 1520)` in LEFT
  space. v1 used 520 px at `(1430, 1567)` and **ran off the back of the panel
  into the rear arch on both sides** — the mirror was fine, the box was simply
  too long and too low.
- **Driver strip** (your `--driver` name, blank by default) 150 px at
  `(1040, 1440)`, ahead of the wordmark.
- **Logo slot 2** (`--logo2`) 330 px on each **engine-cover top shoulder**,
  centred `(1470, 1352)` in LEFT space on island 1, so it mirrors cleanly.
- **Logo slot 1** (`--logo1`) on both endplate outer faces: 96 px at
  `(1984,1928)` left, 112 px at `(595,96)` right.
- **AÏNTOLOGIC** 430 px on the wing top, centred `(270,139)`.
- **Number panels** on all three blocks, margin 10.

## Traps on this car

1. **The Wire layer is blank.** Islands come from the Mask layer; the mask's
   polarity is inverted (opaque over the *background*), which
   `tools/probe_islands.py` already handles.
2. **A top-down frame lies about text on a vertical surface.** Logo slot 2 on the
   engine-cover flank looked upside down from above and correct from a level
   side; acting on the top-down reading flipped it the wrong way. Judge text
   from a **level** camera (playbook Rule 3a), every time.
3. **Islands 4 and 5 are not mirrors** and take opposite rotations. Worse, from
   a level side a mark there is swallowed by the rear wheel and the pod
   shoulder — it only ever read from a rear 3/4. **Tried and rejected** as the
   logo slot 2 location.
4. **Islands 6/7 are mostly hidden.** Their bbox is 607×339 but only a narrow
   strip around the number block is visible from outside; a sash drawn there
   (`xc 615`, `y 1700..2020`) never appeared. **Tried and rejected.**
5. **The rear of this car is almost all mechanicals** — diffuser, crash
   structure, exhaust. There is no tail panel to put a wordmark on. The rear
   signature is the engine-cover centre stripe plus the logo slot 1 mark on both
   endplates.
6. `tools/checkblocks.py` is MX-5-specific — see above.

## How to edit this car later

1. `python src/team_hpd.py` writes the colour TGA and the spec TGA and refuses
   to write if artwork lands in a number block.
2. Every placement is a named constant at the top of `src/team_hpd.py`. Side
   placements are in LEFT texture space (y > 1197); `place()` handles the right
   side.
3. To re-probe: `python tools/template_layers.py <zip> <tpl>` (extract the
   template into a scratch folder `<tpl>`), then
   `python tools/probe_islands.py team_hpd <tpl> list`, then masked
   grids (`IDX:NAME:cols,rows`). For absolute coordinates anywhere on the car,
   **`python tools/coord_grid.py team_hpd 128`** paints the whole texture as a
   labelled `col,row` grid — that one probe answered more questions than any
   other on this car, and it is the first thing to run on the next one.
4. Read everything from a **level** camera, and judge text orientation from a
   full-resolution crop, never a contact-sheet tile.
