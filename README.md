# Paper planes

Original paper planes for kids who just started folding: not hard, a little
extravagant. Each plane has a web page with step-by-step pictures (a flat diagram and
a 3D view per step) and two A4 PDFs:

- **Steps**: the same pictures, numbered, with flying tips.
- **Line sheet**: print it, fold on the lines (blue valley, red mountain), cut the
  black ones. Only the creases on the top layer are printed; folds through several
  layers are on the steps sheet.

No printer? The steps give every size in cm, so a plain A4 sheet works.

Site: <https://mojzis.github.io/planes/>

## The planes

| Plane | What | Scissors |
| --- | --- | --- |
| Arrow | heavy-nosed dart for distance, optional fin | no |
| Arrow Lock | blunt nose held by a lock flap | no |
| Arrow Blunt | Arrow with the point folded back | no |
| Stingray | wide, slow glider with trim flaps | 4 small cuts |
| Albatross | landscape glider with a rolled front edge | 4 small cuts |
| Tube | a rolled band, thrown with a spin | no |

## How it works

The pictures come from a small flat-fold simulator: the sheet is split into convex
facets, and each fold reflects the facets on one side of a line. The same model draws
the step diagrams, the 3D views and the line sheet, so they always match the real
folds. See [docs/architecture.md](docs/architecture.md).

## Build

```sh
uv sync
uv run playwright install chromium   # once: the PDFs are printed with Chromium
uv run poe site                      # site + PDFs into _site/, then lint
uv run poe serve                     # live preview, without PDFs
uv run poe check                     # lint, types, tests
```

GitHub Actions builds and publishes the site on every push to `main`.
