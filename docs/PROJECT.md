# Project

## What this is

A standardised AÏntologic example paint scheme that can be applied to any
iRacing car you drive, so you are recognisable on track across every series.

## Who it serves

You, racing under the AÏntologic example identity. The generator ships the
scheme as an example you personalize with your own details:

| flag | what it sets |
|---|---|
| `--id <id>` | your iRacing customer ID; the build writes `car_<id>.tga` |
| `--driver <name>` | the name shown on the driver strip |
| `--logo1 <image>` | the image dropped into logo slot 1 |
| `--logo2 <image>` | the image dropped into logo slot 2 |

With no flags the output carries a neutral "YOUR LOGO" placeholder in both logo
slots and a blank driver strip, so it is safe to build and view before you have
supplied anything.

Each build writes one paint file, `car_<id>.tga`, for the customer ID you pass.
If you already run a hand-made livery on another account, keep it out of this
repo — the generator never manages or overwrites a file it did not build.

## What matters now

The MX-5 (Global Mazda MX-5 Cup) is car one. It establishes the design
language: black base, forest-green lower sweep with an antique-gold hairline,
cream AÏNTOLOGIC wordmark on the doors, oversized AÏ mark on the hood.

## What must not break

- Graphics must sit on the right panels, right way up, on **both** sides.
- iRacing's number blocks stay clear and readable.
- The livery must read as AÏntologic at racing speed, not just up close.
- Artwork stays reproducible from source so the next car is cheap.

## How success is recognised

Someone sees the car and thinks "that's a good-looking race car — what is
AÏntologic?" Then the same design language goes onto a second car and the two
obviously belong to the same team.

## Brand

AÏntologic is a creative identity built around "what is real?" — simulation,
observation, hidden systems. Premium and deliberate, never generic-AI clichés:
no falling code, no circuit boards, no neon cyberpunk.

Palette: bone `#EFE4D0`, forest `#1D3A31`, rust `#C0552A`, antique gold
`#C69A3F`, on warm near-black `#0B0C0E`.
