# Panel map — Global Mazda MX-5 Cup

- iRacing car ID: **67**  (shown as `#67` in the Car Info panel)
- Template: the car's `67_template_MX16.zip` from your own iRacing template download -> `Mazda MX5 2016.psd`, 2048x2048
- Paint folder: `%USERPROFILE%\Documents\iRacing\paint\mx5 mx52016\`
- Paint file: `car_<id>.tga`, where `<id>` is your iRacing customer ID — pass it to the builder with `--id`.
- Side mirror axis: `left_y = 2492 - (right_y + height)`

This map documents the MX-5 build of the generator's example AÏNTOLOGIC team
scheme (papaya / black / white). Personalize it with your own customer ID
(`--id`), driver name (`--driver`) and two logo images (`--logo1` / `--logo2`);
with no flags the output carries a neutral "YOUR LOGO" placeholder and a blank
driver strip.

**About the script names in this map.** This is the working log from the
first car painted. Many of the one-off probe scripts and early builder files
it names (for example `probeN.py`, `calib.py`,
`build_aintologic_mx5.py`, `stripepath.py`) were written for this car alone
and are
not in this repo. The general tools described in `docs/PANEL-PROBING.md` do
the same jobs on any car.

Every row was verified by eye in iRacing's car viewer. Nothing here is inferred
from the wireframe alone.

## Template anchor blocks

| block | x | y | w | h | lands on |
|---|---|---|---|---|---|
| SA | 195 | 980 | 316 | 531 | hood |
| SB | 1323 | 310 | 447 | 155 | rear deck / trunk lid |
| SC | 719 | 593 | 373 | 179 | LEFT door |
| SD | 719 | 1720 | 373 | 179 | RIGHT door |
| N1 | 493 | 577 | 123 | 105 | LEFT front fender — number |
| N2 | 493 | 1810 | 123 | 105 | RIGHT front fender — number |
| N3 | 777 | 214 | 89 | 74 | front bumper — number |

## Panels

| panel | x | y | w | h | render transform |
|---|---|---|---|---|---|
| RIGHT flank | 386 | 1679 | 884 | 306 | upright — draw normally |
| LEFT flank | 386 | 507 | 884 | 306 | **draw ROTATE_180** |
| hood | 12 | 880 | 706 | 732 | rotated 90° CW — **draw ROTATE_90** |
| rear deck | 1132 | 130 | 747 | 456 | **ROTATE_180** — see correction below |
| front bumper | 683 | 887 | 614 | 751 | orientation NOT yet verified |
| rear bumper / valance | 16 | 11 | 1179 | 441 | orientation NOT yet verified |
| rocker / sill | 1341 | 1741 | 690 | 299 | orientation NOT yet verified |

## Rear quarter

The rear quarter does not sit in one clean rectangle. Two sub-rects were verified
to land **only** on the rear quarter and nowhere else:

- `(1297, 600, 355, 200)`
- `(1652, 800, 355, 200)`

Beware: `(1297, 800, 355, 200)` and everything below y=1000 in that column
straddles the **nose**. Filling the whole `(1297, 600, 710, 600)` block green put
a green square around the Mazda badge.

## Flank orientation — VERIFIED 2026-08-14, supersedes the old note

Read off the car with `calibrate.py rects`, patches `LA/LB/LC` in the LEFT flank
and `RA/RB/RC` in the RIGHT flank, all at raw texture x = 392 / 690 / 988.

**On BOTH flanks, smaller raw-texture x = toward the FRONT of the car.**

- RIGHT flank: content renders **upright**. `RA` (x=392) sat at the nose.
- LEFT flank: content renders **ROTATE_180** — red bar on the patch's bottom
  edge, blue bar on its right edge, the playbook's 180° signature — and yet
  `LA` (x=392) also sat at the nose. Raw y is inverted: raw y=690..805 (low in
  the texture rect) renders HIGH on the car.

### The trap this creates

`fl_left = fl.transpose(ROTATE_180)` does **not** give you the same livery on
both sides. Rotating the shared flank image moves the design's front content to
the car's rear. Confirmed on the car: the lower green sweep rises toward the
tail on the right side and toward the nose on the left, and the AÏ mark — drawn
once at high flank-local x — lands on the rear quarter on the right and on the
**left front fender, on top of N1 and the stamped number**, on the left.

**The flank cannot be one shared image.** Compose it per side: mirror the layout
in x for the left flank, draw glyphs upright, and composite marks after the
rotation. A single shared image also makes N1 and N2 map to opposite ends of the
artwork, so no single wedge shape can dodge both number blocks.

## Number blocks are reserved

N1, N2 and N3 must be **completely empty** in `car_<id>.tga`. When a spec map is
added they must be plain non-metallic gloss — a stamped number inherits whatever
material sits under it at that UV location.

Current build FAILS this. Measured on the built TGA, not eyeballed:

    N1 DIRTY  11376/12915 px   forest [13,49,48]
    N2 DIRTY   5066/12915 px   forest [13,49,48]
    N3 clean       0/6586 px

`tools/checkblocks.py` is the checker. Run it before
every deploy.

## The stamped number

iRacing stamps the number over the paint; the base paint stays number-free
(numbers can be reassigned in official races, so a painted-on number would
double up or contradict scoring). Colour is set in **Paint Shop → Paint Your Car
→ Car Number**, three chips.

**Verified on this car: chip 1 drives the HOOD number, chip 2 drives the FLANK
number.** Setting chip 1 to bone fixed the hood and left the flank dark. Both
chips need bone `#EFE4D0` to get bone-on-dark everywhere. Chip 3 = `#0B0C0E`.

`car_num_<id>.tga` is a later option, not the fix — it only displays with "Hide
Car Numbers" on, and Trading Paints requires **Pro** for custom numbers.

## Viewer loop

- `python tools/view2.py` — focuses iRacing, sends Ctrl+R twice, captures the
  window to `out/viewer/shot.png` (or `--out <file>`). `--drag 520` rotates ~180° to see
  the other side.
- `python tools/zoom.py <in> <out> --box l t r b` — zoom crop; the box is
  fractions of the frame (default: the middle of the 3D view).
- A file bridge that returns PNG/JPG directly needs no base64 step.

## Rear quarter and rear valance — PARTIAL, 2026-08-14

Calibration run: `BA..BF` tiling `(16,11,1179,441)`, `Q1..Q4` splitting the two
quarter rects, `R1/R2` splitting the rocker.

Confirmed:

- `(16, 11, 1179, 441)` **is** the rear bumper / valance, and it also wraps up
  over the **rear deck trailing lip**. Colour from this rect appeared along the
  tail edge and as a sliver on the deck near the roll hoop.
- The two quarter rects do land on the **rear quarter above the rear wheel** —
  Q patches showed cleanly there as solid blocks.
- Blue (texture-LEFT) edge bars on the Q patches appeared on the patches'
  **right** side, which points at a mirrored or 180° mapping. NOT yet confirmed.

Not yet resolved, do not guess:

- Exact orientation of the quarter and valance rects.
- **The valance UV is badly stretched.** The B patches rendered as thin diagonal
  bands across the fascia, not as rectangles. Any shape drawn there will need to
  be pre-distorted or kept to simple horizontal bands. This is the "iRacing
  shuffles and flattens panels" problem the painting tutorial warns about.

Blocker on finishing this: the car viewer needs a level, straight-on rear view
to read the orientation bars, and the old viewer script's sideways drag
orbits with a downward pitch, so it lands on a top-down three-quarter instead.
Either fix the drag or set the view by hand before the next pass.

### Why this matters

The sill wedge currently dies at the rear edge of the flank panel. It cannot be
carried into the quarter or across the tail until the two items above are
measured. Until then the livery reads as a stripe that stops, not a livery.

## Spec map — parked, 2026-08-14

`car_spec_<id>.tga` builds from the same code path (`build(spec=True)`), but it
is NOT deployed. Two attempts both looked worse on the car than no spec map:

- `SPEC_BASE R=200` (following the tutorial's "80% on red"): washed the whole
  body to a flat olive-brown. **Metallic is poison on a near-black car.**
- `SPEC_BASE R=10, G=18`: still laid a visible dull film over everything.

Deployed spec files were moved to a scratch folder (`spec_parked_*`), including
the `.mip` iRacing generates from the TGA on load.

Lesson: do not tune a spec map by eye in the car viewer while also changing the
livery. The tutorial's author states plainly that the viewer does not represent
in-game appearance. Test spec alone, on a plain body, in a replay on track.

### CORRECTION — rear valance is upright and clean, 2026-08-14

The "badly stretched, thin diagonal bands" note above was **wrong**. It came from
reading a near-top-down view where everything foreshortens. Re-read from a level
rear three-quarter (`python tools/view2.py --no-reload --drag-y -170`), the
same patches are clean, large rectangles and the `BF` label renders perfectly
upright and undistorted.

Verified from the rear:

| patch | rect | lands on |
|---|---|---|
| BA / BB / BC | y 30..220 | rear deck trailing lip / boot lid |
| BD / BE / BF | y 230..420 | **rear valance / bumper face**, upright |

- `BE (420,230,370,190)` shows **red bar on top, blue bar on left** — the
  playbook's no-transform signature. **The valance renders UPRIGHT.**
- Texture x increases left-to-right as seen standing behind the car:
  BD = car's right corner, BE = centre / plate area, BF = car's left corner,
  wrapping around onto the quarter.
- The stamped number lands on the valance face, upper-centre, and renders bone
  and clearly readable there. Keep the upper band of the valance clear.

Lesson: never read a panel map from a top-down or steeply angled view.
Foreshortening turns clean rectangles into what look like skewed bands. Get the
camera level with the panel first.

## Valance block, 4x4 grid map — VERIFIED 2026-08-14

Probe: 4x4 labelled grid over `(16,11,1179,441)` overlaid on the live livery,
read from a level rear three-quarter.

Local coords inside the rect (1179 x 441):

| | col 1 (0..294) | col 2/3 (294..884) | col 4 (884..1179) |
|---|---|---|---|
| row A (0..110) | rear deck trailing lip — **KEEP CLEAR** | deck lip | deck lip |
| row B (110..220) | upper RIGHT quarter | upper bumper | upper LEFT quarter |
| row C (220..330) | RIGHT quarter | bumper face — **stamped number lands here** | LEFT quarter |
| row D (330..441) | lower RIGHT quarter | lower bumper / valance | lower LEFT quarter |

So the outer columns are the rear **quarters**, not the bumper. That is what
lets the sill wedge carry up over the quarter and around the tail. The two
`QUARTER` rects in the old map are near-useless by comparison — probed with
bright quadrants, they showed only tiny slivers on unrelated geometry. Left
disabled.

**N3 (777,214,89,74) falls INSIDE this rect**, at local `(761..850, 203..277)`.
iRacing packs the front bumper's number block into the same region. Any band
across the middle must stay below local y=277 there. The build guard catches
this — it fired on exactly that during this session.

## Hood mark orientation — settled

`ROTATE_180` before the panel's `ROTATE_90` compensation is **correct**; the
mark then reads upright from the front of the car. The earlier "hood mark is
wrong" symptom was purely **size**: at 470px wide on a 706px panel it ran off
the front edge and read as a cropped slab. 300px wide, centred, reads properly.

Tried and rejected: `ROTATE_90` renders it on its side, `ROTATE_270` renders it
mirrored. Do not re-litigate.

## Current livery layout

- **Hood** — AI mark, 300px, centred, reads from the front.
- **Door** — AÏNTOLOGIC wordmark. Door is otherwise kept clear.
- **Sill** — forest wedge with gold pinstripe, running the full length from the
  nose and rising toward the tail. Clears N1/N2 by geometry, not by masking.
- **Rear quarter + tail** — valance band rising at both outer columns to meet
  the sill wedge, flat across the middle so the stamped number stays readable.
- **Rear deck** — AÏNTOLOGIC wordmark, 320px, centred, with a gold rule under it.

## Front bumper / nose — VERIFIED 2026-08-14

**Two rects in the old map above are WRONG. Do not trust them:**

- `(683, 887, 614, 751)` labelled "front bumper" lands on the **rear shoulder**,
  as a small patch behind the door. It is not the nose.
- `(1341, 1741, 690, 299)` labelled "rocker / sill" renders **nothing at all**
  that is visible from outside the car. The visible sill is the bottom of the
  flank panel, which the wedge already covers.

Found the real nose by elimination: `calibrate.py grid --n 8` first, then a fine
probe over the region that showed up on the fascia.

    NOSE = (768, 1024, 1280, 384)      # renders UPRIGHT

local y = 0 is the top of the bumper, just under the headlights. A horizontal
band from local y=88 down reads as a splitter accent and ties to the sills.

**The extent matters and it is easy to get wrong twice.** The first probe started
at x=1024 and was 768 wide. That left BOTH bumper corners short, and fixing only
the high-x end fixed only the car's left corner while the right stayed bare -
visibly lopsided head-on. The fascia runs from **x=768 to x=2048**. Anything
narrower clips a corner before the wheel arch.

The far end of that span also catches the **mirror caps**, which come out
body-green. Discovered, not designed, but it reads as a deliberate colour-matched
mirror and it stays. Nothing else on the car is affected - verified from front,
both flanks, both rear three-quarters and above.

## Rear deck — visible area is NOT the rect centre

3x3 grid probe over `DECK = (1132,130,747,456)`: only **columns 2-3 and rows Q-R**
land on the visible boot lid. Column 1 and row P are off-panel. The visible
centre is about local **(498, 300)**, not the rect centre (373, 228). Centring
artwork on the rect puts it half over the edge, which reads as skew.

## Panels with no deliberate content

Everything else on this car - roof area, windscreen surround, interior, mirrors -
either has no visible UV in the regions probed or is not worth painting on a
roadster. The eight surfaces that carry intent are: nose, hood, both flanks,
sills (part of the flank panel), both rear quarters (outer columns of the
valance rect), rear deck, rear bumper.

## The livery, as built

Base, approved and unchanged: warm near-black, forest wedge along the sill,
gold-and-bone twin coachline, AÏNTOLOGIC on the doors, AI mark on the hood.

**The concept.** AÏNTOLOGIC is an AI company that pokes fun at AI. The car
is quietly, deliberately wrong in the specific ways AI is wrong - but every
joke lives inside real race car furniture: scrutineering roundels, contingency
decals, tech plates, a rear-facing line. Correct racing typography, correct
decal proportions, correct placement. Nothing floats in space.

This is NOT the lore text that got killed. "PROJECT REGISTRY // ENTRY 001" was
earnest - decoration pretending to mean something. These are jokes.

Test applied to every element: would someone who works with AI actually smile?
If it only looks technical, it was cut.

| where | what | why it is funny |
|---|---|---|
| sill, forward | AÏNTOLOGIC again, small, one letter gone soft | the wordmark is correct on the doors. This one is almost right. The classic generated-text tell |
| sill, middle | tech plate: "TECH / 97% CONFIDENT" | certification format, uncertain content |
| sill, rear | roundel: a hand with six fingers, rust ring | the oldest tell in image generation, as the most mundane sticker on a race car |
| rear bumper | "I MAY MAKE MISTAKES" | the literal AI disclaimer, aimed at the driver behind. Race cars have a tradition of one rear-facing line. This is the one |

Rust `#C0552A` appears exactly twice and both are deliberate: the diaeresis dots
in the marks, and the ring of the roundel. One warm point on a cool car.

At 100mph the car reads as black, green wedge, gold-and-bone coachline, big AI,
AÏNTOLOGIC. Every joke above is invisible at that distance. They live at walking
pace, which is the whole point.

## Spec map — SOLVED 2026-08-15. Read this before touching `car_spec_*.tga`.

Three attempts failed before this. All three failed for the same reason, and it
was not the one assumed.

### The channels

| channel | controls | values |
|---|---|---|
| **R** | metallic | **binary.** 0 = not metal, 255 = metal. Nothing meaningful in between |
| **G** | roughness | 0 = mirror smooth, very reflective. 255 = very rough, dead flat |
| **B** | **clear coat, INVERTED** | 0-15 = clearcoat OFF (pre-2023 look). **16 = MAXIMUM shine.** 125 = medium. **255 = dullest** |

**Blue is the trap.** It reads like "clear coat amount" and it is the opposite.
Setting B=255 thinking it meant "full clear coat" is what turned the car a
washed-out olive-brown on attempts one and two. Metallic got the blame; metallic
was innocent. Attempt three at `R=10, G=18, B=255` still looked like a dirty film
over the whole car, because the blue was still wrong.

Established two ways, independently:

1. **Ladder test on the car** - `spec_ladder.py` paints six (R,G) steps along each
   flank, B=255 on one side and B=0 on the other. Then uniform-fill sweeps with
   `spec_flat.py R G B`. Result: B=0 deep and glossy, B=128 browner, B=255 worst.
   Metallic with B=0 barely hurt at all.
2. **iRacing's own docs**, found afterwards, which say exactly the same thing.

Both scripts are worth keeping. Ladder first, uniform sweeps to confirm.

### What this car uses

    SPEC_BASE   = (  0,  40, 16)   black paint: non-metal, smooth, max clearcoat
    SPEC_FOREST = (  0, 110, 16)   wedge: satin, so it separates from gloss black
    SPEC_GOLD   = (255,  15, 16)   the gold line IS gold. Real metal
    SPEC_COACH  = (  0,   0, 16)   bone line: non-metal, mirror smooth, reads wet
    SPEC_MARK   = (255,  12, 16)   wordmarks + AI marks: polished metal
    SPEC_DOT    = (255,  22, 16)   diaeresis dots: polished copper
    SPEC_DECAL  = (  0,  95, 16)   sticker faces: semi-matte vinyl
    SPEC_NUMBER = (  0,  40, 16)   number blocks: plain non-metallic gloss

The marks work as metal because their albedo is **bone**. Metals need a light
base colour - iRacing's docs warn that metallic darkens the albedo. Do not make
anything dark metallic; it just goes muddy.

Sticker faces are deliberately NOT mirror-smooth. At `G=0` the tech plate blew
out and its text became unreadable. Real decals are semi-matte. Only the marks
are chrome.

### Method, if a future car needs this again

Never guess global values. `spec_ladder.py` for a stepped read off the car, then
`spec_flat.py R G B` to sweep one axis at a time against a no-spec control. Both
are in `tools/`.


## Rear deck — CORRECTED 2026-08-17. The old note was wrong twice.

Measured with a 3x3 and then a 4x4 labelled grid overlaid on the live livery and
read from a level rear three-quarter, per Rule 3. Both earlier statements about
this panel were wrong, and both cost a cycle on another livery built from this map.

**1. It renders ROTATE_180, not "upright — draw normally".**

The probe patches came back with their labels inverted, the red TOP bars along
the bottom edge of each cell and the blue LEFT bars on the right. That is the
playbook's 180° signature, unambiguously.

Consequence worth knowing: **the AÏNTOLOGIC wordmark on the approved v1.1 car's
boot lid is upside down.** Nobody caught it because an all-caps letterspaced
wordmark inverted at that size reads as "a bit skew" rather than as "upside
down", and the map's own note about the wordmark looking skewed is exactly that
symptom being explained away as a placement problem.

**2. The visible boot lid is a DIAGONAL BAND, not "columns 2-3, rows Q-R".**

On a 4x4 grid over `(1132,130,747,456)` the cells that land on visible boot are:

    Q4   R3   R4   S3

i.e. a band running diagonally across the rect, not an axis-aligned block. Local
cell size is 186 x 114.

That diagonal is why a horizontal wordmark renders running fore-and-aft up the
left side of the boot instead of across it. Artwork has to be rotated onto the
band axis, which is about **50.7°** in texture space. Rotating by that angle also
absorbs the 180° — do not apply both.

Values that work, local to the DECK rect:

    DECK_MARK_CX, DECK_MARK_CY = 558, 285      # centre of the visible band
    DECK_MARK_ROT              = 50.7          # degrees CCW, absorbs the 180

## Hood — a PICTURE needs a different transform from TEXT

The hood renders 90° CW, and the map says draw `ROTATE_180` then `ROTATE_90`.
That is correct **for a text mark**: it leaves letters standing up with their
tops toward the windscreen, which is how you read type off a bonnet.

For a **profile picture** it is wrong. The same chain put a profile logo (a
crested bird mark) with its beak pointing away up the hood, so from the front all
you saw was a white blob with spikes around it. Use `ROTATE_270` before the
panel's `ROTATE_90`; the two cancel and the emblem lands exactly as drawn — crest
toward the windscreen, facing across the car.

    text mark     -> element.transpose(ROTATE_180), then panel ROTATE_90
    profile mark  -> element.transpose(ROTATE_270), then panel ROTATE_90

## Flank — how much of this rect is actually visible

Rule 3c again, and it bit hard on another livery built from this map. A large
part of the bottom of the flank rect is the rocker and the underside of the sill,
which you cannot see from outside the car. A wedge whose top edge sat at y≈288 at
the nose and y≈152 at the tail read on the car as a thin orange skirt along the
rocker and nothing else.

**Everything below about local y=250 is nearly invisible.** Graphics that are
meant to read from trackside need their top edge up around y=100–270.

Hard constraint that fights this: N2 occupies flank-local `(107, 131, 123, 105)`,
so across x 107..230 the artwork top must stay **below y=236**. That livery's
wedge threads it at y≈256..242 there, about 9px of margin. Run the build guard
after any change to the front of that edge.

## Spec map — do not make marks metallic on a near-black car

The AÏNTOLOGIC car's marks are `R=255` polished metal and that is right for bone
on forest: they read as chrome. The same value on a white profile logo made its
head mirror the environment and render as a **dark blue-grey blob** on the
bonnet — the mark simply disappeared.

Metallic darkens the albedo and turns a flat colour into a mirror. Only use it
when you actually want a mirror. That logo uses `SPEC_MARK = (0, 45, 16)` —
gloss vinyl, non-metal — and the white stays white.


## Rear deck — do not put a wordmark on it. 2026-08-17

Beyond the ROTATE_180 and the diagonal band noted above, a ray-fan probe (six
known-angle rays from the intended placement point, overlaid on the live livery)
showed the visible boot strip is both narrow and badly foreshortened, and that
the placement point sits at the edge of it rather than the middle. Every ray ran
off along the trailing edge.

Two attempts to seat a wordmark there produced (a) type running fore-and-aft up
the left side of the boot and (b) type jammed into the right corner at an angle.

**Put the brand on the rear VALANCE instead.** That rect is verified upright and
clean, it is what a following driver actually sees, and it has room. Keep it
clear of N3 at local `(761..850, 203..277)`; a 340px mark centred at local
`(560, 292)` clears it and sits above the number-plate recess, which otherwise
splits the word in half.

The boot lid takes scattered marks well — small roundels, tiled motifs — because
they are rotation-tolerant. Leaving the boot clear and carrying the brand
elsewhere is also a safe choice.


## AÏNTOLOGIC v2 concept build — measured 2026-08-23

Built from the approved concept pack onto this map, as
`src/build_aintologic_mx5.py`. What the pass measured:

### Hood canvas axes — VERIFIED with a 4x4 labelled grid

The hood is drawn into a canvas of `(HOOD[3], HOOD[2])` = 732 x 706 and then
`ROTATE_90`. Probed with a 4x4 grid (cells 183 x 176) overlaid on the live
livery, read from above and behind:

| canvas axis | on the car |
|---|---|
| x 0..732 (cols A..D) | **ACROSS** the car, A = one flank, D = the other |
| y 0..706 (rows 1..4) | **ALONG** the car, y=0 at the NOSE, y=706 at the windscreen |

Rows 1 and part of row 2 sit forward of the visible bonnet.

A four-rotation probe in the same run (`hood_probe.py`) settled the
transform for a WIDE mark, which the old square `AI` mark could not reveal:

    ROTATE_270 -> renders exactly as drawn (red TOP bar on top, blue LEFT bar
                  on the left), long axis running ALONG the car
    ROTATE_180 -> long axis runs ACROSS the car, reads from IN FRONT  <- text
    ROTATE_90 / ROTATE_0 -> upside down / along the car

So the map's "text mark -> ROTATE_180" is right, and it also means a **wide**
text mark lands across the bonnet, which is what a sponsor wordmark wants.

Working values: `HOOD_WM_W = 380` (52% of the 732 canvas width; the map's old
"470 ran off the bonnet" warning applies to the other axis) and a **-150 y
offset from canvas centre** to sit in the forward-middle sponsor field rather
than up against the cowl. At canvas centre it reads as a cowl mark.

### Rear valance — the (560,292) wordmark spot needs a caveat

The verified "340px mark centred at local (560,292)" clears N3, but it assumes
a mark whose art box is all cap height. The AÏNTOLOGIC wordmark carries the
diaeresis above the caps, so centring its **box** at y=292 drops the letters
onto the number-plate recess and the recess splits the word — exactly the
symptom the map warns about. **Centre at (560,268)** for a mark with the dots.

### Rear valance outer columns — PARTIAL

Wrapping the flank bands around the rear corners: `x 884..1179` (col 4, the
car's left corner) wraps cleanly at local y 300..395. `x 0..294` (col 1, the
car's right corner) put colour **inside the number-plate recess** instead of on
the quarter, so it is narrowed to `0..180` as a holding fix. The two corners
are NOT symmetric in this rect. Not yet probed properly — do that before
trusting it.

### Near-black logo art dies on a dark body

A logo image that is near-black or pale grey — as many are, drawn for a white or
black background — is invisible on a dark body. Such a logo is tinted flat to a
palette colour (`tint()` in the build) rather than replaced — still your art,
this car's palette. A multi-colour logo keeps its natural colours and reads fine.

### The stamped number is dark-on-dark on this livery

Chip colours are still set for the old near-black car, so the stamped number
renders navy on navy. Both the hood and flank chips need warm cream
`#F3E8D2` in **Paint Shop -> Paint Your Car -> Car Number**.

Note a contradiction to resolve: the playbook's Rule 6 says **chip 3** drives
the flank number; the section above in this file says **chip 2**. One of them
is wrong. Set all three to cream and it does not matter, but prove it with the
magenta-number-block trick before writing either down as fact again.

### Moving screenshots off the viewer machine

If the car viewer runs on a different machine from where you process images,
base64 the PNG to a `.txt` and transfer that; when a result is too large to load
directly, write the whole payload to a file first and return only its path, then
decode that file. The image crosses without ever entering a size-limited context.
Skip the first two header lines.


## PANEL COVERAGE — the number this map was missing. MEASURED 2026-08-23

Read this before placing anything from a design drawing.

Every earlier version of this file recorded panel **rects and transforms** and
nothing about **scale**: how much of the car a panel covers. Without that there
is no way to turn "the wordmark is 32% of car length" into a pixel width, so it
gets eyeballed, and eyeballing it cost three full rebuild passes on the
AÏNTOLOGIC v2 car before anyone measured.

Probe: `flank_ruler.py` paints labelled gridlines every 100 in x and 50
in y across the flank rect, over the live livery, read from a LEVEL side camera.

### Flank `(386,1679,884,306)` — covers the middle 51% of the car ONLY

| flank coord | on the car |
|---|---|
| x = 0 | **20.6%** of car length back from the nose |
| x = 884 | **71.5%** back |
| y = 0 | the belt line (top of the door) |
| y = 271 | the bottom of the sill |
| y = 306 | just below the sill, not visible |

So the panel runs from just behind the front wheel to just behind the door.
**Both wheels are outside it** (front at flank x ≈ -28, rear at ≈ 1012), which
is why nothing on this panel ever needs a tyre or rim masked out.

**Consequence that matters:** anything a side drawing places forward of 20.6%
or aft of 71.5% of car length CANNOT go on this panel. On the example concept
that is the claw slashes (80%) and logo slot 2 (91%). Putting
them at the back of the flank rect lands them on the door, which is exactly
where they were wrongly sitting for three passes.

### Turning a side elevation into flank coordinates

For a flat whose body runs `flat_x0..flat_x1`, with the belt at `flat_belt` and
the sill at `flat_sill`:

    f      = (flat_x - flat_x0) / (flat_x1 - flat_x0)      # fraction of length
    flank_x = (f - 0.206) / 0.509 * 884
    flank_y = (flat_y - flat_belt) * 271 / (flat_sill - flat_belt)

For the AÏNTOLOGIC flat (2012x782, body x 60..1960, belt y=300, sill y=620)
that reduces to:

    flank_x = (flat_x - 451) * 0.913
    flank_y = (flat_y - 300) * 0.847

### Better than placing elements: resample the flat

Because the flank is a linear map of the car's side and holds no wheels, an
orthographic side elevation can be **resampled straight into the panel** rather
than redrawn element by element. `src/build_aintologic_mx5.py` does this
(`flank_from_flat`). It reproduces the approved design exactly and removes every
opportunity to eyeball a size. Two things still have to be handled in code:

- the design's own number panel must be erased, because iRacing stamps at N2
  which is further forward than a designer will draw it; paint a real panel on
  the block instead;
- artwork past 71.5% of car length has to be carried by the rear quarter.

### Still to measure the same way

The nose, hood, rear deck and valance rects have transforms recorded but **no
coverage figures**. Run the same ruler probe on each before placing anything
from a drawing onto them. Do not repeat the mistake this section exists to
prevent.


## The rear quarters are NOT a symmetric pair — 2026-08-24

Found while fixing a side stripe that stopped dead at the rear wheel on one
side only. Method: `docs/PANEL-PROBING.md` section 3 (elimination).

| rect | what it actually is |
|---|---|
| valance high-x columns `x 944..1179` | ONE rear quarter, seen from the side |
| `(1280,1536,256,256)` | the OTHER rear quarter — shoulder down to the arch |
| `(1536,1536,256,256)` | that quarter's upper SHOULDER only |
| `(1280,1792,512,256)` | the wheel-arch LIP, not the quarter |
| `(1024,1536,256,256)` | nothing visible from outside |
| `(1652,800,355,200)` | **the FRONT FENDER** — the old map calls this a QUARTER rect. It is not. |

So there is no left/right quarter pair to mirror. One side is carried by the
valance rect, the other by a rect that was not in this map at all, which is why
nothing was painting it.

### Still open

The band on `(1280,1536,256,256)` sits about 160px (screen) **above** the door
stripe, and `y=1791` is the bottom of that rect, so it cannot be lowered
further. The piece of quarter at door-stripe height, behind the wheel, is in a
further rect not yet found. `(1024,1536,256,256)` was the obvious candidate and
renders nothing visible, so it is ruled out.

### Viewer note

iRacing pops **System Message** dialogs (race results ready) over the car
viewer. They can take focus and make a reload or a drag silently do nothing.
If a probe seems not to have applied, check for a dialog before doubting the
code — and see `docs/PANEL-PROBING.md` section 0.


## TEAM SCHEME build — MEASURED 2026-09-13. Supersedes the rear-quarter notes above.

Built as `src/team_mx5.py` on the scheme in `docs/PAINT-SCHEME.md`. Probed
with `tools/probe.py` (8x8 grid over the whole texture, then 4x4 over
`(1024,0,512,512)`, 6x6 over the valance, and 8-band height probes on
`(1280,1536,256,256)` and `(1536,768,256,256)`), read from level rear
three-quarters on **both** sides. Locked as `v3.0-2026-09-13`.

### The rear quarters — SOLVED. Both are in the VALANCE rect.

The "further rect not yet found" does not exist. Behind each rear wheel, at
band height and down to the sill, the quarter is carried by the valance rect
`(16,11,1179,441)`:

| side (as the viewer shows it) | quarter behind the wheel | shoulder ABOVE the arch |
|---|---|---|
| the side where `(386,1679)` flank renders upright | valance local **x 0..~250** | `(1280,1536,256,256)`, rows 1728..1791 lowest |
| the side where `(386,507)` flank renders ROTATE_180 | valance local **x ~1008..1179** | `(1536,768,256,256)`, rows 768..863 only, ROTATE_180 |

- **Valance local y 280 is the same screen height as the door band's top
  edge at the rear of the door.** One black fill from local y 280 to 441
  across local x 0..1179 reads as continuous door → arch → quarter → tail on
  both sides.
- **The quarters keep rendering below the rect.** Texture rows 452..512 in
  x 16..270 and x 1024..1195 are the lower quarter too (`VAL_BELOW`).
- The plate recess is at local x ~500..750 (`C2` in the 8x8 grid). The old
  "col 1 hits the plate recess, narrow it to 0..180" note was wrong.
- Both shoulders sit **above** the band line and stay body colour. Painting
  `(1280,1536)` rows 1733..1791 black was the "patch too high" on one side.
- The old 4x4 valance map's LEFT/RIGHT labels are swapped relative to what
  the viewer shows. Don't trust side names in this file; trust rect + view.

### The rocker lip

A thin strip under the door survives every flank fill: it is the texture rows
just past the rect's sill edge. **48 rows below `(386,1679,884,306)`** and
**48 rows above `(386,507,884,306)`** (that one renders ROTATE_180). Painted
band colour, the sill reads solid.

### Nose

Local `(500,300)` in `(768,1024,1280,384)` is the **mirror cap**. A tow arrow
there rendered "TOW" on the mirror. No tow arrow on the nose.

### Viewer

- `python tools/view2.py --drag 260` is ~90° of orbit; 130 is ~45°.
- Pitch clamps: `--drag-y -600` is always level, `+600` always top-down.
  If a capture comes out top-down, that is why — level it first.
- `tools/contact.py <out> --level --pre 130` gives side / front ¾ / front /
  far side / rear ¾ / rear from wherever the camera is.

### Stamped number

Renders dark on the white panel and on papaya. Set all three Car Number chips
to `#0C0C0D` so it is the scheme's black rather than whatever it is now.


## THE WHEEL ARCHES — MEASURED 2026-09-13 (for the stripe sweeps)

Probed with 4x4 labelled grids over candidate rects (`arches.py`,
`fender.py` — same method as `tools/probe.py rect`), read from level
side and rear-three-quarter cameras on both sides. Sides named by which flank
rect the viewer shows: **U** = the side where `(386,1679)` renders upright,
**R** = the side where `(386,507)` renders ROTATE_180.

| surface | side | rect / region | mapping |
|---|---|---|---|
| front fender above the arch | U | flank island continued FORWARD: raw x 30..386, y 1679..1985 | upright, same axes as the flank; x 386 = door front edge, x ~90 = headlight |
| front fender above the arch | R | raw x 30..386, y 507..813 | ROTATE_180 like its flank; raw y 736..813 = fender crown, arch top ≈ 77 flank px below the belt |
| rear shoulder above the arch | U | `(1280,1536,256,256)` | upright; belt ≈ raw y 1600, arch top = 1791; x 1280 = door edge, x 1536 = rear of the arch. ~1.7 raw px per flank px |
| rear shoulder above the arch | R | `(1297,600,355,200)` | ROTATE_180; belt = raw y 800, arch top ≈ 700; x 1297 = door edge, ~1563 = rear of arch, 1652 = tail light. ~0.9 raw px per flank px |
| quarter behind the wheel, below the arch top | U | valance low-x: raw x 16..276, y 196..452 | upright; x 16 nearest the wheel, x 276 the corner; y 196 ≈ arch-top height, y 295 = the tail stripe |
| quarter behind the wheel, below the arch top | R | valance high-x: raw x 1000..1195 | upright; x 1195 nearest the wheel, x 1000 the corner |
| upper shoulder, R (mostly hidden) | R | `(1536,768,256,256)` | ROTATE_180; only rows 768..863 show, at the very top of the haunch |
| beside the tail light | R | `(1652,800,355,200)` | the old map's "FRONT FENDER" — it is not; it sits beside the rear light |

`arches()` in `src/team_mx5.py` draws the stripe over these as parabolas
per island, with the white line on the up side, stripe thickness scaled per
island. The old `(1341,1741,690,299)` "rocker" rect still renders nothing.


## Hood — MEASURED 2026-09-13, supersedes every earlier hood note

6x6 grid over `(12,880,706,732)`, read from above. **Texture x runs ALONG
the car** (col A = nose, col F = cowl), texture y ACROSS it. The visible
bonnet is **columns B..E (texture x 129..597)**; column F and everything
past it is the cowl and the windscreen-header sun shade. The visible centre
is the hood canvas centre, (365, 351) on the 732x706 canvas - not offset
toward the cowl. A 460px badge at +125 spilled onto the sun shade; 400px at
centre fits with margin.

## Front fender / bumper seam — MEASURED 2026-09-13

Height rulers on the fender islands (flank y 50..140) and the nose rect
(local y 0..90) at the same time, read from a level front three-quarter:
the fender's visible skin ends at about **flank y 95** at the seam, which is
level with **nose local y 0** (the bottom of the headlight). The bumper
stripe at local y 40 is therefore BELOW the fender's lowest visible point,
and a continuous stripe has to rise on the bumper corner (the outer ~130
columns of the nose rect) to meet the fender. Nose local x ~1040..1280 is
the mirror caps, not bodywork; keep the stripe off it.

## Viewer captures — reliable way

`python tools/view2.py --drag 87` six times = one lap in ~45° steps from
wherever the camera is; `tools/sheet.py` tiles them. Level first
(`--drag-y -600`). `contact.py`'s "reset" drag drifts; use this when you need
to see one specific joint again.


## THE SIDE STRIPE IS ONE PATH — the island model, CALIBRATED 2026-09-13

Read `src/stripepath.py` and `draw_stripe()` in `src/team_mx5.py`. The
stripe is defined once per side in car-side space (X along the car in flank
px, X 0..884 = the flank rect; Y down from the belt in flank px) and rendered
through these maps. Every number here was read off a level side capture
with reference lines at known Y on the flank islands (`calib.py`)
and ticks at known texture x (`calibx.py`).

| island | texture rect | map (X, Y) -> (x, y) |
|---|---|---|
| flank, upright side | (0,1679,1270,354) | x = FLANK_X(X) (non-linear ahead of the door: X -310..0 <-> x 0..386), y = 1679 + Y |
| flank, rotated side | (0,459,1270,354) | x = FLANK_X(X), y = 813 - Y |
| rear shoulder, upright side | (1280,1536,256,256) | x = 597.4 + 0.789 X; y: Y -70 -> 1600, 33 -> 1728, 98 -> 1792 (arch top) |
| rear shoulder, rotated side | (1297,600,355,200) | x = 1286 + 0.952 (X-864); y = 700 + (95 - Y) 1.32 (700 = arch top) |
| quarter behind wheel, upright side | valance x 16..276, y 180..516 | x = 16 + 1.016 (X-1201); y: Y 62 -> 204, 128 -> 300, 245 -> 420 |
| quarter behind wheel, rotated side | valance x 1000..1195 | x = 1629 - 1.394 (X-864); y: Y 52 -> 204, 130 -> 300, 228 -> 396 |
| bumper corner, upright side | nose local x 910..1040 | x: X -369 -> 910, -252 -> 1040 (1040 is at the arch); y = 1024 + 0.89 (Y - 110) |
| bumper corner, rotated side | nose local x 0..130 | x: X -369 -> 130, -252 -> 0 (0 is at the arch); y = 1024 + 0.89 (Y - 135) |

Arches (the lip, in car-side space): front, both sides, centre (-136, 240),
rx 136, ry 162, top at Y 78. Rear: centre (1065, 240) rx 189 ry 141 on the
upright side, (1046, 240) rx 189 ry 145 on the rotated side, top at Y ~97.

Things this exposed:

- Texture x 0..130 on the flank islands is the fender TIP by the headlight
  and covers only ~40 car units. Anything placed by "flank x" ahead of the
  door is wildly compressed there.
- The bumper corner columns run from the ARCH (inner end) to the nose (outer
  end), under the fender. Their top row is the fender's bottom edge - at Y
  110 on one side and Y 135 on the other. Not symmetric.
- Behind the rear wheel there is no visible skin below the arch top until
  X ~1215; a stripe that dips earlier disappears into the wheel opening.
- The tail stripe on the valance (row 295 = Y ~130) is LOWER than the door
  stripe (Y 98..106). The old note that "valance 280 is the same height as
  the door band" was a rear-three-quarter misread.

## THE STRIPE SEAMS — RE-MEASURED 2026-09-13, v3.5. Supersedes the table above where they differ.

v3.4 passed every geometric check and still had visible gaps at both rear
arch crowns and the rotated-side front corner. The maps above were wrong in
ways no amount of reasoning about them would find; only band/column probes
rendered on the live car found them (`probeFK.py`, `probeCols.py`,
`probeTop.py`, `probeFx.py`, `probeN.py` — all "draw labelled cells on the
build, capture level sides, read"). The current numbers are in
`src/team_mx5.py`; the findings:

- **The upright rear shoulder island is 380 px wide, not 256.** Texture x
  1536..1656 is the wheel-arch CROWN and the skin down to the quarter seam.
  With the rect cut at 1536 the crown was simply never painted — that was
  the "gap": not a misalignment, missing skin. Rect is now (1280,1536,380,266).
- **The quarter-behind-the-wheel columns start at the crown/quarter seam**,
  not at the arch top: upright-side quarter x 0 <-> X ~1285 (was 1185). The
  quarter's rows are also ~2.1 per Y unit, not 1.4 — the earlier value came
  from one point (the tail band) and was wrong at the top. Both quarters:
  Y 133 -> row 303 (tail band), 2.1 rows per Y.
- **The rear arch crown is at the shoulder/quarter seam (X ~1250)**, not
  mid-shoulder. Rear arch ellipse now centre (1250, 240) rx 220 ry 162 on
  the upright side, (1160, 240) rx 200 ry 162 on the rotated side (its
  shoulder map has the seam at a different X — x = 1297 + 1.127 (X-875),
  y = 704 + (95-Y) 1.32).
- **Bumper corners: the face's top strip (nose rows 960..1000) is the skin
  right under the headlight**, where the fender stripe ends. The corner's
  Y offset is therefore not constant: upright side v0 = Y 110 at the fascia
  end -> 122 at the rear tip; rotated side 135 -> 173. The upright corner
  runs to local ~1130 (was 1096); the rotated one 40..220 (0..40 hidden).
  Clip rects start at row 940 so the border isn't cut.
- **Small 3D panel-gap lines break a pixel trace** even when the paint is
  continuous; the QA dilates the orange mask by 7 px so a 2-3 px modelled
  seam doesn't count as a gap, and anything wider still fails.

The check: the stripe's continuity was measured on the live car and passed on
v3.5 (100% / 99%).
Rule learned again, expensively: **a seam that "should" line up by the
numbers is unverified until a probe on the live car says so.**

## THE STRIPE AS A RIBBON — WIDTH CALIBRATED ON THE RENDER, 2026-09-13, v3.6

v3.5 was 100% pixel-connected and still wrong: the quarters behind the rear
wheel rendered the stripe ~2x wide, the rear shoulders 1.3x, the fender
ahead of the door 0.5..0.8x, the tail band 1.4x, and two seams stepped.
Connected is not the same as one ribbon.  The target: "a constant-width
flexible vinyl tape being bent around the fender".

What changed, and the rule that comes out of it:

- **Texel density differs per island AND along an island.**  16 texture
  rows are not the same physical width on the door, the quarter and the
  fender neck.  `stripepath.render()` now takes a per-island width factor
  (a number or an `[(X, factor)]` table) that scales the stroke and the
  border offset together.  The factors are MEASURED: trace the rendered
  stripe column by column and compare its width with the door width; factor = old factor / measured ratio; two or three passes converge.
  Tables in `team_mx5.py`: FENDER_WA/WB (the two flanks differ - one is
  ROTATE_180 and its fender-to-door neck compresses differently), F_W, J_W,
  K_W, L_W.  A factor of 2.2 at the fender neck (X -45..-25) is real.
- **The tail band is drawn at the stripe's own 4+16 px, not 5+22.**
- **The quarter maps run 1.45 rows per car unit**, anchored at the crown
  seam (row ~201 <-> Y 67) and the tail band centre (row 299 <-> Y 133).
  The 2.1 of v3.5 exaggerated the descent (a kink) and doubled the width.
- **The rear shoulder path was raised ~19 units mid-shoulder** (base
  (960,78),(1150,76)) so the ribbon sits on the flat above the arch-flange
  shading instead of half in it; the shoulder maps take the raise back out
  at the crown seam (`_F` dy, `_J` dy) so the crossing onto the quarter did
  not move.  `_F` dy also pulls its copy of the descent down past the crown
  (+38 at X 1347) to coincide with the quarter's copy - the two islands
  overlap across a DIAGONAL seam there and must draw the same line.
- **Corner tips**: upright side tip y0 132, rotated side 165 (re-read at
  the headlight junction).
- **Island X ranges overlap by a few units only** (flank ..892/900, J from
  878, F from 870): a wide overlap draws two copies with different maps
  and the union is thicker than either.
- The roundel moved up (y 14) so its ring clears the stripe's border.

The check now has two halves: connectivity (unchanged), plus width, border,
step and kink checks on the same two level frames. The level frames are found
by nudging the camera until the silhouette is longest. (The scripts that ran
these checks were written for the MX-5 only and are not part of this repo.)
QA_DUMP=1 prints the profile every 10 px.

Known limits: a level side view foreshortens the bumper corners and the
fender tip, so the outer 8% of the car is not width-checked; and the
factors are calibrated for THIS camera distance/FOV - the ribbon is
constant in the viewer's level side view, which is the pose you judge from.


## v4.0 — SEBRING SASH + COBRA CENTRE STRIPES, 2026-09-14. THE RIBBON IS GONE.

The front-to-rear ribbon (v3.4–v3.6) was scrapped
and replaced with a Cobra/Sebring language: a white | papaya | white
sash across each FRONT fender, and centred white | papaya | white stripes
nose → hood → boot lid → tail, with the hood roundel as a node (white ring,
stripes enter front / leave rear) and the sash feeding into the roundel
across the hood. `src/stripepath.py` and the ribbon QA tools are deleted.
Everything below was read off the live car with labelled probes
(`probe*.py` this session); the values live in `src/team_mx5.py`.

### The centre-line panels

| panel | texture | centre / rows | notes |
|---|---|---|---|
| hood | canvas 732x706, ROTATE_90 | canvas centre x 366; y 0 = nose, y 0..128 = the front lip (visible from the front) | stripes y 0..610 |
| nose | (768,1024,1280,384) | local x **585**; rows 0..250 only | rows 256..383 are the MIRROR CAPS; rows 940..1023 above the rect are the bumper's upper face, 1408..1500 below it the lower lip — both painted so the stripe is continuous |
| boot lid | (1132,130,747,456) | local x **415**, rows 104..456 | lid runs up to ~row 100 at the third brake light (the old "rows above 228 are not the lid" was wrong); centre re-measured against the tail lights + Mazda badge in a dead-rear frame (`rearref.py`) |
| tail | valance (16,11,1179,441) | local x **591**, skip rows 118..240 (wordmark) | the wordmark (560) and the plate recess are both off-centre; don't centre on them |

Widths: hood (60,30,7) canvas px, nose (62,31,7), **lid and tail (54,27,7)**
— a dead-front / dead-rear pair at the same zoom (`widthcmp.py`)
puts the nose orange at 7.0% of car width; at 64 the rear was 8.4%.

### The fender sash and the hood/fender shut line

- Fender top = the 64 rows past the flank belt edge (rows 1615..1678 above
  FLANK_R, 814..877 below FLANK_L). The sash runs Y -64..250.
- **The fender renders uniformly in texture px** (1.08 frame px per texel at
  the seam, same as the hood's 1.09 per canvas px). The `FLANK_X` table's
  squeeze between X -50..0 is NOT physical there — drawn through the table,
  the front white rendered 15 px against the rear's 22. The sash is laid out
  in texels from the door front (texel 386), `FS_X_SCALE = 1`.
- **The shut line is a real crease.** No pair of texture directions looks
  straight from every camera; the join was tuned on the render in the two
  poses the design is judged from (slightly elevated side; elevated front 3/4). The
  sash centre line eases from vertical at the seam to its 0.28 lean by the
  belt; the hood feeder leaves the seam at `FEED_TILT0` and bends (quadratic
  Bezier) to radial at the node.
- **The hood island is not mirror-symmetric.** Per-edge trims: left edge
  (canvas x 0) FEED_Y -5; right edge FEED_Y +10 and tilt -0.3.
- **The flank rects are not mirror-symmetric either.** `FS_XC_SIDE`: the
  rotated FLANK_L rect (the car's RIGHT) needs +15 texels. On that rect
  +texels is FORWARD on the car — the sign is easy to get wrong twice; the
  approved state is orange at texels 374..413 on row 877.
- The hood's constant-y lines lean ~+0.22 toward the seam in an elevated
  side view, i.e. the hood UV is skewed relative to the shut line.

### Which rect is which side — say it every time

`(386,1679)` upright flank = car's **LEFT** (driver). `(386,507)` ROTATE_180
flank = car's **RIGHT**. Hood canvas x = 0 edge = LEFT. From a LEFT side view
the nose points LEFT.

### The rear quarters, for decals (probeRQ.py, 5x4 / 4x2 labelled grids)

- Car's LEFT quarter = `(1280,1536,380,266)` upright, one clean island.
  5 cols x 4 rows of 76x66: col 0 at the door edge, col 4 at the tail
  light; **row 0 (y 1536..1602) is the shoulder top, invisible from the
  side**; the face is rows 1-3 (y ~1620..1800); the arch eats rows 2-3 under
  cols 1-2. Renders ~0.57 px/texel across, ~0.45 down (level side).
- Car's RIGHT quarter = TWO islands. `(1297,600,355,200)` ROTATE_180 is the
  lower band next to the door — only its rows 2-3 (raw y 700..800) show,
  cols 0-2 reach the crease, cols 3-4 sit under the S island.
  `(1536,768,256,96)` ROTATE_180 is the upper shoulder from mid-quarter to
  the light. ~0.45 px/texel both ways.
- So a decal that is one piece on the left is two pieces on the right. Logo
  slot 2 sits on the left island at (1428,1712) w 217 and on the
  right R island at (1403,750) w 212; measured within 2% of each other in
  size and position on level sides (`ffbox.py`).
- The old shoulder map (x = 597.4 + 0.789 X) is 2x off in scale for this
  region. Don't use it for placement.

### Rear centring

Tail-light centre line, lid stripe and bumper stripe all within 1 px in a
dead-rear frame; the Mazda badge's cut-outs interrupt the orange
symmetrically. The bumper stripe's upper and lower halves sit ~3 px apart
(a crease in the valance UV) — accepted.

### Spec map — "Option B, satin race finish"

`spec_from_colour()` classifies every texel by nearest colour (so
anti-aliased edges inherit a neighbour's material) and writes two variants:

    B1  body (0,115,16) satin | papaya (0,45,16) gloss | white (0,80,16) | vinyl (0,95,16) | number blocks (0,40,16)
    B2  same, papaya (255,45,16) metallic

Superseded the same week: B3 "Satin-True" (B4 is B3 with a metallic papaya)
is the default, and B1/B2/B4 stay in `SPEC_VARIANTS` as history.
`car_spec_<id>.tga` is B3 unless built with `--spec-variant`. A normal build
writes only that one finish file; add `--finish-tests` to also write all four
as `car_spec_<id>_B1.tga` … `_B4.tga` for comparing finishes.

### Viewer notes learned the hard way

- The camera is cumulative across `view2.py` calls and the drag→angle
  response is non-linear; sweep in small steps and pick frames.
- `--drag-y` past the zenith flips the yaw; the viewer may also be driven by
  hand between automated calls. Never assume a pose — capture and look.
- The paint dialog closed once mid-session; reopen it by clicking View Car
  (by hand), then `python tools/view2.py --no-reload --wheel N` to re-zoom.


## v4.1 — GOLD MASTER, 2026-09-14 evening. Supersedes v4.0 where they differ.

Approved on the render. Changes since v4.0:

- **Spec map "Satin-True" (B3)** is the default: body (0,170,200), white
  (0,55,30), papaya (0,35,16), vinyl (0,120,150), number blocks (0,60,110),
  plus a 3-texel halo of the papaya material around every orange mark (the
  A-bar, the Ï dots and "RACING" are too small to survive texture filtering
  otherwise). Found with a clearcoat ladder against a control in the viewer;
  the roughness channel barely shows there. `speccheck.py`-style readout
  confirmed every papaya texel on the door wordmark carries the stripe
  material — the door's orange shows no highlight in the viewer only because
  a flat vertical panel reflects nothing bright; the fender crown does.
- **Logo slot 2** is drawn via its helper in `src/sponsors.py`.
- **Logo slot 2 on the rear quarters is placed through fitted affines**
  (`RQ_AFFINE` in `team_mx5.py`; `tools/probe_affine.py` + `tools/fit_affine.py`):
  - car's LEFT island `(1280,1536,380,266)`: screen_x = 0.5963u + 0.1607v − 74.2,
    screen_y = −0.0281u + 0.4988v − 408.3 (level left side at the probe zoom;
    residual 4 px over 15 cells).
  - car's RIGHT island `(1297,600,355,250)`: screen_x = −0.6581u + 0.0925v + 1130.5,
    screen_y = −0.0393u − 0.5927v + 924.7 (residual 4 px over 9 cells). The
    island runs on ABOVE the old rect's top (v to ~840) — probed — which is
    what let the right logo come up level with the left.
  - the logo is one screen rectangle per side, 175 px wide at that zoom,
    centre 45% of the quarter from the door edge, 55% from the crease
    toward the arch; the texels are filled by inverse mapping, so text
    orientation and anisotropy take care of themselves.
- The old per-island placement table (`RQ_PLACE`) is kept behind
  `RQ_USE_AFFINE = False` for reference only.

## Your own design (`--design`, `src/design.py`)

`apply_design()` in `src/team_mx5.py` sets `DESIGN`, `BODY` and `BAND` (both
the design's body colour: the lower band stays body colour), `LINE` (its
trim) and `ACCENT` (its graphic colour) before `build()`; no geometry changes
with the design. The hooks, all in `src/team_mx5.py`:

- **stripe style:** `_fender_bands()` (the fender sash), `_band_rects()`
  (every centre-line group `_vbands()` draws: hood, rear deck, nose, bumper
  top, lip and tail) and the hood feeders (`_feeders()`) go through
  `DESIGN.bands()`, so each keeps only the bands the style draws. The ring
  round the hood badge is a thin line, drawn only when `DESIGN.lines_on`. A
  dropped band leaves the others where they were measured.
- **lettering:** the door wordmark (`flank_panel()`) is `DESIGN.wordmark()` +
  `DESIGN.lettering_box()`, with the small "made with AÏNTOLOGIC" credit; the
  rear valance wordmark passes `credit=False` (the credit rides on the doors).
- **badge:** the hood roundel is `DESIGN.roundel()`.
- **logos and driver strip:** logo spot 2 (rear quarters, through
  `RQ_AFFINE`) is `sponsors.logo_slot(LOGO2, ..., ink=DESIGN.lettering,
  accent=DESIGN.graphic)`; logo spot 1 (boot lid) is
  `sponsors.logo_slot(LOGO1, ..., **DESIGN.logo_colours)`. The driver strip
  takes face / ink / accent from body / lettering / graphic; the tail's
  checker rule takes graphic / `DESIGN.shade` / trim, and its tow arrow is
  graphic on body.
- **finish map:** `spec_from_colour()` uses `DESIGN.spec_values()`,
  `DESIGN.material_keys()` and `DESIGN.stripe_mask()`. `_panel_cover()` puts
  the two door number panels' white texels back to the car's own white
  finish (a no-op in the example scheme), so a design's trim finish (chrome,
  matte) never rims the numbers.
- **fixed on purpose:** the white door number panels (N1, N2) stay `T.WHITE`:
  the sim prints the number on them. The door safety marks (cutoff triangle,
  extinguisher) keep their own white and black.

No design, or `--design example-scheme`, builds the ready-made paint in
`paints/mx5-2016-global-cup/` byte for byte.
