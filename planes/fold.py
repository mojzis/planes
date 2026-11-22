"""Tiny flat-fold simulator: a sheet split into convex facets, each with an affine map."""

import math

W, H = 210.0, 297.0


def ap(M, v):
    a, b, c, d, e, f = M
    return (a * v[0] + c * v[1] + e, b * v[0] + d * v[1] + f)


def comp(M1, M2):  # M1 after M2
    a1, b1, c1, d1, e1, f1 = M1
    a2, b2, c2, d2, e2, f2 = M2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def inv(M):
    a, b, c, d, e, f = M
    det = a * d - b * c
    ia, ib, ic, id_ = d / det, -b / det, -c / det, a / det
    return (ia, ib, ic, id_, -(ia * e + ic * f), -(ib * e + id_ * f))


def det(M):
    return M[0] * M[3] - M[1] * M[2]


def refl(p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(dx, dy)
    ux, uy = dx / n, dy / n
    a, b, c, d = 2 * ux * ux - 1, 2 * ux * uy, 2 * ux * uy, 2 * uy * uy - 1
    return (a, b, c, d, p[0] - (a * p[0] + c * p[1]), p[1] - (b * p[0] + d * p[1]))


def side(p, q, v):
    return (q[0] - p[0]) * (v[1] - p[1]) - (q[1] - p[1]) * (v[0] - p[0])


def split(poly, p, q, eps=1e-7):
    """Split convex poly by line pq -> (pos, neg, crease_points)."""
    pos, neg, cut = [], [], []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        sa, sb = side(p, q, a), side(p, q, b)
        if sa >= -eps:
            pos.append(a)
        if sa <= eps:
            neg.append(a)
        if abs(sa) <= eps:
            cut.append(a)
        if (sa > eps and sb < -eps) or (sa < -eps and sb > eps):
            t = sa / (sa - sb)
            x = (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
            pos.append(x)
            neg.append(x)
            cut.append(x)
    return pos, neg, cut


def area(poly):
    s = 0
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        s += a[0] * b[1] - a[1] * b[0]
    return abs(s) / 2


class Facet:
    def __init__(self, poly, M=(1, 0, 0, 1, 0, 0), z=0.0, tags=()):
        self.poly, self.M, self.z, self.tags = poly, M, z, set(tags)

    @property
    def flipped(self):
        return det(self.M) < 0

    def cur(self):
        return [ap(self.M, v) for v in self.poly]


class Model:
    def __init__(self, w=W, h=H):
        self.w, self.h = w, h
        self.facets = [Facet([(0, 0), (w, 0), (w, h), (0, h)])]
        self.creases = []  # (step_no, kind_on_front, a, b)
        self.steps = []  # snapshots: dict
        self.n = 0

    def snapshot(self):
        return [Facet(list(f.poly), f.M, f.z, f.tags) for f in self.facets]

    def step(self, text, folds, kind="valley", unfold=False, art=None):
        """One numbered step: folds = list of (p, q, mv[, filt]) done in order."""
        self.n += 1
        before = self.snapshot()
        lines = []
        for fd in folds:
            p, q, mv = fd[:3]
            filt = fd[3] if len(fd) > 3 else None
            k = (fd[4] if len(fd) > 4 else None) or kind
            tag = fd[5] if len(fd) > 5 else None
            mid_before = self.snapshot()
            self._fold(p, q, mv, k, filt, unfold, tag=tag)
            lines.append(dict(p=p, q=q, mv=mv, kind=k, filt=filt, state=mid_before))
        self.steps.append(
            dict(
                n=self.n,
                before=before,
                lines=lines,
                unfold=unfold,
                text=text,
                after=self.snapshot(),
                art=art,
            )
        )

    def _fold(
        self, p, q, mv, kind="valley", filt=None, unfold=False, crease=True, tag=None
    ):
        smv = side(p, q, mv)
        R = refl(p, q)
        zs = [f.z for f in self.facets]
        zmax, zmin = max(zs), min(zs)
        new = []
        for f in self.facets:
            if filt and not filt(f):
                new.append(f)
                continue
            cur = f.cur()
            pos, neg, cut = split(cur, p, q)
            mvp, stay = (pos, neg) if smv > 0 else (neg, pos)
            Mi = inv(f.M)
            if len(cut) >= 2 and area(mvp) > 1e-6 and area(stay) > 1e-6 and crease:
                fk = (
                    kind
                    if not f.flipped
                    else ("mountain" if kind == "valley" else "valley")
                )
                self.creases.append((self.n, fk, ap(Mi, cut[0]), ap(Mi, cut[-1])))
            if area(mvp) <= 1e-6:
                new.append(f)
                continue
            if area(stay) > 1e-6:
                new.append(Facet([ap(Mi, v) for v in stay], f.M, f.z, f.tags))
            if unfold:
                new.append(Facet([ap(Mi, v) for v in mvp], f.M, f.z, f.tags))
                continue
            z = (2 * zmax + 1 - f.z) if kind == "valley" else (2 * zmin - 1 - f.z)
            t = set(f.tags) | ({tag} if tag else set())
            new.append(Facet([ap(Mi, v) for v in mvp], comp(R, f.M), z, t))
        self.facets = new

    def note(self, text, art=None):
        """A step with no fold (e.g. 'open the wings')."""
        self.n += 1
        s = self.snapshot()
        self.steps.append(
            dict(
                n=self.n, before=s, lines=[], unfold=False, text=text, after=s, art=art
            )
        )
