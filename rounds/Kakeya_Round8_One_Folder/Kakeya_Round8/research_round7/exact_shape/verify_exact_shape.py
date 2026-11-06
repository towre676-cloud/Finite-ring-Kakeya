#!/usr/bin/env python3
"""Finite controls for the census-free exact-shape relaxation.

These controls accompany, rather than replace, the written one-way proof.
They make no new dimension-five support exclusion without a checked proof.
"""
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

from encode_exact_shape import (CNF, encode_support, extend_assignment,
                                quotient_representatives, unsatisfied_clauses)

HERE = Path(__file__).resolve().parent


def pair_set(fibre, direction):
    return {min(x, x ^ direction) for x in fibre if x ^ direction in fibre}


def sumset(left, right):
    return {x ^ y for x in left for y in right}


def necessary_semantics(fibres, maximum, hub_min, total, dimension,
                        normalized=True):
    size = 1 << dimension
    if normalized and not all(0 in A for A in fibres.values()):
        return False
    if not all(2 <= len(A) <= maximum for A in fibres.values()):
        return False
    if not hub_min <= len(fibres[0]) <= maximum:
        return False
    if any(len(A) > len(fibres[0]) for A in fibres.values()):
        return False
    if sum(map(len, fibres.values())) > total:
        return False
    for d in range(1, size):
        capacity = 0
        for a, b in itertools.combinations(sorted(fibres), 2):
            if a ^ b == d:
                capacity += len(sumset(pair_set(fibres[a], d), pair_set(fibres[b], d)))
        if capacity < size // 2:
            return False
    return True


def gate_controls():
    # Both truth directions of the elementary gates, including false output.
    and_rows = 0
    f = CNF()
    left, right = f.new(), f.new()
    out = f.and_gate(left, right)
    for a, b, c in itertools.product((False, True), repeat=3):
        assignment = {left: a, right: b, out: c}
        assert (not unsatisfied_clauses(f, assignment)) == (c == (a and b))
        and_rows += 1
    f = CNF()
    inputs = [f.new() for _ in range(16)]
    out = f.or_gate(inputs)
    or_rows = 0
    for bits in range(1 << 16):
        assignment = {literal: bool(bits >> i & 1) for i, literal in enumerate(inputs)}
        for value in (False, True):
            assignment[out] = value
            assert (not unsatisfied_clauses(f, assignment)) == (value == bool(bits))
            or_rows += 1

    # For each merge, fixing honest child prefixes must directly force every
    # output bit. No solver or assumed uniqueness of extension is used.
    merge_rows = 0
    for nl in range(1, 9):
        for nr in range(1, 9):
            for limit in range(1, nl + nr + 1):
                la, lb, no = min(nl, limit), min(nr, limit), min(nl + nr, limit)
                for a in range(nl + 1):
                    for b in range(nr + 1):
                        forced = {}
                        for i in range(la + 1):
                            for j in range(lb + 1):
                                if 0 < i + j <= no and (i == 0 or a >= i) and (j == 0 or b >= j):
                                    assert forced.get(i + j, True) is True
                                    forced[i + j] = True
                                if i + j < no and (i == la or a < i + 1) and (j == lb or b < j + 1):
                                    assert forced.get(i + j + 1, False) is False
                                    forced[i + j + 1] = False
                        assert forced == {k: a + b >= k for k in range(1, no + 1)}
                        merge_rows += 1
    return {'and_truth_rows': and_rows, 'sixteen_input_or_truth_rows': or_rows,
            'truncated_totalizer_merge_prefix_cases': merge_rows}


def main():
    start = time.monotonic()
    controls = gate_controls()
    # Every pair-active normalized fibre in F2^2, every support containing0.
    shapes = [{x for x in range(4) if mask >> x & 1}
              for mask in range(16) if mask & 1 and mask.bit_count() >= 2]
    small_cases = feasible_families = budget9_feasible = 0
    minimum = None
    for outside_mask in range(8):
        support = [0] + [i + 1 for i in range(3) if outside_mask >> i & 1]
        free = encode_support(support, 4, total=16, dimension=2)
        tight = encode_support(support, 4, total=9, dimension=2)
        for selected in itertools.product(shapes, repeat=len(support)):
            fibres = dict(zip(support, selected))
            expected = necessary_semantics(fibres, 4, 2, 16, 2)
            actual = not unsatisfied_clauses(free, extend_assignment(free, fibres))
            assert actual == expected
            expected_tight = necessary_semantics(fibres, 4, 2, 9, 2)
            actual_tight = not unsatisfied_clauses(tight, extend_assignment(tight, fibres))
            assert actual_tight == expected_tight
            if actual:
                feasible_families += 1
                weight = sum(map(len, selected))
                minimum = weight if minimum is None else min(weight, minimum)
            budget9_feasible += actual_tight
            small_cases += 1
    assert small_cases == 3584 and minimum == 10 and budget9_feasible == 0

    # Algebraically quotient representatives are the kernel of one pivot bit.
    quotient_checks = 0
    for d in range(1, 32):
        representatives = quotient_representatives(d, 32)
        assert len(representatives) == 16
        assert all(x ^ y in representatives for x in representatives for y in representatives)
        assert {min(x, x ^ d) for x in range(32)} == set(representatives)
        quotient_checks += 1

    # Independent translations preserve the exact edge capacities, even
    # though they need not preserve the covered labels themselves.
    rng = random.Random(731337)
    translation_checks = 0
    for _ in range(80):
        A = set(rng.sample(range(32), rng.randrange(2, 33)))
        B = set(rng.sample(range(32), rng.randrange(2, 33)))
        a, b = rng.choice(sorted(A)), rng.choice(sorted(B))
        shifted_A, shifted_B = {x ^ a for x in A}, {x ^ b for x in B}
        assert 0 in shifted_A and 0 in shifted_B
        for d in range(1, 32):
            before = sumset(pair_set(A, d), pair_set(B, d))
            after = sumset(pair_set(shifted_A, d), pair_set(shifted_B, d))
            shift = min(a ^ b, (a ^ b) ^ d)
            assert after == {x ^ shift for x in before}
            translation_checks += 1

    # The actual 94-point star is accepted; the exact93 budget rejects only
    # the budget unit, with all point/weight/pair/sumset/coverage gates true.
    star = {0: set(range(32))}
    star.update({v: {0, v} for v in range(1, 32)})
    assert sum(map(len, star.values())) == 94
    f94 = encode_support(list(range(32)), 32, hub_min=32, total=94)
    assert not unsatisfied_clauses(f94, extend_assignment(f94, star))
    star_metadata = f94.exact_shape_metadata
    almost_star = {v: set(A) for v, A in star.items()}
    almost_star[0].remove(31)
    f94_relaxed_hub = encode_support(list(range(32)), 32, total=94)
    assert unsatisfied_clauses(f94_relaxed_hub, extend_assignment(f94_relaxed_hub, almost_star))
    del f94_relaxed_hub, f94
    f93 = encode_support(list(range(32)), 32, hub_min=32, total=93)
    violations = unsatisfied_clauses(f93, extend_assignment(f93, star))
    assert len(violations) == 1 and len(f93.cl[violations[0]]) == 1
    del f93

    representative = [0, 1, 2, 4, 7, 8, 10, 11, 12, 16, 17, 19, 20]
    f13 = encode_support(representative, 18)
    receipt = {'status': 'PASS_DIRECT_SHAPE_AND_EXACT_EDGE_CARDINALITY_ENCODER_CONTROLS',
               **controls,
               'binary2_normalized_fibre_families_exhausted': small_cases,
               'binary2_feasible_families_at_total16': feasible_families,
               'binary2_minimum_relaxation_weight': minimum,
               'binary2_feasible_families_at_total9': budget9_feasible,
               'binary5_quotient_representation_checks': quotient_checks,
               'independent_translation_sumset_identities_checked': translation_checks,
               'actual_94_point_star_accepted': True,
               '94_point_star_against_budget93_rejected_only_by_budget': True,
               '93_point_almost_star_rejected_without_hub_lower_bound': True,
               'star_formula': star_metadata,
               'sample_support13_formula': f13.exact_shape_metadata,
               'source_sha256': hashlib.sha256((HERE / 'encode_exact_shape.py').read_bytes()).hexdigest(),
               'verifier_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'spectrum_census_dependency': False,
               'new_dimension5_support_exclusions_credited': 0,
               'seconds': round(time.monotonic() - start, 6),
               'trust_note': 'Finite controls plus written one-way proof, not full formal verification.'}
    (HERE / 'EXACT_SHAPE_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
