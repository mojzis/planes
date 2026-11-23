"""Isometric 3D views from the flat-fold model.

Each rigid group of stacked layers is reduced to its two exposed surfaces (found by 2D
occlusion), mapped to 3D, back-face culled, then painted far to near."""

import math

from shapely.geometry import Polygon, box

from .fold import area, side, split

FRONT, BACK = (255, 255, 255), (206, 212, 218)


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(a):
    n = math.sqrt(dot(a, a)) or 1
    return (a[0] / n, a[1] / n, a[2] / n)


class Layer:
    def __init__(self, poly, flipped, z):
        self.poly, self.flipped, self.z = poly, flipped, z


def exposed(layers):
    """-> list of (shapely piece, Layer, seen_from_front)."""
    out = []
    for front in (True, False):
        covered = Polygon()
        for L in sorted(layers, key=lambda L: -L.z if front else L.z):
            g = Polygon(L.poly).buffer(0)
            vis = g.difference(covered)
            covered = covered.union(g.buffer(0.02))
            for p in getattr(vis, "geoms", [vis]):
                if p.geom_type == "Polygon" and p.area > 0.3:
                    out.append((p, L, front))
    return out


def signed_area(r):
    s = 0
    for i in range(len(r)):
        a, b = r[i], r[(i + 1) % len(r)]
        s += a[0] * b[1] - a[1] * b[0]
    return s / 2


class Surf:
    def __init__(self, rings3d, n_exposed, face_u):
        self.rings, self.n, self.u = rings3d, n_exposed, face_u


def newell(pts):
    n = (0.0, 0.0, 0.0)
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n = (
            n[0] + (a[1] - b[1]) * (a[2] + b[2]),
            n[1] + (a[2] - b[2]) * (a[0] + b[0]),
            n[2] + (a[0] - b[0]) * (a[1] + b[1]),
        )
    return norm(n)


def surf(piece, L, front, mapf, offset_normal=0.0):
    ext = list(piece.exterior.coords)[:-1]
    s0 = signed_area(ext)
    face_u = (front and not L.flipped) or (not front and L.flipped)
    rings = [[mapf(q) for q in ext]] + [
        [mapf(q) for q in list(r.coords)[:-1]] for r in piece.interiors
    ]
    N = newell(rings[0])
    # flat placement (x, -y, z): Newell normal z-sign = -sign(s0); the front side faces +z
    nf = tuple(
        c * (-1 if s0 > 0 else 1) for c in N
    )  # normal of the side seen from "front"
    n_exp = nf if front else tuple(-c for c in nf)
    if offset_normal:
        rings = [
            [
                (
                    p[0] + n_exp[0] * offset_normal,
                    p[1] + n_exp[1] * offset_normal,
                    p[2] + n_exp[2] * offset_normal,
                )
                for p in r
            ]
            for r in rings
        ]
    return Surf(rings, n_exp, face_u)


def camera(yaw, pitch):
    cy, sy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    cp, sp = math.cos(math.radians(pitch)), math.sin(math.radians(pitch))

    def proj(p):
        x, y, z = p
        x1, y1 = cy * x - sy * y, sy * x + cy * y
        y2, z2 = cp * y1 - sp * z, sp * y1 + cp * z
        return (x1, -z2, y2)

    v = (0, -1, 0)
    y1 = cp * v[1] + sp * v[2]
    z = -sp * v[1] + cp * v[2]
    x = cy * v[0] + sy * y1
    y = -sy * v[0] + cy * y1
    return proj, (x, y, z)


def _items(surfs, yaw, pitch, cull=True, colors=(FRONT, BACK), by_planes=False):
    """Visible surfaces, projected: (depth, rings, colour)."""
    proj, V = camera(yaw, pitch)
    Lt = norm((0.3, 0.5, 1.0))
    items = []
    for s in surfs:
        if cull and dot(s.n, V) <= 1e-6:
            continue
        rings = [[proj(q) for q in r] for r in s.rings]
        k = 0.8 + 0.2 * abs(dot(s.n, Lt))
        base = colors[0] if s.u else colors[1]
        col = "#{:02x}{:02x}{:02x}".format(*tuple(int(c * k) for c in base))
        depth = sum(q[2] for q in rings[0]) / len(rings[0])
        items.append((depth, rings, col))
    items.sort(key=lambda t: -t[0])
    return _paint_order(items) if by_planes else items


def _side(ring, other, eps=0.05):
    """Where `other` lies against the plane of `ring`, seen from the viewer:
    1 all in front, -1 all behind, 0 both or neither."""
    n, p0 = newell(ring), ring[0]
    toward = -1 if n[2] > 0 else 1  # the viewer looks along +depth
    ds = [toward * dot(n, sub(q, p0)) for q in other]
    if all(d >= -eps for d in ds):
        return 1
    if all(d <= eps for d in ds):
        return -1
    return 0


def _behind(a, b):
    """True if surface a must be painted before b (a is behind b)."""
    ra, rb = a[1][0], b[1][0]
    if (
        max(q[0] for q in ra) < min(q[0] for q in rb)
        or max(q[0] for q in rb) < min(q[0] for q in ra)
        or max(q[1] for q in ra) < min(q[1] for q in rb)
        or max(q[1] for q in rb) < min(q[1] for q in ra)
    ):
        return None  # apart on screen: any order
    for s, flip in ((_side(ra, rb), False), (_side(rb, ra), True)):
        if s:
            return (s > 0) != flip
    return None


def _paint_order(items):
    """Far to near. Centre depth alone fails for a big sheet and a small flap
    standing over it, so overlapping surfaces are ordered by their planes. For
    folding sheets; the finished plane's surfaces touch along edges and keep the
    depth order."""
    n = len(items)
    after = [set() for _ in range(n)]  # after[i]: drawn after i
    for i in range(n):
        for j in range(i + 1, n):
            b = _behind(items[i], items[j])
            if b is True:
                after[i].add(j)
            elif b is False:
                after[j].add(i)
    need = [0] * n
    for i in range(n):
        for j in after[i]:
            need[j] += 1
    out, done = [], [False] * n
    while len(out) < n:  # depth order among the free ones; a cycle falls back to depth
        k = next((i for i in range(n) if not done[i] and need[i] == 0), None)
        if k is None:
            k = next(i for i in range(n) if not done[i])
        done[k] = True
        out.append(items[k])
        for j in after[k]:
            need[j] -= 1
    return out


def extent(surfs, yaw, pitch, cull=True):
    """Bounding box (x0, x1, y0, y1) of the view, to fix the frame across views."""
    items = _items(surfs, yaw, pitch, cull)
    xs = [q[0] for _, rs, _ in items for q in rs[0]]
    ys = [q[1] for _, rs, _ in items for q in rs[0]]
    return min(xs), max(xs), min(ys), max(ys)


def svg(
    surfs,
    yaw,
    pitch,
    w,
    h,
    pad=8,
    outline=True,
    cull=True,
    bounds=None,
    colors=(FRONT, BACK),
    stroke="#343a40",
    lines=(),
    by_planes=False,
):
    """The surfaces painted far to near, scaled to fit, or to fit `bounds`.
    `colors`: RGB of the front and back of the paper; `lines`: 3D segments
    (a, b, svg attributes) drawn on top; `by_planes`: see `_paint_order`."""
    items = _items(surfs, yaw, pitch, cull, colors, by_planes)
    if not items:
        return ""
    x0, x1, y0, y1 = bounds or extent(surfs, yaw, pitch, cull)
    sc = min((w - 2 * pad) / (x1 - x0 or 1), (h - 2 * pad) / (y1 - y0 or 1))
    ox = (w - (x1 - x0) * sc) / 2 - x0 * sc
    oy = (h - (y1 - y0) * sc) / 2 - y0 * sc
    out = []
    for _depth, rings, col in items:
        d = " ".join(
            "M"
            + " L".join(f"{q[0] * sc + ox:.1f},{q[1] * sc + oy:.1f}" for q in r)
            + " Z"
            for r in rings
        )
        st = (
            f'stroke="{stroke}" stroke-width="1"'
            if outline
            else f'stroke="{col}" stroke-width="0.6"'
        )
        out.append(
            f'<path d="{d}" fill="{col}" fill-rule="evenodd" {st} stroke-linejoin="round"/>'
        )
    proj = camera(yaw, pitch)[0]
    for a, b, attrs in lines:
        (ax, ay, _), (bx, by, _) = proj(a), proj(b)
        out.append(
            f'<line x1="{ax * sc + ox:.1f}" y1="{ay * sc + oy:.1f}" '
            f'x2="{bx * sc + ox:.1f}" y2="{by * sc + oy:.1f}" {attrs}/>'
        )
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">{"".join(out)}</svg>'


def clip_x(piece, x0, x1):
    g = piece.intersection(box(x0, -1e4, x1, 1e4))
    return [
        p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and p.area > 0.3
    ]


# ------------------------------------------------------------ step views
def rot_axis(p, a, u, ang):
    v = sub(p, a)
    c, s = math.cos(ang), math.sin(ang)
    cr = cross(u, v)
    d = dot(u, v)
    r = (
        v[0] * c + cr[0] * s + u[0] * d * (1 - c),
        v[1] * c + cr[1] * s + u[1] * d * (1 - c),
        v[2] * c + cr[2] * s + u[2] * d * (1 - c),
    )
    return (r[0] + a[0], r[1] + a[1], r[2] + a[2])


def step_view(step, angle=70):
    st = step["before"]
    stay, groups = [], []
    movers = {}
    for gi, ln in enumerate(step["lines"]):
        p, q, mv = ln["p"], ln["q"], ln["mv"]
        smv = side(p, q, mv)
        for f in st:
            if ln["filt"] and not ln["filt"](f):
                continue
            pos, neg, _ = split(f.cur(), p, q)
            m, s = (pos, neg) if smv > 0 else (neg, pos)
            if area(m) > 1e-6 and id(f) not in movers:
                movers[id(f)] = (gi, m, s)
    groups = [[] for _ in step["lines"]]
    for f in st:
        if id(f) in movers:
            gi, m, s = movers[id(f)]
            groups[gi].append(Layer(m, f.flipped, f.z))
            if area(s) > 1e-6:
                stay.append(Layer(s, f.flipped, f.z))
        else:
            stay.append(Layer(f.cur(), f.flipped, f.z))
    flat = lambda q: (q[0], -q[1], 0.0)
    surfs = [surf(p, L, fr, flat, 0.3) for p, L, fr in exposed(stay)]
    ang0 = math.radians(angle * (0.55 if step["unfold"] else 1))
    for gi, ln in enumerate(step["lines"]):
        p, q = ln["p"], ln["q"]
        a = (p[0], -p[1], 0.6)
        u = norm((q[0] - p[0], -(q[1] - p[1]), 0))
        t = rot_axis((ln["mv"][0], -ln["mv"][1], 0.6), a, u, ang0)
        ang = ang0 if (t[2] > 0.6) == (ln["kind"] == "valley") else -ang0
        lift = 0.6 if ln["kind"] == "valley" else -0.6

        def mp(qq, a=a, u=u, ang=ang, lift=lift):
            return rot_axis((qq[0], -qq[1], lift), a, u, ang)

        surfs += [surf(pc, L, fr, mp, 0.3) for pc, L, fr in exposed(groups[gi])]
    return surfs


# ------------------------------------------------------------ finished plane
def plane3d(
    state, C, hinge, near, far, dihedral=6, winglet=None, winglet_angle=80, tab=None
):
    g = 0.8
    zh = hinge - C
    cd, sd = math.cos(math.radians(dihedral)), math.sin(math.radians(dihedral))
    cw, swl = (
        math.cos(math.radians(winglet_angle)),
        math.sin(math.radians(winglet_angle)),
    )
    surfs = []
    if tab:
        tl = [Layer(f.cur(), f.flipped, f.z) for f in state if tab(f)]
        surfs += [
            surf(p, L, fr, lambda q: (0.0, -q[1], q[0] - C), 0.2)
            for p, L, fr in exposed(tl)
        ]
    for half, sgn in ((near, -1), (far, 1)):
        layers = [
            Layer(f.cur(), f.flipped, f.z)
            for f in state
            if half(f) and not (tab and tab(f))
        ]
        for piece, L, fr in exposed(layers):
            regions = [(-1e4, hinge, "keel")]
            if winglet:
                regions += [
                    (hinge, hinge + winglet, "wing"),
                    (hinge + winglet, 1e4, "tip"),
                ]
            else:
                regions += [(hinge, 1e4, "wing")]
            for x0, x1, kind in regions:
                for pc in clip_x(piece, x0, x1):
                    if kind == "keel":
                        mp = lambda q, s=sgn: (s * g, -q[1], q[0] - C)
                    elif kind == "wing":
                        mp = lambda q, s=sgn: (
                            s * (g + (q[0] - hinge) * cd),
                            -q[1],
                            zh + (q[0] - hinge) * sd,
                        )
                    else:
                        mp = lambda q, s=sgn, wl=winglet or 0.0: (
                            s * (g + wl * cd + (q[0] - hinge - wl) * cw),
                            -q[1],
                            zh + wl * sd + (q[0] - hinge - wl) * swl,
                        )
                    surfs.append(surf(pc, L, fr, mp, 0.25))
    return surfs


def tube3d(state, W, overlap=30, strip=6, frac=1.0):
    R = (W - overlap) / (2 * math.pi * frac)
    layers = [Layer(f.cur(), f.flipped, f.z) for f in state]
    surfs = []
    for piece, L, fr in exposed(layers):
        x = 0
        while x < W:
            for pc in clip_x(piece, x, x + strip):
                rr = R - (0.8 if fr else 0)
                mp = lambda q, rr=rr: (
                    rr * math.sin((q[0] - W / 2) / R),
                    -q[1],
                    -rr * math.cos((q[0] - W / 2) / R),
                )
                surfs.append(surf(pc, L, fr, mp))
            x += strip
    return surfs
