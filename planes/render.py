import math

from .fold import Facet, ap, area, comp, inv, refl, side, split

_cid = [0]


def _id():
    _cid[0] += 1
    return f"c{_cid[0]}"


def pts(poly):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in poly)


def mat(M):
    return "matrix(" + ",".join(f"{v:.5f}" for v in M) + ")"


BACK = "#ffffff"
PRINTED_UP = False  # the picture side starts face down
EDGE = "#333"


def bbox(facets):
    xs, ys = [], []
    for f in facets:
        for x, y in f.cur():
            xs.append(x)
            ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def draw_facets(facets, deco, view="front", clip=None, sw=0.6):
    """SVG for facets in current coords. view='back' mirrors x and reverses layers."""
    out = []
    order = sorted(facets, key=lambda f: f.z, reverse=(view == "back"))
    for f in order:
        cur = f.cur()
        if clip:
            p, q, keep = clip
            pos, neg, _ = split(cur, p, q)
            cur = pos if side(p, q, keep) > 0 else neg
            if area(cur) < 1e-6:
                continue
            Mi = inv(f.M)
            spoly = [ap(Mi, v) for v in cur]
        else:
            spoly = f.poly
        up_visible = (not f.flipped) if view == "front" else f.flipped
        if up_visible != PRINTED_UP:
            out.append(f'<polygon points="{pts(cur)}" fill="{BACK}"/>')
        else:
            cid = _id()
            out.append(
                f'<clipPath id="{cid}"><polygon points="{pts(spoly)}"/></clipPath>'
                f'<g transform="{mat(f.M)}"><g clip-path="url(#{cid})">'
                f'<use href="#{deco}"/></g></g>'
            )
        out.append(
            f'<polygon points="{pts(cur)}" fill="none" stroke="{EDGE}" '
            f'stroke-width="{sw}" stroke-linejoin="round"/>'
        )
    return "\n".join(out)


def arrow(p, q, mv, kind, scale):
    """Curved arrow from the moving side across the fold line."""
    R = refl(p, q)
    a = mv
    b = ap(R, mv)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L, dx / L
    # bulge to one side
    c = (mx + nx * L * 0.35, my + ny * L * 0.35)
    # shorten end a little
    sw = 1.1 / scale * 2.2
    col = "#d9480f"
    dash = (
        ""
        if kind == "valley"
        else f'stroke-dasharray="{3 / scale * 2:.2f},{2 / scale * 2:.2f}"'
    )
    # arrow head at b, direction from c to b
    hx, hy = b[0] - c[0], b[1] - c[1]
    hl = math.hypot(hx, hy) or 1
    hx, hy = hx / hl, hy / hl
    s = 7 / scale * 1.6
    h1 = (b[0] - hx * s - hy * s * 0.6, b[1] - hy * s + hx * s * 0.6)
    h2 = (b[0] - hx * s + hy * s * 0.6, b[1] - hy * s - hx * s * 0.6)
    head_fill = col if kind == "valley" else "#fff"
    return (
        f'<path d="M{a[0]:.2f},{a[1]:.2f} Q{c[0]:.2f},{c[1]:.2f} {b[0]:.2f},{b[1]:.2f}" '
        f'fill="none" stroke="{col}" stroke-width="{sw:.2f}" {dash}/>'
        f'<polygon points="{pts([b, h1, h2])}" fill="{head_fill}" stroke="{col}" '
        f'stroke-width="{sw * 0.7:.2f}"/>'
    )


def fold_line(p, q, kind, scale, ext=2000):
    col = "#1971c2" if kind == "valley" else "#e03131"
    sw = 1.0 / scale * 2.2
    dash = (
        f"{6 / scale * 2:.2f},{3 / scale * 2:.2f}"
        if kind == "valley"
        else f"{6 / scale * 2:.2f},{2 / scale * 2:.2f},{1 / scale * 2:.2f},{2 / scale * 2:.2f}"
    )
    return (
        f'<line x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" '
        f'stroke="{col}" stroke-width="{sw:.2f}" stroke-dasharray="{dash}"/>'
    )


def clip_line(p, q, box):
    """Clip infinite line pq to bbox (x0,y0,x1,y1) padded."""
    x0, y0, x1, y1 = box
    dx, dy = q[0] - p[0], q[1] - p[1]
    cand = []
    if abs(dx) > 1e-9:
        for x in (x0, x1):
            t = (x - p[0]) / dx
            y = p[1] + t * dy
            if y0 - 1e-6 <= y <= y1 + 1e-6:
                cand.append((t, (x, y)))
    if abs(dy) > 1e-9:
        for y in (y0, y1):
            t = (y - p[1]) / dy
            x = p[0] + t * dx
            if x0 - 1e-6 <= x <= x1 + 1e-6:
                cand.append((t, (x, y)))
    cand.sort()
    return cand[0][1], cand[-1][1]


def state_svg(facets, deco, width_px, height_px, lines=(), pad=12, view="front"):
    x0, y0, x1, y1 = bbox(facets)
    w, h = x1 - x0, y1 - y0
    scale = min((width_px - 2 * pad) / w, (height_px - 2 * pad) / h)
    ox = (width_px - w * scale) / 2 - x0 * scale
    oy = (height_px - h * scale) / 2 - y0 * scale
    body = [draw_facets(facets, deco)]
    m = 8
    for ln in lines:
        a, b = clip_line(ln["p"], ln["q"], (x0 - m, y0 - m, x1 + m, y1 + m))
        body.append(fold_line(a, b, ln["kind"], scale))
    for ln in lines:
        body.append(arrow(ln["p"], ln["q"], ln["mv"], ln["kind"], scale))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" '
        f'viewBox="0 0 {width_px} {height_px}"><g transform="translate({ox:.2f},{oy:.2f}) '
        f'scale({scale:.4f})">' + "\n".join(body) + "</g></svg>"
    )


def mirror_x(facets, x):
    """Facets as seen from behind, mirrored about vertical line at x."""
    R = (-1, 0, 0, 1, 2 * x, 0)
    return [Facet(f.poly, comp(R, f.M), -f.z, f.tags) for f in facets]


def wing_views(state, hinge, near, far, width_px, height_px, pad=10, overlay=""):
    """Top and underside views of the opened plane. state: body folded in half,
    keel at the left, wings to the right of vertical line x=hinge."""
    keep_r = ((hinge, -1e4), (hinge, 1e4), (hinge + 1, 0))
    keep_l = ((hinge, -1e4), (hinge, 1e4), (hinge - 1, 0))
    nf = [f for f in state if near(f)]
    ff = [f for f in state if far(f)]
    out = {}
    # top: inner faces. near wing seen from behind (mirrored, goes left); far from front.
    top = draw_facets(mirror_x(nf, hinge), DECO_ID, clip=keep_l) + draw_facets(
        ff, DECO_ID, clip=keep_r
    )
    bot = draw_facets(nf, DECO_ID, clip=keep_r) + draw_facets(
        mirror_x(ff, hinge), DECO_ID, clip=keep_l
    )
    allf = mirror_x(state, hinge) + state
    x0, y0, x1, y1 = bbox(allf)
    x0 = max(x0, 2 * hinge - x1)
    x1 = 2 * hinge - x0
    w, h = x1 - x0, y1 - y0
    scale = min((width_px - 2 * pad) / w, (height_px - 2 * pad) / h)
    ox = (width_px - w * scale) / 2 - x0 * scale
    oy = (height_px - h * scale) / 2 - y0 * scale
    top += overlay
    for k, body in (("top", top), ("bottom", bot)):
        out[k] = (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width_px}" height="{height_px}" '
            f'viewBox="0 0 {width_px} {height_px}"><g transform="translate({ox:.2f},{oy:.2f}) '
            f'scale({scale:.4f})">' + body + "</g></svg>"
        )
    return out


DECO_ID: str = "deco-sheet"
