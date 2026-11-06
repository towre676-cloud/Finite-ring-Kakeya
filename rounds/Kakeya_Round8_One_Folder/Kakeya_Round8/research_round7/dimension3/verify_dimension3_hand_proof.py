#!/usr/bin/env python3
"""Independent finite corroboration of the elementary dimension-three proof.

Uses only Python's standard library. No SAT encoder, solver, spectrum
census, or orbit catalogue is read. The accompanying written proof is a
hand argument; these finite checks are supplementary reproducibility.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
V = set(range(8))


def pair_set(points, d):
    return {min(x, x ^ d) for x in points if x ^ d in points}


def pair_counts(points):
    return {d: len(pair_set(points, d)) for d in range(1, 8)}


def direction_space(points):
    if not points:
        return {0}
    origin = min(points)
    span = {0}
    for x in points:
        span |= {y ^ x ^ origin for y in span}
    return span


def scalar_add(x, y, ring):
    return ((x + y) & 3) if ring == 'z4' else x ^ y


def scalar_multiply(x, y, ring):
    if ring == 'z4':
        return (x * y) & 3
    return ((x & 1) & (y & 1)) | ((((x & 1) & (y >> 1)) ^
                                                ((x >> 1) & (y & 1))) << 1)


def vector(residue, tangent):
    return tuple(((residue >> i) & 1) + 2 * ((tangent >> i) & 1) for i in range(3))


def residue_tangent(point):
    return (sum((x & 1) << i for i, x in enumerate(point)),
            sum((x >> 1) << i for i, x in enumerate(point)))


def line(point, direction, ring):
    return {tuple(scalar_add(x, scalar_multiply(t, y, ring), ring)
                  for x, y in zip(point, direction)) for t in range(4)}


def main():
    start = time.monotonic()
    shapes = [{x for x in range(8) if mask >> x & 1} for mask in range(256)]
    qmax = {w: 0 for w in range(9)}
    energy_distributions = {w: Counter() for w in range(9)}
    complement_checks = period_checks = 0
    planes = []
    for A in shapes:
        w = len(A)
        counts = pair_counts(A)
        Q = sum(p * p for p in counts.values())
        qmax[w] = max(qmax[w], Q)
        energy_distributions[w][Q] += 1
        assert sum(counts.values()) == w * (w - 1) // 2
        other = pair_counts(V - A)
        for d in range(1, 8):
            assert counts[d] == w - 4 + other[d]
            complement_checks += 1
        if w == 2:
            assert sorted(counts.values()) == [0] * 6 + [1]
        elif w == 3:
            assert sorted(counts.values()) == [0] * 4 + [1] * 3
            assert len({0} | {d for d, p in counts.items() if p}) == 4
        elif w == 4:
            if len(direction_space(A)) == 4:
                assert sorted(counts.values()) == [0] * 4 + [2] * 3
                planes.append(A)
            else:
                assert sorted(counts.values()) == [0] + [1] * 6
            for a in range(1, 8):
                for b in range(1, 8):
                    if a != b and counts[a] > 0 and counts[b] == 2:
                        assert direction_space(A) == {0, a, b, a ^ b}
                        period_checks += 1
        elif w == 5:
            assert sorted(counts.values()) == [1] * 4 + [2] * 3
            maximum = {0} | {d for d, p in counts.items() if p == 2}
            assert len(maximum) == 4 and all(a ^ b in maximum for a in maximum for b in maximum)
        elif w == 6:
            assert sorted(counts.values()) == [2] * 6 + [3]
        elif w == 7:
            assert set(counts.values()) == {3}
        elif w == 8:
            assert set(counts.values()) == {4}
        if 2 <= w <= 5:
            assert 2 * (Q - 1) <= 11 * (w - 2)
    assert qmax == {0: 0, 1: 0, 2: 1, 3: 3, 4: 12, 5: 16, 6: 33, 7: 63, 8: 112}

    common_plane_checks = 0
    for A in planes:
        H = direction_space(A)
        for B in planes:
            if direction_space(B) != H:
                continue
            for d in H - {0}:
                X, Y = pair_set(A, d), pair_set(B, d)
                assert len({x ^ y for x in X for y in Y}) == 2
                common_plane_checks += 1
    assert len(planes) == 14 and common_plane_checks == 84

    # Every possible support of each size, with every possible largest hub.
    support5 = support6 = support7 = support8 = 0
    spoke_intersections = 0
    for S_tuple in itertools.combinations(range(8), 5):
        S = set(S_tuple)
        missing = V - S
        centre = 0
        for x in missing:
            centre ^= x
        assert centre in S
        P = S - {centre}
        H = direction_space(P)
        assert len(P) == len(H) == 4
        spokes = {centre ^ x for x in P}
        assert len(spokes) == 4 and 0 not in spokes
        multiplicities = Counter(a ^ b for a, b in itertools.combinations(S, 2))
        assert all(multiplicities[d] == 1 for d in spokes)
        assert all(multiplicities[d] == 2 for d in H - {0})
        for Q in planes:
            if 0 in Q:
                assert len(spokes & Q) <= 2
                spoke_intersections += 1
        support5 += 1
    for S_tuple in itertools.combinations(range(8), 6):
        S = set(S_tuple)
        for hub in S:
            translated = {x ^ hub for x in S}
            a, b = sorted(V - translated)
            assert a and b
            H = {0, a, b, a ^ b}
            C = V - H
            assert translated == C | {0, a ^ b}
            multiplicities = Counter(x ^ y for x, y in itertools.combinations(translated, 2))
            assert multiplicities[a] == multiplicities[b] == 2
            assert multiplicities[a ^ b] == 3
            for d in (a, b):
                edges = [(x, y) for x, y in itertools.combinations(translated, 2) if x ^ y == d]
                assert len(edges) == 2 and {x for edge in edges for x in edge} == C
            support6 += 1
    for S_tuple in itertools.combinations(range(8), 7):
        S = set(S_tuple)
        for hub in S:
            translated = {x ^ hub for x in S}
            d, = V - translated
            edges = [(x, y) for x, y in itertools.combinations(translated, 2) if x ^ y == d]
            assert len(edges) == 3 and {x for edge in edges for x in edge} == translated - {0}
            support7 += 1
    for S_tuple in itertools.combinations(range(8), 8):
        multiplicities = Counter(x ^ y for x, y in itertools.combinations(S_tuple, 2))
        assert set(multiplicities.values()) == {4}
        support8 += 1
    assert (support5, support6, support7, support8) == (56, 168, 56, 1)

    partitions = {}
    for s in range(5, 9):
        partitions[s] = [weights for weights in itertools.combinations_with_replacement(range(2, 9), s)
                         if sum(weights) <= 21]
    s6_survivors = [w for w in partitions[6] if max(w) <= 6 and sum(qmax[x] for x in w) >= 56]
    expected = [(2, 2, 2, 2, 6, 6), (2, 2, 2, 3, 6, 6),
                (2, 2, 2, 4, 4, 6), (2, 2, 2, 4, 5, 6),
                (2, 2, 3, 3, 5, 6), (2, 2, 3, 4, 4, 6)]
    assert s6_survivors == expected
    for weights in s6_survivors:
        heavy = [w for w in weights if w >= 4]
        light = [w for w in weights if w <= 3]
        h, n6 = len(heavy), weights.count(6)
        C0 = sum(w * (w - 1) // 2 for w in light)
        assert n6 >= 1 and h in (2, 3)
        assert 2 * C0 + n6 < 4 * (7 - h * (h - 1) // 2)
    s7_energy_max = max(sum(qmax[x] for x in w) for w in partitions[7] if max(w) <= 6)
    s8_energy_max = max(sum(qmax[x] for x in w) for w in partitions[8] if max(w) <= 6)
    assert s7_energy_max == 54 and s8_energy_max == 42
    assert [w for w in partitions[8] if max(w) == 7] == [(2, 2, 2, 2, 2, 2, 2, 7)]
    assert max(3 * x + y for x in range(8) for y in range(4) if x + 2 * y <= 7) == 21
    outer5_fullhub_profiles = [w for w in itertools.combinations_with_replacement(range(2, 9), 4) if sum(w) <= 13]
    for weights in outer5_fullhub_profiles:
        heavy = [w for w in weights if w >= 4]
        assert len(heavy) <= 2
        if len(heavy) == 1:
            assert heavy[0] <= 7
        if len(heavy) == 2:
            assert max(heavy) <= 5

    # Direct ring arithmetic validates the line reduction and the upper bound.
    ring_checks = {}
    for ring in ('z4', 'dual'):
        checked_lines = 0
        for a in range(8):
            for tangent in range(8):
                origin = vector(a, tangent)
                for d in range(1, 8):
                    for e in range(8):
                        points = line(origin, vector(d, e), ring)
                        assert len(points) == 4
                        fibres = {}
                        for point in points:
                            residue, t = residue_tangent(point)
                            fibres.setdefault(residue, set()).add(t)
                        assert set(fibres) == {a, a ^ d}
                        assert all(len(A) == 2 for A in fibres.values())
                        X, Y = pair_set(fibres[a], d), pair_set(fibres[a ^ d], d)
                        assert len(X) == len(Y) == 1
                        x, = X
                        y, = Y
                        carry = a & d if ring == 'z4' else 0
                        label = x ^ y ^ carry
                        assert min(label, label ^ d) == min(e, e ^ d)
                        checked_lines += 1
        star = {vector(0, t) for t in range(8)}
        star |= {vector(d, t) for d in range(1, 8) for t in (0, d)}
        assert len(star) == 22
        star_lines = set()
        for d in range(1, 8):
            for e in range(8):
                points = line(vector(0, e), vector(d, e), ring)
                assert points <= star
                assert points == {vector(0, e), vector(0, e ^ d), vector(d, 0), vector(d, d)}
                star_lines.add(frozenset(points))
        assert len(star_lines) == 28
        ring_checks[ring] = {'primitive_line_instances_checked': checked_lines,
                             'star_points': 22, 'star_primitive_vectors_checked': 56,
                             'star_direction_classes': len(star_lines)}

    proof = HERE / 'DIMENSION3_ELEMENTARY_PROOF.md'
    receipt = {
        'status': 'PASS_ELEMENTARY_DIMENSION3_THEOREM_FINITE_CORROBORATION',
        'theorem': 'k_R(3)=22 for R=Z/4Z and R=F2[epsilon]/(epsilon^2)',
        'proof_does_not_depend_on_this_enumeration': True,
        'sat_or_external_census_used': False,
        'binary3_subsets_exhausted': 256,
        'qmax_by_weight': qmax,
        'energy_distribution_by_weight': {w: dict(sorted(c.items())) for w, c in energy_distributions.items()},
        'complement_identities_checked': complement_checks,
        'four_point_period_span_implications_checked': period_checks,
        'shared_plane_sumset_capacity_checks': common_plane_checks,
        'five_support_geometries_checked': support5,
        'five_support_spoke_two_space_intersection_checks': spoke_intersections,
        'six_support_and_hub_geometries_checked': support6,
        'seven_support_and_hub_geometries_checked': support7,
        'eight_support_geometries_checked': support8,
        'partitions_checked_by_support': {s: len(p) for s, p in partitions.items()},
        'support6_cap6_energy_survivors': s6_survivors,
        'all_six_survivors_fail_heavy_light_bound': True,
        'support7_cap6_exact_energy_maximum': s7_energy_max,
        'support8_cap6_exact_energy_maximum': s8_energy_max,
        'full_support7hub_capacity_upper_bound': 21,
        'full_support_required_capacity': 28,
        'full_centre_support5_outer_profiles_checked': len(outer5_fullhub_profiles),
        'direct_ring_checks': ring_checks,
        'proof_sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
        'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'seconds': round(time.monotonic() - start, 6),
        'formalization': 'Written elementary proof plus finite corroboration; not a full proof-assistant theorem.'}
    (HERE / 'DIMENSION3_HAND_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
