"""Check finite geometry and arithmetic for two partial support-eleven cuts."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import json

import degree7_pair_budget
from verify_support11_subspaces import span

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def star_check(f):
    assert len(f) == 10
    assert not any(a ^ b in f for a, b in combinations(f, 2))
    periods = {z for z in range(32) if {x ^ z for x in f} == f}
    assert len(periods) == 2
    h = next(iter(periods - {0}))
    intersections = {z: len(f & {x ^ z for x in f}) for z in range(1, 32)}
    assert intersections[h] == 10
    assert all(n <= 4 for z, n in intersections.items() if z != h)
    odd_cycle_bounds = []
    for r in range(2, 7):
        length = 2 * r + 1
        outside = 13 - length
        odd_cycle_bounds.append(length + r * outside + outside * outside // 4)
    assert odd_cycle_bounds == [37, 34, 29, 22, 13]
    assert [(a, 13 - a) for a in range(7) if a * (13 - a) >= 40] == [(5, 8), (6, 7)]
    # Two non-twin vertices exist in either smaller side. Even if every
    # missing edge touches one of them, five common neighbours remain.
    assert 7 - (6 * 7 - 40) == 5 > 4
    assert all(93 - c - 80 <= 5 for c in range(8, 14))
    assert 10 * 4 == 40 > 39
    return {"period": h, "intersection_histogram": dict(sorted(Counter(intersections.values()).items())),
            "odd_cycle_bounds": odd_cycle_bounds, "centre_weight_minimum": 16}


def degree7_witness(f):
    assert len(f) == 7
    for h in range(1, 32):
        core = f & {x ^ h for x in f}
        if len(core) != 6:
            continue
        base = min(core)
        v = span(x ^ base for x in core)
        hull = {base ^ x for x in v}
        if len(v) != 8:
            continue
        missing = hull - core
        if len(missing) != 2:
            continue
        c = min(missing)
        if core != {c ^ x for x in v - {0, h}}:
            continue
        b = next(iter(f - core))
        ell = span(v | {c})
        if len(ell) != 16 or b in ell:
            continue
        # Supply an explicit graph isomorphism in binary coordinates:
        # internal h, two block coordinates in V/<h>, side c, layer b.
        generators = [h]
        for x in sorted(v):
            if x not in span(generators):
                generators.append(x)
        assert len(generators) == 3
        vertices = {}
        for internal, q0, q1, side, layer in product(range(2), repeat=5):
            x = (internal * h) ^ (q0 * generators[1]) ^ (q1 * generators[2]) ^ (side * c) ^ (layer * b)
            vertices[x] = (internal, q0 + 2 * q1, side, layer)
        assert len(vertices) == 32
        for a, d in combinations(range(32), 2):
            ia, qa, sa, la = vertices[a]
            ib, qb, sb, lb = vertices[d]
            expected = ((la == lb and sa != sb and qa != qb)
                        or (la != lb and ia == ib and qa == qb and sa == sb))
            assert ((a ^ d) in f) == expected
        return {"period_of_six_set": h, "V": sorted(v), "side_generator": c,
                "layer_generator": b, "basis_for_V": generators}
    raise AssertionError("No claimed graph decomposition")


def check_dp_formula():
    # A block has four cells, each with two possible internal positions.
    # Enumerating all256 choices proves that the maximum number of matching
    # edges at any fixed count vector is exactly the two minimum terms.
    attainable = {}
    for masks in product(range(4), repeat=4):
        a0, a1, b0, b1 = [m.bit_count() for m in masks]
        matches = (masks[0] & masks[1]).bit_count() + (masks[2] & masks[3]).bit_count()
        key = (a0, a1, b0, b1)
        attainable[key] = max(attainable.get(key, -1), matches)
    assert len(attainable) == 81
    assert all(n == min(a0, a1) + min(b0, b1) for (a0, a1, b0, b1), n in attainable.items())
    result = degree7_pair_budget.calculate()
    expected = [0, 0, 1, 2, 4, 6, 9, 12, 16, 18, 21, 24, 28, 32, 37, 42, 48]
    assert result["max_induced_edges_by_weight"][:17] == expected
    assert max(expected[:12]) == 24
    return result


def check_two_centre_budget():
    assert all(2 * a + 84 > 93 for a in range(8, 12))
    assert 5 * 4 + 2 * 2 == 24 > 8 * 8 // 4
    assert all(2 * a + 76 > 93 for a in range(9, 12))
    assert 6 * 4 + 2 == 26 > 24
    assert 24 + 6 * 8 + 16 + 4 + 2 == 94
    assert 24 + 6 * 8 + 32 + 2 + 2 > 93
    assert 2 * 12 + 8 * 8 + 2 == 90
    return {"two_centre_weight_minimum": 12, "low_centre_baseline": [12, 12] + [8] * 8 + [2],
            "low_centre_slack_at_most": 3, "low_centre_branch_excluded_by_these_bounds": False}


def main():
    if not __debug__:
        raise SystemExit("Run without -O")
    star = []
    double_centre = []
    catalogue = ROOT / "research_round6/imported_claude_round4/data/orbits_all.txt"
    for line in catalogue.read_text().splitlines():
        k, mask, stab, covering = map(int, line.split())
        if k != 10 or not covering:
            continue
        support = {0} | {x for x in range(1, 32) if mask >> x & 1}
        mult = Counter(a ^ b for a, b in combinations(support, 2))
        edges = [(a, b) for a, b in combinations(support, 2) if mult[a ^ b] == 1]
        degrees = Counter(x for edge in edges for x in edge)
        if max(degrees.values()) == 10:
            centre = next(x for x, d in degrees.items() if d == 10)
            f = {centre ^ x for x in support - {centre}}
            star.append({"mask": mask, "centre": centre, **star_check(f)})
        if len(edges) == 15:
            centres = [x for x, d in degrees.items() if d == 7]
            assert len(centres) == 2
            witnesses = []
            for centre in centres:
                f = {a ^ b for a, b in edges if centre in (a, b)}
                witnesses.append({"centre": centre, **degree7_witness(f)})
            double_centre.append({"mask": mask, "witnesses": witnesses})
    assert [r["mask"] for r in star] == [360808726, 377585942]
    assert [r["mask"] for r in double_centre] == [40468758, 151587158, 287383838, 411111830, 411140502]
    result = {"status": "PASS_PARTIAL_LOCAL_RESTRICTIONS", "complete_support_exclusion": False,
              "star_cases": star, "two_degree7_centre_cases": double_centre,
              "exact_degree7_pair_budget": check_dp_formula(), "two_centre_budget": check_two_centre_budget()}
    target = HERE / "ADDITIONAL_LOCAL_GRAPH_CUTS_REPLAY.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "star_marked_cases": len(star),
                      "double_centre_marked_cases": len(double_centre),
                      "complete_support_exclusion": False}, indent=2))


if __name__ == "__main__":
    main()
