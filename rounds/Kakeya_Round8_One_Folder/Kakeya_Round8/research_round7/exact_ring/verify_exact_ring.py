#!/usr/bin/env python3
"""Finite geometric/Boolean replay of the exact two-ring encoder.

The geometry comparison uses literal ring addition/multiplication to
enumerate lines, independently of the encoder's carry/quotient formula.
Complete line-term equality proves the coverage equivalence for every
membership assignment on each tested support, not just sampled point sets.
"""
from pathlib import Path
import gc
import hashlib
import itertools
import json
import random
import time
import encode_exact_ring as E

HERE = Path(__file__).resolve().parent


def add_scalar(a, b, ring):
    return (a + b) % 4 if ring == "z4" else a ^ b


def multiply_scalar(a, b, ring):
    if ring == "z4":
        return (a * b) % 4
    return ((a & 1) & (b & 1)) | ((((a & 1) & (b >> 1)) ^ ((a >> 1) & (b & 1))) << 1)


def point(a, x, n):
    return tuple(((a >> bit) & 1) + 2 * ((x >> bit) & 1) for bit in range(n))


def bits(p):
    a = sum((z & 1) << i for i, z in enumerate(p))
    x = sum((z >> 1) << i for i, z in enumerate(p))
    return a, x


def point_id(p):
    a, x = bits(p)
    return (a << len(p)) | x


def line(base, direction, ring):
    return frozenset(tuple(add_scalar(x, multiply_scalar(t, v, ring), ring)
                           for x, v in zip(base, direction)) for t in range(4))


def direction_classes(n, ring):
    """Primitive vectors modulo actual multiplication by the two ring units."""
    choices = {}
    for v in itertools.product(range(4), repeat=n):
        if not any(x & 1 for x in v):
            continue
        other = tuple(multiply_scalar(3, x, ring) for x in v)
        representative = min(v, other)
        a, x = bits(representative)
        key = (a, min(x, x ^ a))
        if key in choices and choices[key] != representative:
            raise AssertionError("Direction quotient disagrees with ring-unit orbit")
        choices[key] = representative
    assert len(choices) == ((1 << n) - 1) * (1 << (n - 1))
    return choices


def direct_line_terms(support, n, ring):
    S = set(support)
    allowed = [point(a, x, n) for a in sorted(S) for x in range(1 << n)]
    result = {}
    for key, direction in direction_classes(n, ring).items():
        terms = set()
        for base in allowed:
            points = line(base, direction, ring)
            if all(bits(p)[0] in S for p in points):
                if len(points) != 4:
                    raise AssertionError("A primitive line has fewer than four points")
                terms.add(sum(1 << point_id(p) for p in points))
        result[key] = terms
    return result


def encoder_line_terms(support, n, ring):
    N = 1 << n
    result = {(d, u): set() for d in range(1, N) for u in E.quotient_representatives(n, d)}
    for a, b in itertools.combinations(sorted(support), 2):
        d = a ^ b
        for x in E.quotient_representatives(n, d):
            for y in E.quotient_representatives(n, d):
                u = E.quotient(x ^ y ^ E.carry(a, d, ring), d)
                coordinates = [(a, x), (a, x ^ d), (b, y), (b, y ^ d)]
                result[d, u].add(sum(1 << ((v << n) | z) for v, z in coordinates))
    return result


def coverage_from_terms(fibres, terms, n):
    K = sum(1 << ((a << n) | x) for a, A in fibres.items() for x in A)
    return {key for key, clauses in terms.items() if any(K & term == term for term in clauses)}


def verify_actual_kakeya(fibres, n, ring):
    """Direct membership check using actual ring lines, without pair identities."""
    K = {point(a, x, n) for a, A in fibres.items() for x in A}
    missing = []
    directions = direction_classes(n, ring)
    for key, direction in directions.items():
        if not any(line(base, direction, ring) <= K for base in K):
            missing.append(list(key))
    return {"is_kakeya": not missing, "point_count": len(K),
            "direction_count": len(directions), "missing_directions": missing}


def linear_image(x, columns):
    value = 0
    for i, column in enumerate(columns):
        if x >> i & 1:
            value ^= column
    return value


def direct_shear(p, t, columns, ring):
    n = len(p)
    result = []
    for i in range(n):
        y = add_scalar(p[i], 2 * ((t >> i) & 1), ring)
        for j in range(n):
            coefficient = 2 * ((columns[j] >> i) & 1)
            y = add_scalar(y, multiply_scalar(coefficient, p[j], ring), ring)
        result.append(y)
    return tuple(result)


def check_totalizers():
    trials, assignments = 0, 0
    for length in range(1, 5):
        for limit in range(1, length + 1):
            f = E.CNF()
            inputs = [f.new() for _ in range(length)]
            outputs = f.unary_sum(inputs, limit)
            projections = set()
            for mask in range(1 << f.n):
                a = [False] + [bool(mask >> (i - 1) & 1) for i in range(1, f.n + 1)]
                assignments += 1
                if not E.first_failed_clauses(f, a, 1):
                    count = sum(a[v] for v in inputs)
                    assert [a[v] for v in outputs] == [count >= i + 1 for i in range(limit)]
                    projections.add(tuple(a[v] for v in inputs))
            assert len(projections) == 1 << length
            trials += 1
    rng = random.Random(7042026)
    larger = 0
    for length in [5, 8, 13, 32, 67, 208]:
        for limit in sorted({1, min(3, length), min(18, length), length}):
            f = E.CNF()
            inputs = [f.new() for _ in range(length)]
            outputs = f.unary_sum(inputs, limit)
            for count in sorted({0, 1, length // 2, length - 1, length}):
                chosen = set(rng.sample(inputs, count))
                a = [False] * (f.n + 1)
                for v in inputs:
                    a[v] = v in chosen
                f.fill_auxiliaries(a)
                assert not E.first_failed_clauses(f, a)
                assert [a[v] for v in outputs] == [count >= i + 1 for i in range(limit)]
                larger += 1
    # AND gates are checked on every input and output truth value.
    and_assignments = 0
    f = E.CNF(); a, b = f.new(), f.new(); c = f.and_literal(a, b)
    for mask in range(8):
        assignment = [False] + [bool(mask >> i & 1) for i in range(3)]
        assert (not E.first_failed_clauses(f, assignment)) == (assignment[c] == (assignment[a] and assignment[b]))
        and_assignments += 1
    return {"small_truncated_totalizer_instances": trials,
            "exhausted_input_plus_auxiliary_assignments": assignments,
            "larger_constructive_count_assignments": larger,
            "and_gate_truth_table_assignments": and_assignments}


def check_shears(terms5, support5):
    checked_maps, checked_lines = 0, 0
    for ring in E.RINGS:
        n = 2
        points = list(itertools.product(range(4), repeat=n))
        dirs = direction_classes(n, ring)
        for t in range(4):
            for columns in itertools.product(range(4), repeat=2):
                images = {p: direct_shear(p, t, columns, ring) for p in points}
                assert len(set(images.values())) == 16
                for p, target in images.items():
                    a, x = bits(p)
                    assert target == point(a, x ^ t ^ linear_image(a, columns), n)
                for (d, u), direction in dirs.items():
                    for base in points:
                        original = line(base, direction, ring)
                        mapped = {images[p] for p in original}
                        target = point(d, E.quotient(u ^ linear_image(d, columns), d), n)
                        assert mapped == line(images[base], target, ring)
                        checked_lines += 1
                checked_maps += 1
    rng = random.Random(202610287)
    normalization_sets, reindexed_directions = 0, 0
    for ring in E.RINGS:
        terms = terms5[ring]
        for _ in range(24):
            fibres = {a: frozenset(rng.sample(range(32), rng.randrange(2, 18))) for a in support5}
            changed, transformation = E.normalize_fibres(fibres, 5)
            t, columns = transformation["t"], transformation["L_columns"]
            assert len(transformation["anchors"]) == 6
            assert all(len(changed[a]) == len(A) for a, A in fibres.items())
            assert all(0 in changed[a] for a in transformation["anchors"])
            for a, A in fibres.items():
                for x in A:
                    mapped = direct_shear(point(a, x, 5), t, columns, ring)
                    assert bits(mapped)[0] == a and bits(mapped)[1] in changed[a]
            before = coverage_from_terms(fibres, terms, 5)
            after = coverage_from_terms(changed, terms, 5)
            predicted = {(d, E.quotient(u ^ linear_image(d, columns), d)) for d, u in before}
            assert after == predicted
            reindexed_directions += len(terms)
            normalization_sets += 1
    return {"all_dimension2_common_affine_tangent_maps": checked_maps,
            "direct_carried_line_checks": checked_lines,
            "dimension5_random_normalized_fibre_systems": normalization_sets,
            "dimension5_direction_reindex_checks": reindexed_directions}


def check_star():
    result = []
    for ring in E.RINGS:
        fibres = {0: frozenset(range(32))}
        fibres.update({a: frozenset({0, a}) for a in range(1, 32)})
        f = E.encode_support(list(range(32)), 32, total=94, dimension=5, ring=ring)
        assignment = E.actual_assignment(f, fibres)
        failed = E.first_failed_clauses(f, assignment)
        assert not failed, failed
        actual = verify_actual_kakeya(fibres, 5, ring)
        assert actual["is_kakeya"] and actual["point_count"] == 94
        # Corrupt one pair gate while preserving member bits: its AND clauses
        # must detect the inconsistency, independently of any solver.
        pair_variable = next(iter(f.pairs.values()))
        changed = list(assignment)
        changed[pair_variable] = not changed[pair_variable]
        assert E.first_failed_clauses(f, changed)
        result.append({"ring": ring, "variables": f.n, "clauses": len(f.cl),
                       "anchors": f.anchors, "all_clauses_satisfied": True,
                       "corrupted_pair_gate_rejected": True, "direct_geometry": actual})
        del f, assignment, changed
        gc.collect()
    return result


def main():
    started = time.monotonic()
    support5 = [0, 1, 2, 4, 7, 8, 11, 12, 15, 16, 17, 18, 19]
    comparisons, terms5 = [], {}
    for n, support in [(2, [0, 1, 2]), (2, [0, 1, 2, 3]), (5, support5)]:
        for ring in E.RINGS:
            direct = direct_line_terms(support, n, ring)
            encoded = encoder_line_terms(support, n, ring)
            assert direct == encoded
            comparisons.append({"dimension": n, "ring": ring, "support": support,
                                "directions": len(direct),
                                "distinct_line_terms": sum(map(len, direct.values())),
                                "literal_ring_geometry_equals_encoder_line_terms": True})
            if n == 5:
                terms5[ring] = direct
    report = {"status": "PASS_EXACT_RING_GEOMETRY_AND_BOOLEAN_REPLAY",
              "line_family_comparisons": comparisons,
              "scope": "Line-term equality covers every membership assignment on each tested support; separate manual proof covers arbitrary supports.",
              "counters": check_totalizers(), "normalization": check_shears(terms5, support5),
              "positive_94_point_stars": check_star(),
              "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                                [HERE / "encode_exact_ring.py", Path(__file__)]},
              "proof_assistant_formalized": False,
              "seconds": round(time.monotonic() - started, 6)}
    (HERE / "EXACT_RING_REPLAY.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
