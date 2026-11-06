"""Independent finite check of the support-10, weight-12 centre obstruction.

This is not a SAT search. It enumerates all 84 six-subsets of the nine allowed
differences and all 32 possible common neighbours. The accompanying proof
derives the obstruction analytically from Mantel's equality case.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json


def main():
    here = Path(__file__).resolve().parent
    space = range(32)
    V = set(range(8))
    w, u = 8, 16
    W = {0, w, u, w ^ u}
    B = {w ^ v for v in V if v != 0}
    E = W - {0, w}
    F = B | E
    assert sorted(F) == [9, 10, 11, 12, 13, 14, 15, 16, 24]
    assert len(F) == 9 and 0 not in F
    assert all((a ^ b) not in F for a in F for b in F)

    overlap = {}
    for z in space:
        intersection = sorted(a for a in F if (a ^ z) in F)
        overlap[z] = intersection
        if z == 0:
            assert len(intersection) == 9
        elif z in V:
            assert set(intersection) == {w ^ v for v in V - {0, z}}
            assert len(intersection) == 6
        else:
            assert len(intersection) <= 2

    rows = []
    for Y_tuple in combinations(sorted(F), 6):
        Y = set(Y_tuple)
        # Direct adjacency test in the full Cayley graph. No earlier computed
        # overlaps or imported census are used to obtain these neighbours.
        neighbours = [x for x in space if all((x ^ y) in F for y in Y)]
        if Y <= B:
            missing = next(iter(B - Y))
            predicted = {0, missing ^ w}
        else:
            predicted = {0}
        assert set(neighbours) == predicted
        rows.append({'six_vertices': list(Y_tuple), 'common_neighbours': neighbours})

    histogram = Counter(len(row['common_neighbours']) for row in rows)
    assert len(rows) == 84
    assert histogram == {1: 77, 2: 7}
    assert max(histogram) == 2
    result = {
        'status': 'PASS_COMMON_NEIGHBOUR_BOUND_TWO',
        'dimension': 5,
        'V': sorted(V), 'W': sorted(W), 'w': w, 'u': u,
        'difference_set_F': sorted(F), 'F_is_sum_free': True,
        'six_subsets_checked': len(rows),
        'common_neighbour_count_histogram': dict(sorted(histogram.items())),
        'maximum_common_neighbours': 2,
        'translate_overlap_sets': overlap,
        'all_six_subsets_and_common_neighbours': rows,
        'analytic_corollary': 'For any 12-set A in F_2^5, sum_{d in F} p_A(d) <= 35. Hence p_A(d)>=4 for all nine d in F is impossible.',
        'analytic_corollary_reason': 'Triangle freeness gives Mantel bound 36. Equality would give K_6,6, whose six vertices on one side would have six common neighbours, contradicting the verified bound two after translating a vertex on the other side to zero.',
        'scope': 'The finite check proves the stated common-neighbour bound for this explicit F. The accompanying hand proof gives GL_5(F_2) invariance, the structural derivation and the Mantel equality argument. No assertion about unavailable CNF files or complete Kakeya strata is made here.',
        'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    output = here/'SUPPORT10_MANTEL_COMMON_NEIGHBOUR_REPLAY.json'
    output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in (
        'status', 'six_subsets_checked', 'common_neighbour_count_histogram',
        'maximum_common_neighbours', 'analytic_corollary')}, indent=2))


if __name__ == '__main__':
    main()
