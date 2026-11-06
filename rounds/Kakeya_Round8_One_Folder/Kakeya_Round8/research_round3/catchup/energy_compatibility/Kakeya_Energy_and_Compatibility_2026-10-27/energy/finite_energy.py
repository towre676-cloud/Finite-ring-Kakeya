"""Exact finite coverage, collision, and translation-parity certificates.

Only Python's standard library is used. All counts and certificates are exact.
This does not claim the unrestricted dimension-five Kakeya theorem.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


def parity(x: int) -> int:
    return x.bit_count() & 1


def quotient(x: int, d: int) -> int:
    return min(x, x ^ d)


def pair_set(points: set[int], d: int) -> set[int]:
    return {u for u in points if u < (u ^ d) and (u ^ d) in points}


def covered_sets(fibres: dict[int, set[int]], n: int, d: int, ring: str):
    assert ring in ("dual", "z4")
    answer = []
    for x in range(1 << n):
        y = x ^ d
        if x >= y:
            continue
        a = pair_set(fibres.get(x, set()), d)
        b = pair_set(fibres.get(y, set()), d)
        carry = (x & d) if ring == "z4" else 0
        s = {quotient(u ^ v ^ carry, d) for u in a for v in b}
        if s:
            answer.append(((x, y), s))
    return answer


def coverage_statistics(sets: list[set[int]], n: int, d: int):
    qs = [x for x in range(1 << n) if x < (x ^ d)]
    q = len(qs)
    multiplicity = {b: sum(b in s for s in sets) for b in qs}
    total = sum(map(len, sets))
    intersections = sum(
        len(sets[i] & sets[j])
        for i in range(len(sets))
        for j in range(i + 1, len(sets))
    )
    chars = [ell for ell in range(1 << n) if parity(ell & d) == 0]
    fourier = {
        ell: sum((1 - 2 * parity(ell & b)) * multiplicity[b] for b in qs)
        for ell in chars
    }
    l_bound = len(sets)
    # Cover implies this integer is nonnegative. No division or rounding.
    collision_slack = l_bound * (total - q) - 2 * intersections
    # The Walsh congruence diagonalizes the exact slack matrix.
    psd_eigenvalues = [q * (multiplicity[b] - 1) for b in qs]
    return {
        "q": q,
        "set_sizes": [len(s) for s in sets],
        "total_local_sumset_size": total,
        "union_size": sum(v > 0 for v in multiplicity.values()),
        "multiplicity": multiplicity,
        "pairwise_intersection_sum": intersections,
        "maximum_active_channels": l_bound,
        "collision_slack": collision_slack,
        "single_character_cuts_pass": all(
            abs(fourier[ell]) <= total - q for ell in chars if ell
        ),
        "nontrivial_fourier_coefficients": {
            ell: fourier[ell] for ell in chars if ell
        },
        "exact_psd_eigenvalues": psd_eigenvalues,
    }


def translate(fibres: dict[int, set[int]], shifts: dict[int, int]):
    return {x: {u ^ shifts.get(x, 0) for u in a} for x, a in fibres.items()}


def unavoidable_overlap(a: set[int], b: set[int], n: int, d: int) -> int:
    reps = [h for h in range(1 << n) if h < (h ^ d)]
    return min(len(a & {quotient(v ^ h, d) for v in b}) for h in reps)


def tree_overlap_bound(sets: list[set[int]], n: int, d: int):
    """Union upper bound valid under arbitrary independent translations.

    Maximum spanning tree in the complete graph of minimum translate overlaps.
    """
    if not sets:
        return {"union_upper_bound": 0, "tree_weight": 0, "tree_edges": []}
    weights = {
        (i, j): unavoidable_overlap(sets[i], sets[j], n, d)
        for i in range(len(sets)) for j in range(i + 1, len(sets))
    }
    seen = {0}
    chosen = []
    while len(seen) < len(sets):
        weight, i, j = max(
            (weights[tuple(sorted((i, j)))], i, j)
            for i in seen for j in range(len(sets)) if j not in seen
        )
        chosen.append((i, j, weight))
        seen.add(j)
    total_weight = sum(w for _, _, w in chosen)
    return {
        "union_upper_bound": sum(map(len, sets)) - total_weight,
        "tree_weight": total_weight,
        "tree_edges": chosen,
        "minimum_translate_overlaps": {f"{i},{j}": w for (i, j), w in weights.items()},
    }


def verify_tree_overlap_certificate(sets, n, d, certificate):
    """Verify a tree certificate without trusting the tree optimizer.

    Translation intersection counts are recomputed by point membership, and a
    separate union-find check verifies that the supplied edges form a tree.
    Optimality is unnecessary: every verified tree gives a sound union bound.
    """
    count = len(sets)
    if not count:
        assert certificate["union_upper_bound"] == 0
        assert not certificate["tree_edges"]
        return True
    parent = list(range(count))

    def find(v):
        while parent[v] != v:
            v = parent[v]
        return v

    assert len(certificate["tree_edges"]) == count - 1
    total_weight = 0
    for i, j, weight in certificate["tree_edges"]:
        assert 0 <= i < count and 0 <= j < count and i != j
        assert find(i) != find(j)
        parent[find(i)] = find(j)
        overlaps = []
        for h in range(1 << n):
            if h > (h ^ d):
                continue
            overlaps.append(sum(quotient(u ^ h, d) in sets[j] for u in sets[i]))
        assert weight == min(overlaps)
        total_weight += weight
    assert len({find(i) for i in range(count)}) == 1
    assert total_weight == certificate["tree_weight"]
    assert certificate["union_upper_bound"] == sum(map(len, sets)) - total_weight
    return True


def direct_lift_count(fibres: dict[int, set[int]], n: int, d: int, ring: str):
    """Independent point-level line test for all lifts of one residue direction.

    For Z/4 this computes coordinate arithmetic modulo four, rather than using
    the quotient carry formula. For the dual ring it multiplies formal pairs.
    """
    points = {(x, y) for x, a in fibres.items() for y in a}
    lifts = [b for b in range(1 << n) if b < (b ^ d)]
    count = 0
    for b in lifts:
        covered = False
        for x, y in points:
            line = []
            for t in range(4):
                xx = yy = 0
                for i in range(n):
                    base = ((x >> i) & 1) + 2 * ((y >> i) & 1)
                    v = ((d >> i) & 1) + 2 * ((b >> i) & 1)
                    if ring == "z4":
                        value = (base + t * v) % 4
                    else:
                        low = (base & 1) ^ ((t & 1) & (v & 1))
                        high = ((base >> 1) & 1) ^ (
                            ((t & 1) & ((v >> 1) & 1))
                            ^ (((t >> 1) & 1) & (v & 1))
                        )
                        value = low + 2 * high
                    xx |= (value & 1) << i
                    yy |= ((value >> 1) & 1) << i
                line.append((xx, yy))
            if all(p in points for p in line):
                covered = True
                break
        count += covered
    return count


def tight_halfspace_rows(fibres, n, directions, ring):
    """Produce equations ell(T)=rhs for matchings on the same four vertices.

    Se denotes the quotient sumset at the supplied canonical fibre positions.
    Translating each internal fibre by tx changes its Se phase by ell(tx+ty).
    Both matching edges partition the same four vertices, hence T = xor(tx).
    """
    rows = []
    vertex_set = None
    q = 1 << (n - 1)
    for d in directions:
        entries = covered_sets(fibres, n, d, ring)
        assert len(entries) == 2
        vs = set(itertools.chain.from_iterable(e for e, _ in entries))
        assert len(vs) == 4
        if vertex_set is None:
            vertex_set = vs
        assert vs == vertex_set
        assert all(len(s) == q // 2 for _, s in entries)
        found = []
        for ell in range(1, 1 << n):
            if parity(ell & d):
                continue
            phases = [{parity(ell & u) for u in s} for _, s in entries]
            if all(len(p) == 1 for p in phases):
                rhs = 1 ^ next(iter(phases[0])) ^ next(iter(phases[1]))
                found.append((ell, rhs))
        assert len(found) == 1
        ell, rhs = found[0]
        rows.append({"direction": d, "normal": ell, "rhs": rhs})
    return rows


def xor_certificate(rows):
    ell = rhs = 0
    for row in rows:
        ell ^= row["normal"]
        rhs ^= row["rhs"]
    return {"xor_normal": ell, "xor_rhs": rhs, "contradiction": ell == 0 and rhs == 1}


def run():
    report = {"scope": "Exact finite lemmas and local fixtures; no new full n=5 case closure."}

    # The full hub star is a positive control in both rings.
    star = {0: set(range(32)), **{x: {0, x} for x in range(1, 32)}}
    assert sum(map(len, star.values())) == 94
    star_rows = []
    for ring in ("dual", "z4"):
        for d in range(1, 32):
            ss = [s for _, s in covered_sets(star, 5, d, ring)]
            stats = coverage_statistics(ss, 5, d)
            assert stats["union_size"] == 16
            assert stats["total_local_sumset_size"] == 16
            assert stats["collision_slack"] == 0
            assert set(stats["exact_psd_eigenvalues"]) == {0}
            assert direct_lift_count(star, 5, d, ring) == 16
            bound = tree_overlap_bound(ss, 5, d)
            assert verify_tree_overlap_certificate(ss, 5, d, bound)
            assert bound["union_upper_bound"] == 16
            star_rows.append({"ring": ring, "direction": d, "covered": 16})
    report["star_positive_control"] = {"weight": 94, "checked_ring_direction_rows": len(star_rows)}

    # Local n5 regression. d=16 makes quotient representatives exactly 0..15.
    # Every local convolution here is injective; covered-set multiplicity equals
    # pair-representation multiplicity, so both versions of the cuts apply.
    d = 16
    factors = [{0, 8}, set(range(1, 8)), {0, 8}, {1, 2, 3}]
    bases = [0, 16, 1, 17]
    regression = {
        x: {u ^ z for u in e for z in (0, d)}
        for x, e in zip(bases, factors)
    }
    ss = [s for _, s in covered_sets(regression, 5, d, "dual")]
    stats = coverage_statistics(ss, 5, d)
    assert sorted(stats["set_sizes"]) == [6, 14]
    assert stats["union_size"] == 14
    assert stats["single_character_cuts_pass"]
    assert stats["collision_slack"] == -4
    assert direct_lift_count(regression, 5, d, "dual") == 14
    assert direct_lift_count(regression, 5, d, "z4") == 14
    report["collision_regression_n5"] = {
        "direction": d,
        "fibre_weights": {x: len(a) for x, a in regression.items()},
        "fibre_points": {x: sorted(a) for x, a in regression.items()},
        **stats,
    }

    # A stronger one-direction fixture: no choice of independent fibre shifts
    # can make the two output sets cover Q. This cut preserves translation gauges.
    output = {0, 1, 2, 3, 4, 6, 8, 9}
    robust_factors = [{0}, output, {0}, output]
    robust = {
        x: {u ^ z for u in e for z in (0, d)}
        for x, e in zip(bases, robust_factors)
    }
    robust_sets = [s for _, s in covered_sets(robust, 5, d, "dual")]
    robust_bound = tree_overlap_bound(robust_sets, 5, d)
    assert robust_bound["tree_weight"] == 2
    assert robust_bound["union_upper_bound"] == 14
    assert verify_tree_overlap_certificate(robust_sets, 5, d, robust_bound)
    shift_maximum = max(
        len({v ^ h for v in output} | {v ^ k for v in output})
        for h in range(16) for k in range(16)
    )
    assert shift_maximum == 14
    shift_witness = next(h for h in range(16) if len(output | {v ^ h for v in output}) == 14)
    best_robust = translate(robust, {17: shift_witness})
    robust_direct = {ring: direct_lift_count(best_robust, 5, d, ring) for ring in ("dual", "z4")}
    assert robust_direct == {"dual": 14, "z4": 14}
    report["translation_uniform_overlap_regression_n5"] = {
        "direction": d,
        "fibre_weights": {x: len(a) for x, a in robust.items()},
        "canonical_output_set": sorted(output),
        "total_local_sumset_size": 16,
        "independent_output_translation_pairs_checked": 256,
        "maximum_union_over_all_output_translations": shift_maximum,
        "attaining_shift_on_base17": shift_witness,
        "independent_direct_ring_lift_counts": robust_direct,
        "independent_tree_certificate_verified": True,
        **robust_bound,
    }

    # Lift the n2 three-hole obstruction to genuine 12-point fibres in n5.
    # These four distinct planes lie in W={0,4,8,...,28}.
    planes = [{0, 8, 16, 24}, {0, 4, 16, 20}, {0, 12, 16, 28}, {0, 4, 8, 12}]
    w = set(range(0, 32, 4))
    assert set().union(*planes) == w
    for a, b in itertools.combinations(planes, 2):
        assert {u ^ v for u in a for v in b} == w
    block = {x: {u ^ h for u in (1, 2, 3) for h in planes[x]} for x in range(4)}
    assert all(len(a) == 12 for a in block.values())
    block_report = {}
    for ring in ("dual", "z4"):
        rows = tight_halfspace_rows(block, 5, (1, 2, 3), ring)
        count = 0
        first = None
        for ts in itertools.product(range(4), repeat=4):
            moved = translate(block, dict(enumerate(ts)))
            covered = [len(set().union(*(s for _, s in covered_sets(moved, 5, d, ring)))) for d in (1, 2, 3)]
            succeeds = covered == [16, 16, 16]
            total_shift = ts[0] ^ ts[1] ^ ts[2] ^ ts[3]
            predicted = all(parity(row["normal"] & total_shift) == row["rhs"] for row in rows)
            assert predicted == succeeds
            if succeeds:
                count += 1
                if first is None:
                    first = ts
        assert count == (0 if ring == "dual" else 64)
        witness = (3, 0, 0, 0)
        moved = translate(block, dict(enumerate(witness)))
        direct = [direct_lift_count(moved, 5, d, ring) for d in (1, 2, 3)]
        if ring == "z4":
            assert direct == [16, 16, 16]
        else:
            assert direct == [16, 16, 8]
        block_report[ring] = {
            "linear_equations": rows,
            "sum_certificate": xor_certificate(rows),
            "low_component_translation_assignments_checked": 256,
            "successful_assignments": count,
            "first_success": first,
            "direct_ring_lift_counts_for_shifts_3_0_0_0": direct,
        }
    report["three_matching_block_n5"] = {
        "base_support": [0, 1, 2, 3],
        "fibre_points": {x: sorted(a) for x, a in block.items()},
        "fibre_weight": 12,
        "total_block_weight": 48,
        "scope": "Obstruction on three residue directions when no additional base edges contribute there; not a complete Kakeya candidate.",
        **block_report,
    }

    # Exhaustive verification of the collision inequality over all triples of
    # subsets of a four-point quotient; independent of the ring representation.
    tiny_sets = [{i for i in range(4) if mask & (1 << i)} for mask in range(16)]
    fixtures = covers = 0
    for ss in itertools.product(tiny_sets, repeat=3):
        fixtures += 1
        nu = [sum(i in s for s in ss) for i in range(4)]
        total = sum(nu)
        j = sum(v * (v - 1) // 2 for v in nu)
        if min(nu):
            covers += 1
            assert 2 * j <= 3 * (total - 4)
        # View the four points as representatives of F2^3/<4>.
        bound = tree_overlap_bound(list(ss), 3, 4)
        assert verify_tree_overlap_certificate(list(ss), 3, 4, bound)
        assert sum(v > 0 for v in nu) <= bound["union_upper_bound"]
    report["collision_formula_exhaustion"] = {"set_triples": fixtures, "full_covers": covers}
    return report


if __name__ == "__main__":
    report = run()
    destination = Path(__file__).with_name("finite_energy_receipt.json")
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "receipt": str(destination),
        "star": report["star_positive_control"],
        "collision_slack": report["collision_regression_n5"]["collision_slack"],
        "block_dual_count": report["three_matching_block_n5"]["dual"]["successful_assignments"],
        "block_z4_count": report["three_matching_block_n5"]["z4"]["successful_assignments"],
        "exhaustion": report["collision_formula_exhaustion"],
    }, indent=2))
