"""Replay the finite premises and all applications of three analytic obstructions.

The proofs are in SUPPORT10_CLOSURE_PROOF.md and the two rigidity audits.
This is not a proof-assistant formalization or an enumeration of fibre shapes.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent


def rank(points):
    span = {0}
    for point in points:
        span |= {x ^ point for x in tuple(span)}
    return len(span).bit_length() - 1


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must remain enabled.')
    V, W = set(range(8)), {0, 8, 16, 24}
    ordinary, central = V - {0}, W - {0}
    common_neighbour_histograms = []
    four_period_choices = 0
    for w in sorted(central):
        F7 = {w ^ v for v in ordinary}
        F9 = F7 | (central - {w})
        assert len(F7) == 7 and rank(F7) == 4
        assert len(F9) == 9 and rank(F9) == 5
        assert all((a ^ b) not in F9 for a, b in combinations(F9, 2))
        for four in combinations(F7, 4):
            assert rank(four) >= 3
            four_period_choices += 1
        hist = Counter()
        for opposite in combinations(F9, 6):
            neighbours = [x for x in range(32) if all((x ^ y) in F9 for y in opposite)]
            assert len(neighbours) <= 2
            hist[len(neighbours)] += 1
        assert hist == {1: 77, 2: 7}
        common_neighbour_histograms.append(dict(hist))
    for x in ordinary:
        assert rank({x ^ w for w in central}) == 3

    # The three independent directions on an ordinary fibre give disjoint
    # 3-cubes. Check every cube subset and every distribution of five points
    # among the four cosets of its direction space.
    cube_max = [0] * 9
    for mask in range(256):
        A = {x for x in range(8) if mask >> x & 1}
        edges = sum((x ^ y) in {1, 2, 4} for x, y in combinations(A, 2))
        cube_max[len(A)] = max(cube_max[len(A)], edges)
    five_point_max = max(sum(cube_max[k] for k in sizes)
                         for sizes in product(range(6), repeat=4) if sum(sizes) == 5)
    assert cube_max == [0, 0, 1, 2, 4, 5, 7, 9, 12]
    assert five_point_max == 5

    # A centre of size 17 with seven small ordinary neighbours has 56
    # edges in two disjoint 7-regular bipartite graphs on 16 vertices.
    def e(t):
        return min(t * t // 4, 7 * t // 2)
    split_bounds = {k: e(k) + e(17-k) for k in range(2, 9)}
    assert list(split_bounds.values()) == [53, 51, 46, 42, 39, 37, 36]
    assert max(split_bounds.values()) < 56

    source = HERE / 'FULL_SUPPORT10_ROLE_SURVIVORS.json'
    rows = json.loads(source.read_text())
    assert len(rows) == 11
    applications = []
    for row in rows:
        weights = row['weights']
        assert len(weights) == 10 and sum(weights) == 93 and max(weights) <= 18
        assert weights == sorted(weights, reverse=True)
        allowed = row['allowed_central_triplets']
        assert allowed
        proofs = []
        for centers in allowed:
            leaves = list(weights)
            for weight in centers:
                leaves.remove(weight)
            assert len(centers) == 3 and len(leaves) == 7
            options = []
            for i, weight in enumerate(centers):
                neighbours = leaves + [x for j, x in enumerate(centers) if j != i]
                if weight == 16 and sum(x <= 6 for x in leaves) >= 4:
                    options.append('FOUR_PERIODS_FORCE_AFFINE_FOUR_FLAT')
                if weight == 12 and max(neighbours) <= 15:
                    options.append('MANTEL_EQUALITY_CONTRADICTS_COMMON_NEIGHBOURS')
                if weight == 17 and max(leaves) <= 6:
                    options.append('SEVENTEEN_SPLIT_FORCES_FOUR_FLAT_PLUS_ONE')
            assert options, (weights, centers)
            proofs.append({'central_weights': centers, 'ordinary_weights': leaves,
                           'applicable_obstructions': sorted(set(options))})
        applications.append({'weights': weights, 'all_allowed_role_assignments': proofs})

    earlier = json.loads((HERE / 'SUPPORT10_ROLE_SURVIVORS.json').read_text())
    assert {tuple(r['weights']) for r in earlier} <= {tuple(r['weights']) for r in rows}
    result = {
        'status': 'PASS_ALL_ELEVEN_RIGIDITY_APPLICATIONS',
        'full_universe_residual_profiles': len(rows),
        'excluded_profiles': len(applications),
        'earlier_seven_all_included': True,
        'remaining_support10_profiles': 0,
        'four_period_rank_choices_checked': four_period_choices,
        'six_subset_common_neighbour_checks': 3 * 84,
        'common_neighbour_histograms': common_neighbour_histograms,
        'cube_induced_edge_maxima': cube_max,
        'five_point_union_of_cubes_edge_maximum': five_point_max,
        'seventeen_nontrivial_split_bounds': split_bounds,
        'applications': applications,
        'source_survivors_sha256': sha256(source.read_bytes()).hexdigest(),
        'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope': 'Exact finite premises and every surviving weight-role application of the included analytic proofs. The period/flat, Mantel equality, quotient-capacity and support-normalization arguments are hand proofs, not proof-assistant formalization.'
    }
    (HERE / 'SUPPORT10_RIGIDITY_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: result[k] for k in ('status', 'excluded_profiles',
          'remaining_support10_profiles', 'four_period_rank_choices_checked',
          'six_subset_common_neighbour_checks')}, indent=2))


if __name__ == '__main__':
    main()
