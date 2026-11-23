# Architecture

## Overview

`planes/` turns fold steps into pictures; the repo root is a [deedum](https://github.com/mojzis/deedum)
site (config in `[tool.deedum]` of `pyproject.toml`) whose App makes one page per plane and prints the PDFs after the build.

## Components

- `planes/fold.py`: flat-fold simulator. A `Model` holds convex facets with affine
  maps; `step()` folds along lines and keeps a snapshot before and after each step.
- `planes/models.py`: the planes as fold steps (Arrow family, Albatross, Tube).
- `planes/render.py`: 2D step diagrams (fold lines, arrows) and top views of the
  opened wings.
- `planes/iso.py`: 3D views. Each stack of layers is reduced to its exposed surfaces,
  mapped to 3D (a half-done fold per step, the finished plane, the tube), culled and
  painted far to near.
- `planes/sheets.py`: print CSS, the line legend, and the line sheet: creases that
  lie on the top, front-facing layer when they are folded.
- `planes/data/`: one file per plane (`PLANE = Spec(...)`) or series of planes
  (`SERIES = Series(...)`, e.g. the Arrow lab): words, fold model, stabilizers, flaps.
  `order` sets the catalogue order. Files starting with `_` hold shared bits.
- `planes/spec.py`: the fields a plane or series file can set.
- `planes/build.py`: `Spec` → `Plane`: panels (text, flat SVG, 3D SVG), the "open the
  wings", stabilizer and flap steps, finished picture, line sheet. A plane that is not
  a wing plane (the Tube) passes its own `finish`.
- `planes/catalogue.py`: finds the files in `planes/data/` and builds each plane once.
- `planes/printing.py`: HTML for the two PDFs and the social previews, and
  `write_build_files` (Playwright,
  headless Chromium).
- `planes/video.py`: folding videos. Every frame comes from the fold model
  (`iso.step_view` at 0° to 180°, a fixed camera per view). The frames are rendered
  with rsvg-convert and joined with ffmpeg into `_video/<slug>-<palette>.mp4`.
- `site_app.py`: deedum `App`: catalogue page, plane pages, a page per series, PDFs in
  `after_build`. Templates in `templates/`, CSS in `static/`.

## Flows

`poe site` → deedum loads `site_app.PlanesApp` → `planes()` builds every model once →
pages render from `templates/` → `after_build` prints `<slug>/<slug>-steps.pdf` and
`<slug>/<slug>-lines.pdf` and a 1200x630 `social.png` (the 3D view, used as og:image) into `_site/` → `deedum check` lints links and heads.
