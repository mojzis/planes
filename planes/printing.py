"""The two A4 PDFs of a plane: the steps, and the line sheet to fold."""

from pathlib import Path

from .catalogue import Panel, Plane
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
            head = f'<h1>{plane.title}</h1><div class="sub">{plane.sub}</div>{badges}'
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
    return _doc(plane, pages)


def sheet_document(plane: Plane) -> str:
    """HTML for the line-sheet PDF: one A4 page with the creases to fold on."""
    return _doc(plane, [f'<div class="page lines">{plane.line_sheet}</div>'])


ALL_LINES_PDF = "all-line-sheets.pdf"


def all_sheets_document(planes: list[Plane]) -> str:
    """HTML for one PDF with every plane's line sheet, one A4 page each."""
    pages = [f'<div class="page lines">{p.line_sheet}</div>' for p in planes]
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>All line sheets</title>"
        f"<style>{CSS}</style></head><body>{defs(planes[0].width, planes[0].height)}"
        f"{''.join(pages)}</body></html>"
    )


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


def write_build_files(planes: list[Plane], out: Path) -> list[Path]:
    """Print each plane's two PDFs into ``out/<slug>/``, one PDF with all line
    sheets into ``out/``, and every social preview."""
    from playwright.sync_api import sync_playwright  # noqa: PLC0415 -- heavy, build only

    written = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": CARD_W, "height": CARD_H})
        for plane in planes:
            folder = out / plane.slug
            folder.mkdir(parents=True, exist_ok=True)
            for name, doc in (
                (f"{plane.slug}-steps.pdf", steps_document(plane)),
                (f"{plane.slug}-lines.pdf", sheet_document(plane)),
            ):
                page.set_content(doc, wait_until="load")
                path = folder / name
                page.pdf(path=str(path), format="A4", print_background=True)
                written.append(path)
        page.set_content(all_sheets_document(planes), wait_until="load")
        path = out / ALL_LINES_PDF
        page.pdf(path=str(path), format="A4", print_background=True)
        written.append(path)
        cards = [
            (
                "",
                card_document(
                    "Fold, throw, fly", [p.finished or "" for p in planes[:3]]
                ),
            )
        ]
        cards += [(p.slug, card_document(p.name, [p.finished or ""])) for p in planes]
        for slug, doc in cards:
            page.set_content(doc, wait_until="load")
            path = out / card_path(slug)
            page.screenshot(path=str(path))
            written.append(path)
        browser.close()
    return written
