"""Turn a plane file (``Spec``) into everything its page and PDFs show (``Plane``).

Every fold step gets a flat diagram and a 3D view of the fold half done. The wing
fold of a wing plane is shown on the folded plane instead, and an ``Optional`` step
(the beak) on the plane with its halves pressed together. Wing planes then get the
"open the wings" step, stabilizers and flaps from their ``Spec``.
"""

import html
from dataclasses import dataclass
from typing import Any

from . import iso, render
from .render import state_svg, wing_views
from .sheets import line_el, line_sheet_svg, visible_creases
from .spec import Spec

render.DECO_ID = "back"


@dataclass
class Panel:
    """One step: its number (None for the closing panel), text as HTML, pictures."""

    n: int | None
    text: str
    flat: str | None = None
    view3d: str | None = None
    optional: bool = False


@dataclass
class Plane:
    """Everything a plane's web page and PDFs show."""

    slug: str
    title: str
    sub: str
    badges: list[str]
    tips: str
    panels: list[Panel]
    line_sheet: str
    width: float
    height: float
    finished: str | None = None
    scissors: bool = False
    box: str | None = None  # extra box under the title, as HTML
    series: str | None = None

    @property
    def name(self) -> str:
        """The title in normal case, for headings and links."""
        return self.title.title()


def view(surfs, yaw=-18, pitch=52, w=300, h=190, **kw) -> str:
    """A 3D view as SVG."""
    return iso.svg(surfs, yaw, pitch, w, h, **kw)


def _text(step) -> str:
    txt = html.escape(step["text"]).replace("Optional beak:", "<b>Beak:</b>")
    return ("Start with a plain A4 sheet. " + txt) if step["n"] == 1 else txt


def _optional(step) -> bool:
    return step["text"].startswith("Optional")


def _mirror_last(creases, model, w):
    """The last fold is done on both halves; the line sheet shows both."""
    c, wn = w / 2, len(model.steps)
    return creases + [
        (n, k, (2 * c - a[0], a[1]), (2 * c - b[0], b[1]))
        for n, k, a, b in creases
        if n == wn
    ]


class _Wings:
    """The folded wing plane of a model, drawn in 3D and from the top."""

    def __init__(self, d: dict[str, Any]) -> None:
        self.d = d
        self.c = d["w"] / 2

    def plane3d(self, st, **kw):
        d = self.d
        return iso.plane3d(
            st, self.c, d["hinge"], d["near"], d["far"], tab=d.get("tab"), **kw
        )

    def top(self, st, overlay=""):
        d = self.d
        views = wing_views(
            st, d["hinge"], d["near"], d["far"], 300, 210, pad=8, overlay=overlay
        )
        return views["top"]


def _step_panels(spec: Spec, d: dict[str, Any]) -> list[Panel]:
    m = d["m"]
    wings = _Wings(d) if "hinge" in d else None
    wn = len(m.steps)
    panels = []
    for s in m.steps:
        opt = _optional(s)
        if wings and opt:
            v = view(wings.plane3d(s["after"], dihedral=-89), 300, 25)
        elif wings and s["n"] == wn:
            v = view(wings.plane3d(s["before"], dihedral=-40), 120, 35)
        else:
            v = view(iso.step_view(s))
        flat = state_svg(s["before"], "back", 300, spec.flat_height, s["lines"])
        panels.append(Panel(s["n"], _text(s), flat, v, optional=opt))
    return panels


def _marks(spec: Spec, d: dict[str, Any]) -> tuple[str, list]:
    """Flaps and stabilizer bend lines: an overlay for the top view (folded plane
    coordinates) and extra line-sheet segments (sheet coordinates)."""
    hg, w, h = d["hinge"], d["w"], d["h"]
    overlay, extra = "", []
    if f := spec.flaps:
        for sg in (-1, 1):
            for x in (f.x0, f.x1):
                overlay += line_el(
                    (hg + sg * x, h), (hg + sg * x, h - f.depth), "cut", 1.4
                )
            overlay += line_el(
                (hg + sg * f.x0, h - f.depth),
                (hg + sg * f.x1, h - f.depth),
                "bend",
                1.4,
            )
        for xs in ((hg + f.x0, hg + f.x1), (w - hg - f.x0, w - hg - f.x1)):
            extra.extend((0, "cut", (x, h), (x, h - f.depth), None) for x in xs)
            extra.append((0, "bend", (xs[0], h - f.depth), (xs[1], h - f.depth), None))
        extra[0] = (*extra[0][:4], "cut")
    s = spec.stabilizers
    if s and s.sheet_from is not None:
        for sg in (-1, 1):
            x = hg + sg * (w - hg - s.size)
            overlay += line_el((x, s.sheet_from), (x, h), "bend", 1.4)
        extra.extend(
            (0, "bend", (x, s.sheet_from), (x, h), "tip") for x in (w - s.size, s.size)
        )
    return overlay, extra


def _wing_finish(spec: Spec, d: dict[str, Any]) -> tuple[list[Panel], str, list]:
    """The steps after the folds: open the wings, stabilizers, flaps."""
    wings, m = _Wings(d), d["m"]
    st = m.steps[-1]["before"]
    n = len(m.steps)
    stab = spec.stabilizers
    wl = None
    if stab:
        wl = max(v[0] for f in st for v in f.cur()) - d["hinge"] - stab.size
    overlay, extra = _marks(spec, d)
    marked = wings.top(st, overlay) if overlay else None
    merged = bool(stab and not stab.own_panel)
    done = wings.plane3d(st, dihedral=spec.dihedral, winglet=wl)
    panels = [
        Panel(
            n + 1,
            spec.open_text + (f" {stab.text}" if stab and merged else ""),
            (marked if merged and marked else wings.top(st)),
            view(
                done if merged else wings.plane3d(st, dihedral=spec.dihedral), 120, 35
            ),
        )
    ]
    if stab and not merged:
        panels.append(
            Panel(
                len(panels) + n + 1,
                stab.text,
                None,
                view(done, 120, 35, h=230) + view(done, 180, 8, h=150),
            )
        )
    if spec.flaps:
        panels.append(
            Panel(len(panels) + n + 1, spec.flaps.text, marked or wings.top(st))
        )
    return panels, view(done, *spec.finish_view, 600, 330), extra


def build(spec: Spec) -> Plane:
    """Everything the page and PDFs of ``spec`` show."""
    d = spec.model()
    m, w, h = d["m"], d["w"], d["h"]
    panels = _step_panels(spec, d)
    creases = visible_creases(m)
    if spec.finish:
        more, finished = spec.finish(d)
        extra: list = []
    else:
        more, finished, extra = _wing_finish(spec, d)
        creases = _mirror_last(creases, m, w)
    skip = {s["n"] for s in m.steps if _optional(s)}
    creases = [cr for cr in creases if cr[0] not in skip]
    return Plane(
        slug=spec.slug,
        title=spec.title,
        sub=spec.sub,
        badges=list(spec.badges),
        tips=spec.tips,
        panels=panels + more,
        line_sheet=line_sheet_svg(spec.title, w, h, creases, extra, spec.sheet_note),
        width=w,
        height=h,
        finished=finished,
        scissors=spec.flaps is not None,
        box=spec.box,
        series=spec.series,
    )
