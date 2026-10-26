# Your own colors and team name

## What and why

Every measured car can wear your own colors and your team name instead of the
black, papaya and white example. You choose them in a **design settings
file**: a small text file you can open in Notepad. The same file works on all
ten measured cars, so every car you race can match.

You don't draw anything. The tools draw your colors through each car's
measured panels, so a stripe still lines up across every panel seam, whatever
color it is.

This came in version 0.3.0
([#5](https://github.com/Aintologic/aintologic-iracing-paints/issues/5)). It
works on path 2 (a command) and path 3 (an AI assistant) of the
[getting-started guide](GETTING-STARTED.md), so you need Python and the four
add-ons. With an AI assistant, you can simply tell it your colors and team
name, and it writes the file for you.

## What "done" looks like

- A file such as `profiles/designs/my-team.json` holds your colors, finishes,
  stripe style and team name.
- Adding `--design my-team` to a build makes any measured car in your design.
- Your team name is on the car where the big AÏNTOLOGIC lettering was, with a
  small "made with AÏNTOLOGIC" line under it.
- The paint and its finish file are in iRacing's paint folder, and the car
  viewer shows your design.

## Try a sample first

Four sample designs come with the project, in `examples/designs/`:

| sample | what it looks like |
|---|---|
| `example-scheme` | the example's black, papaya and white colors, written out. It builds exactly the same paint as no design at all. |
| `neutral` | silver, with a blue stripe and dark lettering, and "YOUR TEAM NAME" as the team name |
| `blue-and-yellow` | deep blue, with a yellow stripe, white lines and "EXAMPLE RACING" |
| `white-and-red` | white, with a red stripe on its own, black lettering and "SAMPLE MOTORSPORT" |

To try one, add `--design` and the sample's name to a build, for example
`--design blue-and-yellow` (the full command is
[below](#build-a-car-with-it)).

## Make your own design

1. In the project folder, make a folder called `profiles` if there isn't one
   yet, and inside it a folder called `designs`.
2. Copy a sample from `examples/designs/` into `profiles/designs/`, and rename
   the copy, for example to `my-team.json`. `neutral.json` is a good start. If
   Windows hides file endings, the file shows as `neutral`: rename it to
   `my-team`, and don't type the `.json` yourself.
3. Open your copy in a plain text editor such as Notepad, change what you like
   (the choices are [below](#the-choices)), and save it. Don't use a word
   processor such as Word: it changes the quote marks, and the file stops
   working.

Git ignores the `profiles` folder, so your design and your team name stay on
your computer and are never published with the project.

### Where the build looks for the file

With `--design my-team`, the build looks in this order and uses the first file
it finds:

1. the file you named, if you gave the path to one, such as
   `--design my-designs/red.json`;
2. `profiles/designs/my-team.json`;
3. `examples/designs/my-team.json`.

So your own copy in `profiles/designs/` wins over a sample with the same name.
You can leave the `.json` off the name. If it finds nothing, it stops and says
where it looked.

## Build a car with it

Open a terminal in the project folder, as in the
[getting-started guide](GETTING-STARTED.md#path-2-personalize-with-a-command),
and add `--design` to a build:

```
python src/team_mx5.py --id 123456 --driver "A. DRIVER" --design my-team
```

**Every car takes `--design`.** Swap `team_mx5.py` for your car's builder from
the README's [table](../README.md#cars-measured-so-far). The six cars with a
one-time setup step need it done first, as for any build. `--design` works
with all the other options in the README's
[path 2](../README.md#path-2-personalize-with-a-command-measured-cars).

The build writes the same two files as always, into the `out` folder:
`car_123456.tga` (the paint) and `car_spec_123456.tga` (the finish). Your
finishes are in the second file, so copy both.

## The choices

A design file looks like this. Every line in it is optional.

```json
{
  "note": "My team's colors.",
  "team_name": "EXAMPLE RACING",
  "badge_text": "ER",
  "colors": {
    "body": "#14306E",
    "graphic": "#FFC20E",
    "trim": "#F2F2F2",
    "lettering": "#F2F2F2"
  },
  "finishes": {
    "body": "metallic",
    "graphic": "gloss",
    "trim": "gloss"
  },
  "stripes": "classic",
  "logo1": "placeholder",
  "logo2": "none"
}
```

Keep the quote marks, colons, commas and curly brackets as they are: each
line but the last in a `{ }` group ends with a comma.

| choice | what it sets | what you can put |
|---|---|---|
| `team_name` | your team name, in place of the big AÏNTOLOGIC lettering | plain letters, numbers and simple punctuation |
| `badge_text` | the big letters in the round badge (on the hood, nose, roof, deck or just in front of the cockpit, depending on the car) | one to three characters; without it, your team name's initials |
| `colors`: `body` | the main color of the car | a color code such as `"#14306E"` |
| `colors`: `graphic` | the wide stripe, and the small details that match it | a color code |
| `colors`: `trim` | the thin lines either side of the stripe, and the ring round the badge | a color code |
| `colors`: `lettering` | your team name, the driver name, and the outline of the "YOUR LOGO" placeholder | a color code |
| `finishes`: `body`, `graphic`, `trim` | how each part takes the light | `gloss`, `satin`, `matte`, `metallic`, `pearl`, `chrome` or `brushed` |
| `stripes` | which stripes are drawn | `classic`, `stripe-only`, `lines-only` or `none` |
| `logo1`, `logo2` | what goes in the car's two logo spots | a picture file, `"none"` or `"placeholder"` |
| `note` | a note to yourself | any text; the build ignores it |

You may also see `layout` in a message. `classic` is the only layout, so you
can leave it out.

### Colors

**Each color is a code like `"#14306E"`:** a `#` and six characters, two each
for red, green and blue, from `00` to `FF`. `"#FFFFFF"` is white and
`"#000000"` is black. Most image editors and online color pickers show this
code for any color; it's often called a hex code. The British spelling,
`colours`, works too.

### Finishes

| finish | what it looks like |
|---|---|
| `gloss` | a deep shine, like fresh paint |
| `satin` | a soft sheen |
| `matte` | flat, with no shine |
| `metallic` | metal flake under a clear coat |
| `pearl` | a little flake: a softer glow than metallic |
| `chrome` | mirror-bright metal |
| `brushed` | rough metal: a dull steel sheen |

The lettering takes the trim's finish. Leave a finish out and that part keeps
the example's: satin for the body, gloss for the stripe, and a slightly softer
gloss for the trim and lettering that no finish name gives exactly. The number
panels keep their own finish in every design. The finishes live in the finish
file, `car_spec_<your ID>.tga`. Without that file in the paint folder, iRacing
shows the car without them.

### Stripes

- `classic`: the wide stripe with a thin line either side, as on the example.
- `stripe-only`: the wide stripe, without the thin lines.
- `lines-only`: the thin lines, without the wide stripe.
- `none`: no stripes.

### Your team name

**Your team name goes wherever the big AÏNTOLOGIC lettering is on that car,**
on one line or two, whichever reads bigger. Shorter names come out bigger.
Under the main lettering, a small "made with AÏNTOLOGIC" line always stays:
it's how the project is credited, and there's no setting to remove it. You
may race the car with it on your own iRacing car (see
[`TRADEMARKS.md`](../TRADEMARKS.md)). Where a car also carries the lettering
in a smaller spot, such as the tail or a wing, your name goes there too,
without the small line.

The round badge (on the hood, nose, roof, deck or just in front of the
cockpit, depending on the car) shows your initials, or your `badge_text`,
with your team name under them, in your colors. With no team name, the lettering stays AÏNTOLOGIC in your colors, and
so does the badge unless you set `badge_text`.

If the lettering can't draw a character in your team name, such as an emoji
or some accented letters, the build stops and says which one.

### Logo spots

`logo1` and `logo2` say what goes in the car's two logo spots:

- **a picture file:** a PNG with a see-through background works best (a JPG
  brings its white background along as a box). The build looks for it from
  the folder you run the command in, so put it in the project folder and
  write just its name, such as `"my-logo.png"`. If you write a full path, use
  forward slashes (`/`) in it, not backslashes (`\`): this file reads a
  backslash differently.
- **`"none"`:** the spot stays the body color.
- **`"placeholder"`:** the "YOUR LOGO" placeholder. This is what you get if
  you leave it out.

`--logo1` and `--logo2` on the command line win over the design file, and the
design file wins over a saved profile. Use only logos you own or have
permission to use (see the README's [notice](../README.md#notice)).

### Leaving things out

**Anything you leave out keeps the example's choice.** A file with nothing
between its curly brackets, `{}`, builds exactly the example paint, byte for
byte, the same as no `--design` at all. So does `example-scheme`. You can
start from that and add one choice at a time.

## What it tells you

**Warnings.** Before it builds, the build checks your colors and prints a
line starting with `note:` for anything that will be hard to see. It still
builds the car; change the color and build again if you agree.

- `note: the lettering colour is close to the body colour, so your team name and driver name may be hard to read`
- `note: the graphic colour and finish are close to the body's, so the wide stripe will barely show`
- `note: the trim colour and finish are close to the body's, so the thin lines will barely show`

A stripe in nearly the body's color still shows when its finish is different,
so the last two only appear when the finish is the same too.

**Mistakes.** If something in the file isn't right, such as a finish it
doesn't know or a missing comma, the build stops before it writes anything
and says what's wrong. For example:

```
design: finishes.body should be one of gloss, satin, matte, metallic, pearl, chrome, brushed, not 'shiny'
```

For a missing comma or quote mark, the message says the file "is not valid
JSON" (JSON is the name of this kind of settings file) and gives a line
number: the mistake is on that line, or at the end of the line just before
it.

Save the file as UTF-8, Notepad's normal choice. If the message says the file
"is not saved as UTF-8 text", open it in Notepad, choose **File**, **Save
as**, set **Encoding** to **UTF-8** and save it again.

## What it doesn't do yet

- **The logo spots stay where they are.** Each car has its two logo spots in
  fixed places, shown in its map in [`car-maps/`](car-maps/). A design picks
  what goes in them, not where they are.
- **The stripes keep each car's layout.** A design picks their colors and
  which ones show, not their shape or where they run.
- **The number panels stay white,** with their own finish, in every design,
  because iRacing prints your car number on them.

## Get it into iRacing

Copy both files from the `out` folder into the car's paint folder, as in step
6 of [path 2 in the getting-started guide](GETTING-STARTED.md#path-2-personalize-with-a-command),
then [open the car in the car viewer](GETTING-STARTED.md#see-it-on-the-car).
If a file with the same name is already there, move it somewhere safe first.

## For the AI agent

- The format and every allowed value are in the docstring of `src/design.py`;
  `src/personalize.py` gives every builder `--design`. Each car's map in
  `docs/car-maps/` has a "Your own design" note on how that car uses it.
- Turn the colors the client describes into `"#RRGGBB"` codes, write their
  design to `profiles/designs/<name>.json` (never into `examples/designs/`),
  and show a preview before the final files. Tell them about any `note:` line
  in plain words.
- If the client gives colors but no team name, tell them the AÏNTOLOGIC
  lettering stays on the car (and the badge, unless they choose
  `badge_text`), and ask for a team name.
- Never remove or hide the "made with AÏNTOLOGIC" line, and don't move a logo
  spot by changing a builder's coordinates. If the client wants a logo
  somewhere else, say plainly that it isn't possible yet.
- A build with no design, or with `--design example-scheme`, must stay byte
  for byte the same as `paints/`. `python tools/check_builds.py` checks that,
  and builds every car with every sample design.
