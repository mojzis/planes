import math

from .fold import Model

T225 = math.tan(math.radians(22.5))


def halves(C):
    near = lambda f: sum(v[0] for v in f.poly) / len(f.poly) > C
    far = lambda f: sum(v[0] for v in f.poly) / len(f.poly) < C
    return near, far


def arrow():
    W, H = 210.0, 297.0
    C = W / 2
    m = Model(W, H)
    near, far = halves(C)
    m.step(
        "Fold the sheet in half the long way, edge to edge. Crease well and open it again.",
        [((C, -5), (C, H + 5), (20, 150))],
        unfold=True,
    )
    m.step(
        "Fold both top corners down so their edges lie on the middle crease.",
        [((C, 0), (0, C), (5, 5)), ((C, 0), (W, C), (W - 5, 5))],
    )
    m.step(
        "Fold the whole top triangle down. The fold goes where the corners ended.",
        [((-5, C), (W + 5, C), (C, 20))],
    )
    m.step(
        "Fold the two new top corners to the middle again. They meet over the point.",
        [((C, C), (0, 2 * C), (3, C + 3)), ((C, C), (W, 2 * C), (W - 3, C + 3))],
    )
    xb = C - (H - C) * T225
    m.step(
        "Fold the slanted edges to the middle line once more. Now the nose is thick and heavy: that's the trick for distance.",
        [((C, C), (xb, H), (4, 230)), ((C, C), (W - xb, H), (W - 4, 230))],
    )
    m.step(
        "Fold in half along the middle, all the folds outside (fold the left half behind).",
        [((C, -5), (C, H + 5), (60, 280), None, "mountain")],
    )
    k = 16
    m.step(
        "Optional beak: fold the back bottom corner up (2.5 cm along the bottom edge), crease hard and unfold. Open the halves a little and push the corner up inside between them along the creases. It sticks up as a little fin.",
        [((C, H - 25), (C + 14, H), (C + 1, H - 1), None, "valley", "beak")],
    )
    for f in m.facets:
        if "beak" in f.tags:
            f.z = -1000 + f.z * 0.001  # tucked between the halves
    m.steps[-1]["after"] = m.snapshot()
    nb = lambda f: near(f) and "beak" not in f.tags
    fb = lambda f: far(f) and "beak" not in f.tags
    m.step(
        "Fold the wings down 1.5 cm from the middle fold, one to the front and one behind. Keep the fold parallel to the middle fold.",
        [
            ((C + k, -5), (C + k, H + 5), (200, 285), nb, "valley"),
            ((C + k, -5), (C + k, H + 5), (200, 285), fb, "mountain"),
        ],
    )
    return dict(
        m=m, hinge=C + k, near=nb, far=fb, w=W, h=H, tab=lambda f: "beak" in f.tags
    )


def albatross():
    W, H = 297.0, 210.0
    C = W / 2
    m = Model(W, H)
    near, far = halves(C)
    m.step(
        "Turn the sheet sideways (landscape). Fold it in half left to right, crease and open again.",
        [((C, -5), (C, H + 5), (40, 120))],
        unfold=True,
    )
    m.step(
        "Fold the top edge down 2.5 cm (about a thumb's width). Crease hard.",
        [((-5, 25), (W + 5, 25), (C, 8))],
    )
    m.step(
        "Fold the folded edge down again, the same 2.5 cm.",
        [((-5, 50), (W + 5, 50), (C, 33))],
    )
    m.step(
        "And once more. The thick front edge makes it glide steadily.",
        [((-5, 75), (W + 5, 75), (C, 58))],
    )
    m.step(
        "Fold in half along the middle crease, the thick edge outside (fold the left half behind).",
        [((C, -5), (C, H + 5), (60, 150), None, "mountain")],
    )
    k = 15
    m.step(
        "Fold the wings down 1.5 cm from the middle fold, one to the front and one behind.",
        [
            ((C + k, -5), (C + k, H + 5), (280, 150), near, "valley"),
            ((C + k, -5), (C + k, H + 5), (280, 150), far, "mountain"),
        ],
    )
    return dict(m=m, hinge=C + k, near=near, far=far, w=W, h=H)


def tube():
    W, H = 297.0, 210.0
    C = W / 2
    m = Model(W, H)
    m.step(
        "Turn the sheet sideways (landscape). Fold the top edge down 7 cm, a third of the sheet.",
        [((-5, 70), (W + 5, 70), (C, 15))],
    )
    m.step(
        "Fold the folded edge down to cover half of the flap (3.5 cm).",
        [((-5, 105), (W + 5, 105), (C, 85))],
    )
    m.step(
        "Fold it down once more (about 2 cm). You now have a thick band along the top.",
        [((-5, 122.5), (W + 5, 122.5), (C, 113))],
    )
    return dict(m=m, w=W, h=H)


def _arrow_finish(m, C, H, near, far, k=16, wing_text=None):
    m.step(
        wing_text
        or "Fold the wings down 1.5 cm from the middle fold, one to the front and one behind. Keep the fold parallel to the middle fold.",
        [
            ((C + k, -5), (C + k, H + 5), (200, 285), near, "valley"),
            ((C + k, -5), (C + k, H + 5), (200, 285), far, "mountain"),
        ],
    )
    return k


def arrow_lock(k=16):
    """Blunt nose held by a little lock flap (Nakamura-style lock)."""
    W, H = 210.0, 297.0
    C = W / 2
    m = Model(W, H)
    near, far = halves(C)
    m.step(
        "Fold the sheet in half the long way, edge to edge. Crease well and open it again.",
        [((C, -5), (C, H + 5), (20, 150))],
        unfold=True,
    )
    m.step(
        "Fold both top corners down so their edges lie on the middle crease.",
        [((C, 0), (0, C), (5, 5)), ((C, 0), (W, C), (W - 5, 5))],
    )
    m.step(
        "Fold the whole top triangle down. The fold goes where the corners ended.",
        [((-5, C), (W + 5, C), (C, 20))],
    )
    ym = 180.0
    mx, my = C / 2, (C + ym) / 2
    dx, dy = C, ym - C
    p1 = (mx - dy, my + dx)
    p2 = (mx + dy, my - dx)
    m.step(
        "Fold the top corners to the middle so they meet 3 cm above the point. The little point peeks out below.",
        [
            (p2, p1, (2, C + 2)),
            ((W - p2[0], p2[1]), (W - p1[0], p1[1]), (W - 2, C + 2)),
        ],
    )
    yl = 190.0
    tipf = lambda f: (
        max(v[1] for v in f.cur()) > yl + 0.01
        and min(v[1] for v in f.cur()) >= C - 0.01
        and abs(sum(v[0] for v in f.cur()) / len(f.poly) - C) < 40
    )
    m.step(
        "Fold the little point up over the corners. This locks them, and the nose stays blunt and strong.",
        [((-5, yl), (W + 5, yl), (C, 205), tipf)],
    )
    m.step(
        "Fold in half along the middle, the lock outside (fold the left half behind).",
        [((C, -5), (C, H + 5), (60, 280), None, "mountain")],
    )
    k = _arrow_finish(
        m,
        C,
        H,
        near,
        far,
        k,
        None
        if k == 16
        else f"Fold the wings down {k / 10:.1f} cm from the middle fold, one to the front and one behind. Keep the fold parallel to the middle fold.".replace(
            ".0 cm", " cm"
        ),
    )
    return dict(m=m, hinge=C + k, near=near, far=far, w=W, h=H, tab=None)


def arrow_blunt():
    """The heavy Arrow, with its sharp point folded back."""
    W, H = 210.0, 297.0
    C = W / 2
    m = Model(W, H)
    near, far = halves(C)
    m.step(
        "Fold the sheet in half the long way, edge to edge. Crease well and open it again.",
        [((C, -5), (C, H + 5), (20, 150))],
        unfold=True,
    )
    m.step(
        "Fold both top corners down so their edges lie on the middle crease.",
        [((C, 0), (0, C), (5, 5)), ((C, 0), (W, C), (W - 5, 5))],
    )
    m.step(
        "Fold the whole top triangle down. The fold goes where the corners ended.",
        [((-5, C), (W + 5, C), (C, 20))],
    )
    m.step(
        "Fold the two new top corners to the middle again. They meet over the point.",
        [((C, C), (0, 2 * C), (3, C + 3)), ((C, C), (W, 2 * C), (W - 3, C + 3))],
    )
    xb = C - (H - C) * T225
    m.step(
        "Fold the slanted edges to the middle line once more.",
        [((C, C), (xb, H), (4, 230)), ((C, C), (W - xb, H), (W - 4, 230))],
    )
    m.step(
        "Fold the sharp point back behind by 1.5 cm. A blunt nose is safer, stronger, and still flies far.",
        [((-5, C + 15), (W + 5, C + 15), (C, C + 5), None, "mountain")],
    )
    m.step(
        "Fold in half along the middle, all the folds outside (fold the left half behind).",
        [((C, -5), (C, H + 5), (60, 280), None, "mountain")],
    )
    k = _arrow_finish(m, C, H, near, far)
    return dict(m=m, hinge=C + k, near=near, far=far, w=W, h=H, tab=None)
