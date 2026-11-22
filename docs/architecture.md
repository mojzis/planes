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
- `planes/catalogue.py`: a `Plane` per model: panels (text, flat SVG, 3D SVG), tips,
  badges, finished picture, line sheet. `ORDER` is the catalogue order.
- `planes/printing.py`: HTML for the two PDFs and the social previews, and
  `write_build_files` (Playwright,
  headless Chromium).
- `site_app.py`: deedum `App`: catalogue page, plane pages, PDFs in
  `after_build`. Templates in `templates/`, CSS in `static/`.

## Flows

`poe site` → deedum loads `site_app.PlanesApp` → `planes()` builds every model once →
pages render from `templates/` → `after_build` prints `<slug>/<slug>-steps.pdf` and
`<slug>/<slug>-lines.pdf` and a 1200x630 `social.png` (the 3D view, used as og:image) into `_site/` → `deedum check` lints links and heads.
