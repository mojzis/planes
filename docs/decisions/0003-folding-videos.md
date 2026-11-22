# 0003 Folding videos: folding only, from the fold model, a girl's voice

Date: 2026-11-22
Status: accepted

## Context

The user: "lets try to create a scenario for the first arrow that could be used by the
cecil system to create a video - i guess we could just animate the folding, for
starters no extra pics, just the folding. some decent, maybe girl like voice from the
local model. later we could have some "mascots" - for the whole page and for each
plane (but lets save on $$ for now)"

## Decision

- Folding videos are made with cecil. The first is the Arrow:
  [video/arrow-folding.md](../video/arrow-folding.md).
- For now a video shows only the folding: the sheet on a plain background, each fold
  animated. No mascot, no generated pictures, so nothing is spent on image models.
- Every frame comes from the fold model, the same as the steps page.
- The narration is a friendly girl's voice from a local TTS model.
- English first (asked which language goes first, the user picked English,
  2026-11-22). The scenario keeps the Czech text for when cecil has a Czech voice.

## Consequences

- The planes repo needs a frame exporter (fixed camera and scale per view).
- cecil needs a way to play program-made frames, and a Czech voice for the Czech
  version.
- Mascots (one for the site, one per plane) wait until there is budget for pictures.
