# Branding

The README banner and the AÏntologic marks used across this repository.

## Assets

- `banner.png`: the README header, rendered by `render_banner.py`.
- `wordmark.png`, `roundel.png`, `checker-rule.png`: the canonical AÏntologic
  marks (code exports of the paint generator's own marks — the custom A, the
  orange crossbar, the slanted diaeresis and the smaller wordmark tail). Do not
  redraw or AI-generate them.
- `fonts/`: Orbitron Variable and Barlow Condensed SemiBold, each with its
  family-specific SIL Open Font License notice.
- `render_banner.py`: a small, deterministic banner layout (Pillow + these
  assets). It does not build paint files.

## Style

| Color | Hex | Role |
| --- | --- | --- |
| Black | `#0C0C0D` | Dominant ground |
| Papaya | `#FF7A00` | Restrained accents |
| White | `#ECECEC` | Type and rules |
| Graphite | `#2E3034` | Dividers |

Orbitron at weight 800 is the display face; Barlow Condensed SemiBold is the
label face. Flat color, generous space.

## Reproduce the banner

From the repository root, with Pillow available:

```text
py assets/brand/render_banner.py "iRacing Paints" "Open source" "SIM RACING / CUSTOM LIVERIES" ""
```

The names and logos here are trademarks — see `TRADEMARKS.md` at the repository
root.
