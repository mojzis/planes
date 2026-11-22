"""The two A4 PDFs of a plane: the steps, and the line sheet to fold."""

from pathlib import Path

from .catalogue import Panel, Plane, Series, series_planes
from .sheets import CSS, defs, legend

PER_PAGE = 6


def panel_html(p: Panel) -> str:
    """One step panel, the same markup on the web page and in the PDF."""
    num = f'<span class="num">{p.n}</span>' if p.n else '<span class="num ok">✓</span>'
    tag = '<span class="opt-tag">optional</span>' if p.optional else ""
    pics = (p.flat or "") + (f'<div class="iso">{p.view3d}</div>' if p.view3d else "")
    cls = "panel" + (" opt" if p.optional else "") + ("" if p.n else " done")
    return f'<div class="{cls}"><div class="txt">{num}<span>{tag}{p.text}</span></div>{pics}</div>'  # noqa: E501


def _doc(plane: Plane, pages: list[str]) -> str:
    return (
        f'<!doctype html><html><head><meta charset="utf-8"><title>{plane.name}</title>'
        f"<style>{CSS}</style></head><body>{defs(plane.width, plane.height)}"
        f"{''.join(pages)}</body></html>"
    )


def steps_document(plane: Plane) -> str:
    """HTML for the steps PDF: numbered panels, six to a page, tips at the end."""
    return _doc(plane, steps_pages(plane))


def steps_pages(plane: Plane) -> list[str]:
    """The pages of the steps PDF."""
    panels = [panel_html(p) for p in plane.panels]
    if plane.finished:
        panels.append(
            '<div class="panel done big"><div class="txt"><span class="num ok">✓</span>'
            f"<span><b>Ready for take-off!</b></span></div>{plane.finished}</div>"
        )
    chunks = [panels[i : i + PER_PAGE] for i in range(0, len(panels), PER_PAGE)]
    pages = []
    for i, chunk in enumerate(chunks):
        if i == 0:
            badges = "".join(f'<span class="badge">{b}</span>' for b in plane.badges)
            head = f'<h1>{plane.title}</h1><div class="sub">{plane.sub}</div>'
            if plane.box:
                head += f'<div class="exp">{plane.box}</div>'
            head += badges
            head += '<div style="height:3mm"></div>'
        else:
            head = f'<div class="sub"><b>{plane.title}</b>, continued</div>'
        last = i == len(chunks) - 1
        tail = legend() + (f'<div class="tips">{plane.tips}</div>' if last else "")
        foot = (
            '<div class="foot"><span>No printer? These steps work with any plain A4 '
            "sheet. The line sheet is a separate PDF.</span>"
            f"<span>{i + 1} / {len(chunks)}</span></div>"
        )
        pages.append(
            f'<div class="page inst">{head}<div class="grid">{"".join(chunk)}</div>'
            f"{tail}{foot}</div>"
        )
    return pages


def sheet_document(plane: Plane) -> str:
    """HTML for the line-sheet PDF: one A4 page with the creases to fold on."""
    return _doc(plane, [f'<div class="page lines">{plane.line_sheet}</div>'])


ALL_LINES_PDF = "all-line-sheets.pdf"
COUNT = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}


def _plain_doc(title: str, planes: list[Plane], pages: list[str]) -> str:
    return (
        f'<!doctype html><html><head><meta charset="utf-8"><title>{title}</title>'
        f"<style>{CSS}</style></head><body>{defs(planes[0].width, planes[0].height)}"
        f"{''.join(pages)}</body></html>"
    )


def score_card_page(s: Series) -> str:
    """A series score card: its planes, then experiments on one plane."""
    head = (
        "<tr><th>{}</th><th>My guess</th><th>Throw 1</th><th>Throw 2</th>"
        "<th>Throw 3</th><th>Straight?</th></tr>"
    )
    cells = "<td></td>" * 5
    rows1 = "".join(
        f"<tr><td><b>{p.letter}</b> {p.title.title()}</td>{cells}</tr>"
        for p in s.planes
    )
    rows2 = "".join(
        f"<tr><td>{e}<br><small>on plane ____</small></td>{cells}</tr>"
        for e in s.experiments
    )
    count = COUNT.get(len(s.planes), str(len(s.planes)))
    return (
        f'<div class="page inst"><h1 style="font-size:22pt">{s.title}: SCORE CARD</h1>'
        '<div class="sub">Count steps from where you throw to where the plane lands. '
        'Write ✓ under "Straight?" if it flew straight.</div>'
        f'<h3>1. The {count} planes</h3><table class="score">{head.format("Plane")}'
        f"{rows1}</table>"
        "<h3>2. Experiments: change one thing, then throw again</h3>"
        f'<table class="score">{head.format("Experiment")}{rows2}</table>'
        '<h3>3. What did you find out?</h3><div class="lines-box"></div>'
        '<div class="foot"><span>Tip: a fair test changes only one thing at a time.'
        "</span></div></div>"
    )


def series_intro_page(s: Series) -> str:
    """The first page of a series PDF."""
    cards = "".join(
        f'<div class="labcard">{p.finished}<b>{p.name}</b><br>'
        f"<span>{p.sub}</span></div>"
        for p in series_planes(s)
    )
    return (
        f'<div class="page inst"><h1>{s.title}</h1><div class="sub">{s.intro}</div>'
        f'<div class="labgrid">{cards}</div><div class="tips">{s.howto}</div>'
        f'<div class="tips" style="background:#fff9db">{s.found}</div>'
        '<div class="foot"><span>No printer? Every plane has step pages that work with '
        "any plain A4 sheet.</span></div></div>"
    )


def series_document(s: Series) -> str:
    """A whole series in one PDF: intro, each plane's steps and line sheet, and the
    score card."""
    planes = series_planes(s)
    pages = [series_intro_page(s)]
    for p in planes:
        pages += steps_pages(p)
        pages.append(f'<div class="page lines">{p.line_sheet}</div>')
    pages.append(score_card_page(s))
    return _plain_doc(s.name, planes, pages)


def score_card_document(s: Series) -> str:
    """The score card on its own."""
    return _plain_doc(f"{s.name} score card", series_planes(s), [score_card_page(s)])


def all_sheets_document(planes: list[Plane]) -> str:
    """HTML for one PDF with every plane's line sheet, one A4 page each."""
    pages = [f'<div class="page lines">{p.line_sheet}</div>' for p in planes]
    return _plain_doc("All line sheets", planes, pages)


CARD_W, CARD_H = 1200, 630

CARD_CSS = f"""
* {{ box-sizing: border-box }}
body {{ margin: 0; width: {CARD_W}px; height: {CARD_H}px; overflow: hidden;
  font-family: Inter, 'DejaVu Sans', sans-serif; color: #212529;
  background: linear-gradient(160deg, #e7f5ff, #fff 60%) }}
.card {{ display: flex; flex-direction: column; height: 100%; padding: 48px 64px }}
.brand {{ color: #1971c2; font-weight: 800; font-size: 30px }}
h1 {{ font-size: 76px; font-weight: 900; letter-spacing: -2px; margin: 6px 0 0 }}
.pics {{ flex: 1; display: flex; align-items: center; justify-content: center;
  gap: 24px; min-height: 0 }}
.pics svg {{ height: 100%; max-width: 100%; flex: 1 }}
"""


def card_document(title: str, pictures: list[str]) -> str:
    """A 1200x630 social preview: the site name, a title and 3D pictures."""
    return (
        f'<!doctype html><html><head><meta charset="utf-8"><style>{CARD_CSS}</style>'
        f'</head><body><div class="card"><div class="brand">✈ Paper planes</div>'
        f'<h1>{title}</h1><div class="pics">{"".join(pictures)}</div></div>'
        "</body></html>"
    )


def card_path(slug: str) -> str:
    """Site-relative path of a page's social preview (``""`` is the home page)."""
    return f"{slug}/social.png" if slug else "social.png"


def write_build_files(
    planes: list[Plane], groups: list[Series], out: Path
) -> list[Path]:
    """Print each plane's two PDFs into ``out/<slug>/``, one PDF with all line
    sheets into ``out/``, each series' PDFs, and every social preview."""
    from playwright.sync_api import sync_playwright  # noqa: PLC0415 -- heavy, build only

    grouped = [p for s in groups for p in series_planes(s)]
    docs: list[tuple[str, str]] = []
    for plane in planes + grouped:
        docs.append((f"{plane.slug}/{plane.slug}-steps.pdf", steps_document(plane)))
        docs.append((f"{plane.slug}/{plane.slug}-lines.pdf", sheet_document(plane)))
    docs.append((ALL_LINES_PDF, all_sheets_document(planes + grouped)))
    for s in groups:
        docs.append((s.pdf, series_document(s)))
        docs.append((s.score_pdf, score_card_document(s)))
    cards = [
        ("", card_document("Fold, throw, fly", [p.finished or "" for p in planes[:3]]))
    ]
    cards += [
        (p.slug, card_document(p.name, [p.finished or ""])) for p in planes + grouped
    ]
    cards += [
        (
            s.slug,
            card_document(s.name, [p.finished or "" for p in series_planes(s)[:3]]),
        )
        for s in groups
    ]
    written = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": CARD_W, "height": CARD_H})
        for name, doc in docs:
            path = out / name
            path.parent.mkdir(parents=True, exist_ok=True)
            page.set_content(doc, wait_until="load")
            page.pdf(path=str(path), format="A4", print_background=True)
            written.append(path)
        for slug, doc in cards:
            path = out / card_path(slug)
            path.parent.mkdir(parents=True, exist_ok=True)
            page.set_content(doc, wait_until="load")
            page.screenshot(path=str(path))
            written.append(path)
        browser.close()
    return written
