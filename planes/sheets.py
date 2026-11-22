"""Print styling and the shared pieces of a plane's sheets: legend, line sheet, tube art."""

from shapely.geometry import LineString, Polygon

from .fold import ap, inv

BLUE, RED, GREEN = "#1971c2", "#e03131", "#2f9e44"

CSS = """
@page { size: A4; margin: 0 }
* { box-sizing: border-box }
body { margin: 0; font-family: Inter, 'DejaVu Sans', sans-serif; color: #212529 }
.page { width: 210mm; height: 297mm; position: relative; overflow: hidden;
  page-break-after: always }
.page:last-child { page-break-after: auto }
.inst { padding: 10mm 12mm 9mm }
h1 { font-weight: 900; font-size: 26pt; margin: 0; letter-spacing: -0.5px }
.sub { font-size: 11pt; color: #495057; margin: 1mm 0 4mm }
.badge { display: inline-block; background: #e9ecef; border-radius: 20px;
  padding: 1mm 3.5mm; font-size: 9pt; font-weight: 700; margin-right: 2mm }
.grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3mm }
.panel { border: 0.4mm solid #dee2e6; border-radius: 3mm; padding: 2mm 2.5mm;
  position: relative; background: #fff }
.panel svg { width: 100%; height: auto; display: block }
.panel .iso { border-top: 0.3mm dashed #e9ecef; margin-top: 1mm }
.panel.opt { border-style: dashed; border-color: #adb5bd }
.opt-tag { display: inline-block; background: #e9ecef; border-radius: 2mm;
  padding: 0 1.5mm; font-size: 7.5pt; font-weight: 700; margin-right: 1mm }
.num { display: inline-flex; align-items: center; justify-content: center; width: 7mm;
  height: 7mm; border-radius: 50%; background: #1971c2; color: #fff; font-weight: 900;
  font-size: 11pt; margin-right: 1.5mm; flex: none }
.num.ok { background: #f59f00 }
.txt { display: flex; align-items: flex-start; font-size: 9pt; line-height: 1.25;
  min-height: 10mm }
.done { background: #fff9db; border-color: #ffd43b }
.big { grid-column: span 2 }
.legend { display: flex; flex-wrap: wrap; gap: 6mm; font-size: 8.5pt; color: #495057;
  margin: 3mm 0 0; align-items: center }
.exp { margin: -2mm 0 3mm; background: #e7f5ff; border-radius: 2.5mm; padding: 2mm 3mm;
  font-size: 9.5pt; line-height: 1.4 }
.labgrid { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; margin-top: 4mm }
.labcard { border: 0.4mm solid #dee2e6; border-radius: 3mm; padding: 2mm 3mm; font-size: 10pt }
.labcard span { color: #495057; font-size: 9pt }
.labcard svg { width: 100%; height: auto }
table.score { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin-bottom: 3mm }
table.score th, table.score td { border: 0.3mm solid #868e96; padding: 2mm; height: 11mm;
  text-align: left }
table.score th { background: #f1f3f5; height: auto }
h3 { font-size: 12pt; margin: 4mm 0 2mm }
.lines-box { height: 45mm; background: repeating-linear-gradient(#fff 0 9mm, #ced4da 9mm 9.3mm) }
.tips ol { margin: 1mm 0 0; padding-left: 5mm }
.tips { margin-top: 3mm; background: #f1f3f5; border-radius: 3mm; padding: 2.5mm 4mm;
  font-size: 9pt; line-height: 1.35 }
.foot { position: absolute; bottom: 4mm; left: 12mm; right: 12mm; font-size: 7.5pt;
  color: #adb5bd; display: flex; justify-content: space-between }
.lines svg { position: absolute; inset: 0; width: 210mm; height: 297mm }
"""


def legend() -> str:
    """The key to the four line styles and the grey back of the sheet."""
    return f"""<div class="legend">
<span><svg width="36" height="8"><line x1="0" y1="4" x2="36" y2="4" stroke="{BLUE}" stroke-width="2" stroke-dasharray="6,3"/></svg> valley fold: towards you</span>
<span><svg width="36" height="8"><line x1="0" y1="4" x2="36" y2="4" stroke="{RED}" stroke-width="2" stroke-dasharray="6,2,1,2"/></svg> mountain fold: behind</span>
<span><svg width="36" height="8"><line x1="0" y1="4" x2="36" y2="4" stroke="#212529" stroke-width="2"/></svg> cut</span>
<span><svg width="36" height="8"><line x1="0" y1="4" x2="36" y2="4" stroke="{GREEN}" stroke-width="2" stroke-dasharray="1.5,2.5" stroke-linecap="round"/></svg> bend a little</span>
<span style="display:flex;align-items:center;gap:1mm"><span style="display:inline-block;width:5mm;height:3mm;background:#ced4da;border:1px solid #555"></span> back of the sheet</span>
</div>"""


def defs(w: float, h: float) -> str:
    """The grey fill the step diagrams use for the back of the sheet."""
    return (
        '<svg width="0" height="0" style="position:absolute"><defs>'
        f'<g id="back"><rect x="-10" y="-10" width="{w + 20}" height="{h + 20}" '
        'fill="#ced4da"/></g></defs></svg>'
    )


def visible_creases(model):
    """Crease segments that lie on the top, front-facing layer at the moment of folding."""
    out = []
    for s in model.steps:
        for ln in s["lines"]:
            covered = Polygon()
            far_line = LineString(
                [_ext(ln["p"], ln["q"], -1000), _ext(ln["p"], ln["q"], 1000)]
            )
            for f in sorted(ln["state"], key=lambda f: -f.z):
                cur = Polygon(f.cur()).buffer(0)
                vis = cur.difference(covered)
                covered = covered.union(cur.buffer(0.05))
                base = f.M == (1, 0, 0, 1, 0, 0)
                if f.flipped or (vis.is_empty and not base):
                    continue
                if base:
                    vis = cur
                if ln["filt"] and not ln["filt"](f):
                    continue
                seg = far_line.intersection(vis.buffer(0.01))
                mi = inv(f.M)
                for g in getattr(seg, "geoms", [seg]):
                    if g.geom_type != "LineString" or g.length < 3:
                        continue
                    a, b = next(iter(g.coords)), list(g.coords)[-1]
                    out.append((s["n"], ln["kind"], ap(mi, a), ap(mi, b)))
    return out


def _ext(p, q, t):
    return (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t)


def line_el(a, b, kind: str, sw: float = 0.55) -> str:
    """One SVG line in the style of a fold, cut or bend."""
    st = {
        "valley": f'stroke="{BLUE}" stroke-dasharray="4,2"',
        "mountain": f'stroke="{RED}" stroke-dasharray="4,1.5,0.8,1.5"',
        "cut": 'stroke="#212529"',
        "bend": f'stroke="{GREEN}" stroke-dasharray="0.6,1.6" stroke-linecap="round"',
    }[kind]
    w = sw * (1.5 if kind in ("cut", "bend") else 1)
    return (
        f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" '
        f'{st} stroke-width="{w:.2f}"/>'
    )


def _badge(x, y, label, col=BLUE):
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{col}"/>'
        f'<text x="{x:.1f}" y="{y + 1.5:.1f}" font-size="4.2" font-weight="900" '
        f'fill="#fff" text-anchor="middle" font-family="Inter">{label}</text>'
    )


def line_sheet_svg(title, w, h, creases, extra, note) -> str:
    """A4 line sheet as SVG; landscape models are rotated to fill the portrait page."""
    els, best = [], {}
    for n, k, a, b in creases:
        els.append(line_el(a, b, k))
        length = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
        if length > best.get(n, (0,))[0]:
            best[n] = (length, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), k)
    for _n, k, a, b, lab in extra:
        els.append(line_el(a, b, k))
        if lab:
            col = "#212529" if k == "cut" else GREEN
            els.append(_badge((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 5, lab, col))
    for n, (_, (x, y), k) in best.items():
        els.append(_badge(x, y, n, BLUE if k == "valley" else RED))
    body = "".join(els)
    if w > h:
        body = f'<g transform="translate(210,0) rotate(90)">{body}</g>'
        note = "Hold the page sideways, right-hand edge at the top. " + note
    foot = (
        '<text x="105" y="292" font-size="3.6" fill="#868e96" text-anchor="middle" '
        f'font-family="Inter">{title}: fold with this side up. {note}</text>'
    )
    return (
        '<svg viewBox="0 0 210 297" xmlns="http://www.w3.org/2000/svg">'
        f"{body}{foot}</svg>"
    )


TUBE_TUCK = """<svg viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg">
<text x="150" y="16" font-size="13" text-anchor="middle" font-family="Inter" fill="#495057">looking into the tube from the front</text>
<circle cx="150" cy="118" r="78" fill="#fff" stroke="#333" stroke-width="2.4"/>
<path d="M150,46 A72,72 0 1 1 112,57" fill="none" stroke="#868e96" stroke-width="9"/>
<path d="M188,57 A72,72 0 0 0 150,46" fill="none" stroke="#ced4da" stroke-width="5" stroke-dasharray="3,3"/>
<path d="M118,30 Q150,10 182,30" stroke="#d9480f" stroke-width="3" fill="none"/><polygon points="188,36 174,30 186,22" fill="#d9480f"/>
<text x="150" y="224" font-size="15" text-anchor="middle" font-family="Inter" fill="#495057">slide one end 3 cm into the other</text></svg>"""

TUBE_THROW = """<svg viewBox="0 0 300 240" xmlns="http://www.w3.org/2000/svg">
<g stroke="#333" stroke-width="2.4" fill="#fff">
<path d="M120,80 L220,80 C238,80 252,100 252,120 C252,140 238,160 220,160 L120,160"/>
<ellipse cx="120" cy="120" rx="22" ry="40"/><ellipse cx="120" cy="120" rx="15" ry="31" fill="#ced4da" stroke-width="1.6"/></g>
<path d="M60,120 L20,120" stroke="#d9480f" stroke-width="4"/><polygon points="12,120 28,110 28,130" fill="#d9480f"/>
<path d="M150,62 q30,-20 60,0" stroke="#2f9e44" stroke-width="3" fill="none"/><polygon points="212,62 199,57 205,70" fill="#2f9e44"/>
<text x="150" y="200" font-size="15" text-anchor="middle" font-family="Inter" fill="#495057">band first, push it off</text>
<text x="150" y="220" font-size="15" text-anchor="middle" font-family="Inter" fill="#495057">with a little spin</text></svg>"""
