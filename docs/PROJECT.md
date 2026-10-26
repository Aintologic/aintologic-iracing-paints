# Project

## What and why

iRacing Paints helps people paint their own iRacing cars with an AI assistant.
The person describes the car they want, like hiring a painter. The AI asks
questions, shows a preview, and builds the paint once it's approved. The tools
here handle the hard part: placing stripes, names and logos accurately across
iRacing's flattened car templates.

Because the tools measure each car from iRacing's own paint template, they work
on any car in iRacing, including cars released after this project. The ten cars
already measured were chosen to cover the main kinds of car (formula, prototype,
GT, road-based cup car). They, and the black, papaya and white AÏntologic scheme
they wear, are examples. They are not the point.

It is for anyone who races in iRacing and wants a good-looking car of their own,
whether or not they can draw, use an image editor or write code.

It is not an official iRacing tool, not a paint-sharing service, and not a
showcase of one team's scheme.

## What "done" looks like

The project is doing its job when:

- Someone who has never painted a car can describe one, approve a preview, and
  race it, on any car they choose.
- A car the project has never seen can be measured and painted by following the
  documented method, without guessing.
- Graphics sit on the right panels, the right way up, on **both** sides of the
  car, and iRacing's number areas stay clear and readable.
- The same inputs always build the same paint, so a design can be rebuilt or
  moved to another car cheaply.
- The person stays in charge: nothing installs itself, nothing is overwritten
  without permission, and nothing private is shared.

Planned next steps are tracked as
[issues](https://github.com/Aintologic/aintologic-iracing-paints/issues): the
rest of your own design (colors, finishes, stripe style and a team name came
in 0.3.0; other stripe layouts and choosing where the logos go aren't in yet),
the full brief-to-delivery workflow, a delivery pack with a Trading Paints
guide, and cars that aren't on the list.

## For the AI agent

- Start with `AGENTS.md`; it defines your role and rules.
- The example scheme (palette, marks, placement rules) is documented in
  `docs/PAINT-SCHEME.md`. Its palette is black `#0C0C0D`, papaya `#FF7A00`
  (accent only), white `#ECECEC` and graphite `#2E3034`.
- The build method is in `docs/IRACING-PAINTING-PLAYBOOK.md`; how a car's panel
  layout is measured is in `docs/PANEL-PROBING.md`; each car's verified panel
  map is in `docs/car-maps/`.
- Personalization options (`--id`, `--driver`, `--logo1`, `--logo2`, `--out`,
  `--profile`, `--design`) are shared by every builder through
  `src/personalize.py`. Defaults are neutral: a blank driver strip and a
  "YOUR LOGO" placeholder. `--design` reads a design settings file
  (`src/design.py`, `docs/YOUR-OWN-DESIGN.md`); without it, the example
  scheme.
