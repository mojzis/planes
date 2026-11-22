"""The planes: each one's steps, pictures, tips and line sheet, from the fold model."""

import html
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache

from . import iso, render
from .models import albatross, arrow, arrow_blunt, arrow_lock, tube
from .render import state_svg, wing_views
from .sheets import TUBE_THROW, TUBE_TUCK, line_el, line_sheet_svg, visible_creases

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

    @property
    def name(self) -> str:
        """The title in normal case, for headings and links."""
        return self.title.title()


ARROW_TIPS = (
    "<b>Throw</b> hard and straight, slightly upwards, outdoors or down a long "
    "hallway. <b>Dives?</b> Bend the last 3 mm of the back of both wings up. "
    "<b>Climbs then drops?</b> Flatten those bends. <b>Curves?</b> Make both wings "
    "and both stabilizers exactly equal. Sharp creases = longer flights: run a "
    "fingernail along every fold."
)
FLAP_TIPS = (
    "<b>Dives?</b> Bend both flaps up a bit more. <b>Climbs and stalls?</b> Bend the "
    "flaps down a little. <b>Turns left?</b> Bend the right flap up a little more "
    "(and the other way round)."
)

ARROWS = {
    "arrow": (
        "ARROW",
        "A heavy-nosed dart made for distance, with wing-tip stabilizers and an "
        "optional fin.",
    ),
    "arrow-lock": (
        "ARROW LOCK",
        "An Arrow with a blunt nose held by a lock flap. Tough, and it flies far "
        "and straight.",
    ),
    "arrow-blunt": (
        "ARROW BLUNT",
        "The heavy Arrow with its point folded back: safer indoors, still fast.",
    ),
    "stingray": (
        "STINGRAY",
        "A wide, slow glider with a locked blunt nose, stabilizers and trim flaps.",
    ),
}
ORDER = ["arrow", "arrow-lock", "arrow-blunt", "stingray", "albatross", "tube"]


def _iso(surfs, yaw=-18, pitch=52, w=300, h=190, **kw) -> str:
    return iso.svg(surfs, yaw, pitch, w, h, **kw)


def _flat(step, h=210) -> str:
    return state_svg(step["before"], "back", 300, h, step["lines"])


def _text(step) -> str:
    txt = html.escape(step["text"]).replace("Optional beak:", "<b>Beak:</b>")
    return ("Start with a plain A4 sheet. " + txt) if step["n"] == 1 else txt


def _flaps(hg, h, x0, x1, depth):
    """Overlay and line-sheet segments for two trim flaps cut into each wing."""
    overlay = ""
    for sg in (-1, 1):
        for x in (x0, x1):
            overlay += line_el((hg + sg * x, h), (hg + sg * x, h - depth), "cut", 1.4)
        overlay += line_el(
            (hg + sg * x0, h - depth), (hg + sg * x1, h - depth), "bend", 1.4
        )
    return overlay


def _flap_lines(w, h, hg, x0, x1, depth, tip_x, tip_y):
    extra = []
    for xs in ((hg + x0, hg + x1), (w - hg - x0, w - hg - x1)):
        extra.extend((0, "cut", (x, h), (x, h - depth), None) for x in xs)
        extra.append((0, "bend", (xs[0], h - depth), (xs[1], h - depth), None))
    extra[0] = (*extra[0][:4], "cut")
    extra.extend((0, "bend", (x, tip_y), (x, h), "tip") for x in (w - tip_x, tip_x))
    return extra


def _mirror_last(creases, model, w):
    """The last fold is done on both halves; the line sheet shows both."""
    c, wn = w / 2, len(model.steps)
    return creases + [
        (n, k, (2 * c - a[0], a[1]), (2 * c - b[0], b[1]))
        for n, k, a, b in creases
        if n == wn
    ]


def _arrow_family(slug: str) -> Plane:
    makers: dict[str, Callable[[], dict]] = {
        "arrow": arrow,
        "arrow-lock": arrow_lock,
        "arrow-blunt": arrow_blunt,
        "stingray": lambda: arrow_lock(22),
    }
    d = makers[slug]()
    m, c, tab = d["m"], d["w"] / 2, d["tab"]
    stingray = slug == "stingray"

    def plane3d(st, **kw):
        return iso.plane3d(st, c, d["hinge"], d["near"], d["far"], tab=tab, **kw)

    title, sub = ARROWS[slug]
    wn = len(m.steps)
    panels = []
    for s in m.steps:
        beak = bool(tab) and s["n"] == 7
        if beak:
            v = _iso(plane3d(s["after"], dihedral=-89), 300, 25)
        elif s["n"] == wn:
            v = _iso(plane3d(s["before"], dihedral=-40), 120, 35)
        else:
            v = _iso(iso.step_view(s))
        panels.append(Panel(s["n"], _text(s), _flat(s), v, optional=beak))
    st = m.steps[-1]["before"]
    wl = max(v[0] for f in st for v in f.cur()) - d["hinge"] - 11
    views = wing_views(st, d["hinge"], d["near"], d["far"], 300, 210, pad=8)
    panels.append(
        Panel(
            wn + 1,
            "Open the wings so they are flat or in a very shallow V. Pinch the body "
            "together under the wings.",
            views["top"],
            _iso(plane3d(st, dihedral=6), 120, 35),
        )
    )
    done = plane3d(st, dihedral=6, winglet=wl)
    panels.append(
        Panel(
            wn + 2,
            "<b>Stabilizers:</b> bend the outer 1 cm at the back of each wing straight "
            "up. They keep it flying straight (tested: they help!).",
            None,
            _iso(done, 120, 35, h=230) + _iso(done, 180, 8, h=150),
        )
    )
    extra = []
    hg, w, h = d["hinge"], d["w"], d["h"]
    if stingray:
        overlay = _flaps(hg, h, 30, 52, 18)
        top = wing_views(st, hg, d["near"], d["far"], 300, 210, pad=8, overlay=overlay)
        panels.append(
            Panel(
                wn + 3,
                "With a grown-up, cut 2 slits 1.8 cm long, 2 cm apart, into the back "
                "of each wing. Bend the flaps up a little.",
                top["top"],
            )
        )
        extra = _flap_lines(w, h, hg, 30, 52, 18, 11, 235)
        tips = (
            "<b>Throw</b> gently and level, like letting go of a bird. "
            + FLAP_TIPS
            + " Keep the stabilizers equal and straight up."
        )
        note = "Cut the black lines with a grown-up."
        badges = ["Floats far", "Medium", "Scissors for 4 small cuts"]
    else:
        tips = ARROW_TIPS
        note = "Some later folds go through layers: follow the steps pages."
        badges = ["Goes far", "Easy-medium", "No scissors"]
    creases = _mirror_last(visible_creases(m), m, w)
    if slug == "arrow":
        creases = [cr for cr in creases if cr[0] != 7]
    return Plane(
        slug=slug,
        title=title,
        sub=sub,
        badges=badges,
        tips=tips,
        panels=panels,
        line_sheet=line_sheet_svg(title, w, h, creases, extra, note),
        width=w,
        height=h,
        finished=_iso(done, 120, 32, 600, 330),
        scissors=stingray,
    )


def _albatross() -> Plane:
    d = albatross()
    m, hg, c, w, h = d["m"], d["hinge"], d["w"] / 2, d["w"], d["h"]

    def plane3d(st, **kw):
        return iso.plane3d(st, c, hg, d["near"], d["far"], **kw)

    n = len(m.steps)
    panels = []
    for s in m.steps:
        if s["n"] == n:
            v = _iso(plane3d(s["before"], dihedral=-40), 120, 35)
        else:
            v = _iso(iso.step_view(s))
        panels.append(Panel(s["n"], _text(s), _flat(s), v))
    st = m.steps[-1]["before"]
    half = w - hg
    overlay = _flaps(hg, h, 35, 65, 20)
    for sg in (-1, 1):
        x = hg + sg * (half - 25)
        overlay += line_el((x, 75), (x, h), "bend", 1.4)
    top = wing_views(st, hg, d["near"], d["far"], 300, 210, pad=8, overlay=overlay)
    top = top["top"]
    panels.append(
        Panel(
            n + 1,
            "Open the wings flat. <b>Stabilizers:</b> bend the last 2.5 cm of each "
            "wing tip straight up.",
            top,
            _iso(plane3d(st, dihedral=4, winglet=half - 25), 120, 35),
        )
    )
    panels.append(
        Panel(
            n + 2,
            "With a grown-up, cut 2 slits 2 cm long, 3 cm apart, into the back of "
            "each wing. Bend the flaps up a little.",
            top,
        )
    )
    tips = (
        "<b>Throw</b> gently and level, let it go rather than throw it. Launch from "
        "high up for the longest glides. <b>Dives?</b> Bend the flaps up more. "
        "<b>Stalls (swoops up and drops)?</b> Flatten the flaps. <b>Turns left?</b> "
        "Bend the right flap up a bit more, and the other way round."
    )
    extra = _flap_lines(w, h, hg, 35, 65, 20, 25, 80)
    creases = _mirror_last(visible_creases(m), m, w)
    note = "Cut the black lines with a grown-up."
    return Plane(
        slug="albatross",
        title="ALBATROSS",
        sub="A wide, long-winged glider with stabilizers and trim flaps.",
        badges=["Glides far", "Medium", "Scissors for 4 small cuts"],
        tips=tips,
        panels=panels,
        line_sheet=line_sheet_svg("ALBATROSS", w, h, creases, extra, note),
        width=w,
        height=h,
        finished=_iso(plane3d(st, dihedral=4, winglet=half - 25), 125, 30, 600, 330),
        scissors=True,
    )


def _tube() -> Plane:
    d = tube()
    m, w, h = d["m"], d["w"], d["h"]
    panels = [
        Panel(s["n"], _text(s), _flat(s, 200), _iso(iso.step_view(s))) for s in m.steps
    ]

    def tube3d(frac):
        return iso.tube3d(m.facets, w, frac=frac)

    panels.append(
        Panel(
            4,
            "Gently bend the sheet into a round tube, with the band on the inside.",
            None,
            _iso(tube3d(0.6), 25, 18, h=260, outline=False),
        )
    )
    panels.append(
        Panel(
            5,
            "Slide one end of the band about 3 cm into the other end so the tube "
            "holds. Make it nice and round.",
            TUBE_TUCK,
            _iso(tube3d(1.0), 25, 18, h=190, outline=False),
        )
    )
    panels.append(
        Panel(
            None,
            "<b>Throw it band first</b>: hold the back end from below and push it off "
            "forward with a little spin.",
            TUBE_THROW,
        )
    )
    tips = (
        "<b>Throw</b> it like a gentle dart, band first, level. Hold it underneath at "
        "the plain end. <b>Wobbles?</b> Make the tube rounder and the overlap even. "
        "<b>Drops fast?</b> Throw it a bit harder. Try: who can throw it through a "
        "hula hoop?"
    )
    sheet = line_sheet_svg(
        "TUBE", w, h, visible_creases(m), [], "Fold on lines 1, 2, 3 in order."
    )
    return Plane(
        slug="tube",
        title="TUBE",
        sub="Doesn't look like a plane at all, but it flies straight and far.",
        badges=["Weird & fun", "Easy", "No scissors"],
        tips=tips,
        panels=panels,
        line_sheet=sheet,
        width=w,
        height=h,
        finished=_iso(tube3d(1.0), 25, 18, 600, 330, outline=False),
    )


@cache
def plane(slug: str) -> Plane:
    """Build one plane by its slug (see ``ORDER``)."""
    if slug in ARROWS:
        return _arrow_family(slug)
    if slug == "albatross":
        return _albatross()
    if slug == "tube":
        return _tube()
    msg = f"unknown plane {slug!r}; known: {', '.join(ORDER)}"
    raise KeyError(msg)


def planes() -> list[Plane]:
    """All planes, in catalogue order."""
    return [plane(s) for s in ORDER]
