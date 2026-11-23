"""Folding animation: every frame from the fold model, one fixed camera per view.

`uv run python -m planes.video arrow [palette]` writes `_video/arrow-<palette>.mp4`
(palettes: night, the default, and peach; needs rsvg-convert and ffmpeg). Pictures
only for now; voice and music come later (decision 0003).

Layout: the folding on a stage at the left; a card at the right with the step number,
where this step is going (its folded result) and a dot per step.
"""

import math
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path

from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union

from . import iso
from .catalogue import _files

FPS = 24
W, H = 960, 540  # SVG units; rendered at 2x = 1920 x 1080
SCALE = 2
STAGE = 660  # width of the stage; the card is right of it
CARD = (684, 60, 246, 420)  # x, y, w, h
TABLE = (-18, 52)  # yaw, pitch: the sheet on the table, as on the steps page
PLANE = (120, 35)  # the finished plane from the side, as on the site
FONT = "font-family=\"'Nunito', 'Quicksand', sans-serif\" font-weight=\"800\""


@dataclass(frozen=True)
class Palette:
    bg: str
    front: tuple[int, int, int]  # the paper's top side
    back: tuple[int, int, int]  # its other side: shows every fold
    edge: str
    accent: str  # fold lines, the current dot
    card: str
    ink: str  # text, done dots
    faint: str  # dots to come


PALETTES = {
    "peach": Palette(
        bg="#faf4ea",
        front=(255, 255, 255),
        back=(255, 196, 150),
        edge="#6b5446",
        accent="#e76f51",
        card="#ffffff",
        ink="#6b5446",
        faint="#e9ddd0",
    ),
    "night": Palette(
        bg="#1d2b45",
        front=(255, 255, 255),
        back=(150, 210, 236),
        edge="#1d2b45",
        accent="#ffbe3d",
        card="#26375a",
        ink="#f4f1ea",
        faint="#3a4d74",
    ),
}


@dataclass
class Timing:
    before: float = 1.2  # the sheet still, its fold line shown
    fold: float = 2.0  # one fold, eased
    after: float = 1.5  # the folded paper still
    open_wings: float = 2.0
    spin: float = 6.0  # the finished plane turning


@dataclass
class Shot:
    surfs: list
    cam: tuple[float, float]  # yaw, pitch
    view: str  # shots of one view share one framing
    step: int  # 1-based; the card shows it
    frames: int = 1
    frames_view: bool = False  # the framing is made to fit this shot
    lines: list = field(default_factory=list)  # fold lines, 3D segments


def ease(t: float) -> float:
    return 0.5 - 0.5 * math.cos(math.pi * t)


def _inner(svg: str) -> str:
    """The content of an `iso.svg` picture, to place inside another."""
    return svg.split(">", 1)[1].rsplit("</svg>", 1)[0] if svg else ""


def _union(boxes):
    return (
        min(b[0] for b in boxes),
        max(b[1] for b in boxes),
        min(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def _grow(b, k=0.12):
    """Room around the held pictures for the flaps in mid-air."""
    dx, dy = (b[1] - b[0]) * k, (b[3] - b[2]) * k
    return b[0] - dx, b[1] + dx, b[2] - dy, b[3] + dy


def _fold_angles(seconds: float, there_and_back: bool) -> list[float]:
    n = max(2, round(seconds * FPS))
    ts = [ease(i / (n - 1)) for i in range(n)]
    if there_and_back:
        return [180 * math.sin(math.pi * t) for t in ts]
    return [180 * t for t in ts]


def _flat(state) -> list:
    """A folded state lying still on the table."""
    return iso.step_view({"before": state, "lines": [], "unfold": False}, 0)


def _fold_lines(step) -> list:
    """The step's fold lines where they cross the paper, a little above it."""
    paper = unary_union([Polygon(f.cur()).buffer(0) for f in step["before"]])
    out = []
    for ln in step["lines"]:
        seg = LineString([ln["p"], ln["q"]]).intersection(paper)
        for part in getattr(seg, "geoms", [seg]):
            if part.geom_type == "LineString" and part.length > 1:
                (ax, ay), (bx, by) = part.coords[0], part.coords[-1]
                out.append(((ax, -ay, 1.2), (bx, -by, 1.2), ln["kind"]))
    return out


def shots(slug: str, t: Timing) -> tuple[list[Shot], list[tuple[list, tuple]]]:
    """Every picture of the video in order, and each step's result (surfs, camera)."""
    d = _files()[0][slug].model()
    # the optional steps (the Arrow's beak) are left out, as in the scenario
    steps = [s for s in d["m"].steps if not s["text"].startswith("Optional")]
    wings = "hinge" in d  # the last step folds the wings: shown in the plane view
    table = steps[:-1] if wings else steps
    out, goals = [], []
    for n, s in enumerate(table, 1):
        full = {**s, "unfold": False}  # step_view halves the angle of an unfold
        still = round(t.before * FPS)
        before = _flat(s["before"])
        out.append(Shot(before, TABLE, "table", n, still, True, _fold_lines(s)))
        for a in _fold_angles(t.fold, s["unfold"]):
            # 179, not 180: at 180 the flap would cut to the flat picture anyway
            out.append(Shot(iso.step_view(full, min(a, 179)), TABLE, "table", n))
        after = _flat(s["after"])
        out.append(Shot(after, TABLE, "table", n, round(t.after * FPS), True))
        goals.append((after, TABLE))
    if wings:
        c = d["w"] / 2
        state = steps[-1]["before"]
        n = len(steps)

        def plane(dih, frames=1, yaw=PLANE[0]):
            surfs = iso.plane3d(
                state, c, d["hinge"], d["near"], d["far"], dih, tab=d.get("tab")
            )
            return Shot(surfs, (yaw, PLANE[1]), "plane", n, frames, True)

        out.append(plane(-89, round(t.before * FPS)))
        k = round(t.open_wings * FPS)
        out += [plane(-89 + 95 * ease(i / (k - 1))) for i in range(k)]
        out.append(plane(6, round(t.after * FPS)))
        goals.append((out[-1].surfs, PLANE))
        k = round(t.spin * FPS)
        # a slow look around, there and back
        out += [
            plane(6, yaw=PLANE[0] + 30 * math.sin(2 * math.pi * i / k))
            for i in range(k)
        ]
    return out, goals


def _card(n: int, goals, pal: Palette) -> str:
    x, y, w, h = CARD
    total = len(goals)
    colors = (pal.front, pal.back)
    surfs, cam = goals[n - 1]
    gw, gh = w - 32, 190
    goal = iso.svg(surfs, *cam, gw, gh, pad=10, colors=colors, stroke=pal.edge)
    gap = min(28, (w - 40) / max(total - 1, 1))
    x0 = x + w / 2 - gap * (total - 1) / 2
    dots = ""
    for i in range(1, total + 1):
        cx = x0 + gap * (i - 1)
        if i == n:
            dots += (
                f'<circle cx="{cx:.1f}" cy="{y + h - 40}" r="9" fill="{pal.accent}"/>'
            )
        else:
            col = pal.ink if i < n else pal.faint
            dots += f'<circle cx="{cx:.1f}" cy="{y + h - 40}" r="6" fill="{col}"/>'
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{pal.card}"/>'
        f'<text x="{x + w / 2}" y="{y + 92}" text-anchor="middle" {FONT} '
        f'font-size="76" fill="{pal.accent}">{n}<tspan font-size="30" '
        f'fill="{pal.ink}" dx="4">/ {total}</tspan></text>'
        f'<g transform="translate({x + 16},{y + 140})">{_inner(goal)}</g>'
        f"{dots}"
    )


DASH = {"valley": "10 7", "mountain": "14 5 3 5"}


def _frame(shot: Shot, bounds, card: str, pal: Palette) -> str:
    lines = [
        (a, b, f'stroke="{pal.accent}" stroke-width="3.5" stroke-linecap="round" '
         f'stroke-dasharray="{DASH[k]}"')
        for a, b, k in shot.lines
    ]  # fmt: skip
    stage = iso.svg(
        shot.surfs,
        *shot.cam,
        STAGE,
        H,
        pad=24,
        bounds=bounds,
        colors=(pal.front, pal.back),
        stroke=pal.edge,
        lines=lines,
        by_planes=shot.view == "table",
    )
    return (
        f'<svg viewBox="0 0 {W} {H}" width="{W * SCALE}" height="{H * SCALE}" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%">'
        f'<feDropShadow dx="0" dy="8" stdDeviation="9" flood-color="#000" '
        f'flood-opacity="0.18"/></filter></defs>'
        f'<rect width="{W}" height="{H}" fill="{pal.bg}"/>'
        f'<g filter="url(#sh)">{_inner(stage)}</g>{card}</svg>'
    )


def _png(svg: str, png: Path) -> None:
    subprocess.run(  # noqa: S603
        ["rsvg-convert", "-o", str(png)],  # noqa: S607
        input=svg.encode(),
        check=True,
    )


def render(
    slug: str, dest: Path, pal: Palette = PALETTES["night"], t: Timing | None = None
) -> Path:
    t = t or Timing()
    seq, goals = shots(slug, t)
    # one fixed frame per view, so the paper never jumps inside it
    bounds = {
        view: _grow(
            _union(
                [
                    iso.extent(s.surfs, *s.cam)
                    for s in seq
                    if s.view == view and s.frames_view
                ]
            )
        )
        for view in {s.view for s in seq}
    }
    card = cache(lambda n: _card(n, goals, pal))
    work = dest.parent / f".{dest.stem}-frames"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    pngs = [work / f"{i:05d}.png" for i in range(len(seq))]
    svgs = [_frame(s, bounds[s.view], card(s.step), pal) for s in seq]
    with ThreadPoolExecutor() as pool:
        list(pool.map(_png, svgs, pngs))
    concat = []
    for shot, png in zip(seq, pngs, strict=True):
        concat += [f"file '{png.name}'", f"duration {shot.frames / FPS:.4f}"]
    concat.append(f"file '{pngs[-1].name}'")  # else ffmpeg drops the last duration
    (work / "list.txt").write_text("\n".join(concat) + "\n")
    subprocess.run(  # noqa: S603
        [  # noqa: S607
            "ffmpeg", "-y", "-loglevel", "error",
            "-f", "concat", "-i", "list.txt",
            "-vf", f"fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-crf", "18",
            str(dest.resolve()),
        ],
        cwd=work,
        check=True,
    )  # fmt: skip
    return dest


if __name__ == "__main__":
    defaults = ["arrow", "night"]  # plane, palette
    slug, name = (sys.argv[1:] + defaults[len(sys.argv) - 1 :])[:2]
    out = Path("_video")
    out.mkdir(exist_ok=True)
    dest = render(slug, out / f"{slug}-{name}.mp4", PALETTES[name])
    sys.stdout.write(f"{dest}\n")
