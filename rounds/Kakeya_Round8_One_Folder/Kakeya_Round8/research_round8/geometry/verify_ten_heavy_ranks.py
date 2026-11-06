#!/usr/bin/env python3
"""Complete normalized ten-point classification and rank-bridge controls."""
from collections import Counter, defaultdict
from itertools import combinations
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASKS = (377850134, 411136406, 671697334, 2185856310)


def span(generators):
    result = {0}
    for vector in generators:
        result |= {x ^ vector for x in result}
    return result


def differences(points):
    return Counter(a ^ b for a, b in combinations(points, 2))


def classify(points):
    points = set(points)
    counts = differences(points)
    assert len(points) == 10 and set(counts) == set(range(1, 32))
    assert Counter(counts.values()) == Counter({1: 24, 3: 7})
    W = {0} | {d for d, multiplicity in counts.items() if multiplicity == 3}
    assert len(W) == 8 and span(W) == W
    cosets = defaultdict(set)
    for point in points:
        cosets[min(point ^ w for w in W)].add(point)
    assert sorted(map(len, cosets.values())) == [1, 1, 1, 7]
    thick = next(values for values in cosets.values() if len(values) == 7)
    full_coset = {next(iter(thick)) ^ w for w in W}
    missing = full_coset - thick
    assert len(missing) == 1
    centre = next(iter(missing))
    translated = {x ^ centre for x in points}
    U = {0} | (translated - W)
    assert len(U) == 4 and span(U) == U and W & U == {0}
    assert translated == (W | U) - {0}
    rank5, other7 = sorted(centre ^ u for u in U if u), sorted(centre ^ w for w in W if w)
    forced_spans = {}
    for point in points:
        forced = [point ^ other for other in points
                  if point != other and counts[point ^ other] == 1]
        actual = span(forced)
        if point in rank5:
            assert len(forced) == 9 and len(actual) == 32
        else:
            w = point ^ centre
            expected = span(U | {w})
            assert len(forced) == 3 and actual == expected and len(actual) == 8
            assert actual & W == {0, w}
            assert all((point ^ other) not in actual for other in other7 if other != point)
        forced_spans[str(point)] = sorted(actual)
    for selected in combinations(W - {0}, 4):
        assert len(differences(selected)) < 7
    return {'heavy_residues': sorted(points), 'missing_centre': centre,
            'W': sorted(W), 'U': sorted(U), 'forced_rank5_residues': rank5,
            'seven_residues_at_least_five_rank_ge4': other7,
            'minimum_rank_ge4_in_seven': 5,
            'forced_positive_direction_spans': forced_spans}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    basis = {0, 1, 2, 4, 8, 16}
    additional = sorted(set(range(32)) - basis)
    normalized, covers = 0, []
    for tail in combinations(additional, 4):
        points = basis | set(tail)
        normalized += 1
        if len(differences(points)) == 31:
            covers.append(classify(points))
    assert normalized == 14950 and len(covers) == 80
    cases = []
    for mask in MASKS:
        support = [0] + [v for v in range(1, 32) if (mask >> v) & 1]
        assert len(support) == 13
        patterns = []
        for tail in combinations(support[1:], 9):
            heavy = {0, *tail}
            if len(differences(heavy)) == 31:
                pattern = classify(heavy)
                pattern['light_residues'] = sorted(set(support) - heavy)
                pattern['distinguished_hub_component'] = 'U' if 0 in pattern['forced_rank5_residues'] else 'W'
                patterns.append(pattern)
        cases.append({'marked_nonzero_mask': mask, 'support': support,
                      'ten_heavy_patterns': patterns, 'pattern_count': len(patterns)})
    assert [row['pattern_count'] for row in cases] == [4, 6, 1, 2]
    result = {'status': 'PASS_COMPLETE_TEN_POINT_DIFFERENCE_COVER_STRUCTURE_AND_RANK_BRIDGE',
              'normalized_sets_checked': normalized,
              'normalized_difference_covers': len(covers),
              'complete_normalization_argument': 'Every difference cover has affine rank5 and contains an affine basis of6 points.',
              'analytic_rank_lemma_uses_no_spectrum_census': True,
              'new_unsat_exclusions_claimed': 0,
              'normalized_cover_decompositions': covers, 'marked_support_cases': cases,
              'source_hashes': {str(path.relative_to(ROOT)): sha(path) for path in (
                  Path(__file__), HERE / 'TEN_HEAVY_RANK_CONSEQUENCES.md')},
              'seconds': round(time.monotonic() - started, 6)}
    (HERE / 'TEN_HEAVY_RANK_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: value for k, value in result.items()
                      if k not in ('normalized_cover_decompositions', 'marked_support_cases')}, indent=2))


if __name__ == '__main__':
    main()
