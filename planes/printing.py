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


def write_pdfs(planes: list[Plane], out: Path) -> list[Path]:
    """Print each plane's two PDFs into ``out/<slug>/`` with headless Chromium."""
    from playwright.sync_api import sync_playwright  # noqa: PLC0415 -- heavy, build only

    written = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page()
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
        browser.close()
    return written
