import pytest

from planes.fold import Model, ap, comp, inv, refl


def test_reflection_is_its_own_inverse():
    r = refl((0, 0), (1, 1))
    assert ap(comp(r, r), (3.0, -2.0)) == pytest.approx((3.0, -2.0))
    assert ap(r, (2.0, 0.0)) == pytest.approx((0.0, 2.0))


def test_inverse_undoes_a_map():
    m = comp(refl((10, 0), (10, 5)), refl((0, 3), (5, 3)))
    x, y = ap(inv(m), ap(m, (7.0, 11.0)))
    assert abs(x - 7.0) < 1e-9
    assert abs(y - 11.0) < 1e-9


def test_folding_in_half_stacks_the_halves():
    m = Model(210, 297)
    m.step("half", [((105, -5), (105, 302), (20, 150))])
    xs = [v[0] for f in m.facets for v in f.cur()]
    assert min(xs) == pytest.approx(105)  # the left half went over to the right
    assert max(xs) == pytest.approx(210)
    assert sorted(f.flipped for f in m.facets) == [False, True]


def test_first_fold_records_a_valley_crease():
    m = Model(210, 297)
    m.step("half", [((105, -5), (105, 302), (20, 150))])
    assert [c[1] for c in m.creases] == ["valley"]


def test_unfold_step_leaves_a_crease_but_a_flat_sheet():
    m = Model(210, 297)
    m.step("crease", [((105, -5), (105, 302), (20, 150))], unfold=True)
    assert not any(f.flipped for f in m.facets)
    assert len(m.creases) == 1
