# 0004 One file per plane

Date: 2026-11-22
Status: accepted

## Context

Adding the Arrow lab took about 380 lines: a builder per plane family in
`catalogue.py`, and one-off code for the lab page, PDFs and score card. The user had
hoped adding planes would be mostly automatic, and asked to build it ("cool, lets build
it then").

## Decision

- A plane is one Python file in `planes/data/` that sets `PLANE = Spec(...)`: words,
  fold model, stabilizers, flaps. A series of planes (the Arrow lab) is one file that
  sets `SERIES = Series(...)`.
- Files are found automatically; `order` sets where they appear.
- One generic builder (`planes/build.py`) makes the panels, 3D views, "open the wings",
  stabilizer and flap steps, and the line sheet. A plane that doesn't open wings (the
  Tube) passes its own `finish`.
- A series gets its page, whole-series PDF, score card and home-page teaser from its
  file.
- The files are Python, not TOML, so fold lines can be computed (`C / 2`).

## Consequences

- Output stayed the same, except two small corrections: Stingray's flap picture now
  shows the stabilizer lines, and Albatross's stabilizer lines start at 8 cm in the top
  view, as on its line sheet.
- The fold steps themselves are still written by hand in `models.py` (or in the
  plane's file).
