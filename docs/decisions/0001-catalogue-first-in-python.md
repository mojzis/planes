# 0001 Catalogue first, built in Python

Date: 2026-11-22
Status: accepted

## Context

The models were prototyped in Python (fold simulator, SVG diagrams, PDFs through
Chromium). The longer-term plan is one implementation in JavaScript, so a web page can
let you change a plane and export its PDF in the browser. The user asked to start with
a catalogue of the planes already built, on a Python template, published with deedum;
the interactive page can come later.

## Decision

Port the prototype into the `planes` package as is (line-style models only) and build
a static deedum site: a catalogue page, one page per plane with the steps, and two
PDFs per plane printed at build time.

## Consequences

- The catalogue ships now, with pictures that match the fold model.
- The interactive page needs the fold model in JS. When it exists, the static pages
  can be generated from it too, and the Python model retired; until then the Python
  model is the source.
