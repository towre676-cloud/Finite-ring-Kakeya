"""Finite checks accompanying the analytic V union W support-eleven proof.

No SAT solver, optimizer, spectrum census or previous exclusion ledger is used.
The optional catalogue classification reads the imported support list and gives
explicit translated complementary subspaces for every matching marked class.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def span(generators):
    out = {0}
    for x in generators:
        out |= {x ^ y for y in out}
    return out


def rank(generators):
    return len(span(generators)).bit_length() - 1


def cube_bounds():
    best = [-1] * 9
    for mask in range(256):
        points = [x for x in range(8) if mask >> x & 1]
        edges = sum((a ^ b) in (1, 2, 4) for a, b in combinations(points, 2))
        best[len(points)] = max(best[len(points)], edges)
    dp = [0] + [-1000] * 32
    for _ in range(4):
        nxt = [-1000] * 33
        for n in range(33):
            for t in range(min(8, n) + 1):
                nxt[n] = max(nxt[n], dp[n - t] + best[t])
        dp = nxt
    assert best == [0, 0, 1, 2, 4, 5, 7, 9, 12]
    assert dp[:6] == [0, 0, 1, 2, 4, 5]
    return {"one_cube": best, "four_cubes_weights_0_to_5": dp[:6]}


def subspaces_inside(points, dimension):
    return sorted({tuple(sorted(span(g))) for g in combinations(sorted(points - {0}), dimension)
                   if rank(g) == dimension and span(g) <= points})


def classify(support):
    support = set(support)
    for origin in sorted(support):
        shifted = {x ^ origin for x in support}
        vspaces = subspaces_inside(shifted, 3)
        wspaces = subspaces_inside(shifted, 2)
        for vt in vspaces:
            for wt in wspaces:
                v, w = set(vt), set(wt)
                if v & w == {0} and v | w == shifted:
                    return {"origin": origin, "V": list(vt), "W": list(wt)}
    return None


def verify_geometry(v, w):
    assert len(v) == 8 and len(w) == 4 and v & w == {0}
    assert span(v) == v and span(w) == w and span(v | w) == set(range(32))
    ordinary, centres = v - {0}, w - {0}
    support = v | w
    multiplicity = Counter(a ^ b for a, b in combinations(sorted(support), 2))
    unique = {frozenset((a, b)) for a, b in combinations(sorted(support), 2)
              if multiplicity[a ^ b] == 1}
    assert unique == {frozenset((a, b)) for a in ordinary for b in centres}
    assert len(unique) == 21
    for d in centres:
        edges = {frozenset((a, b)) for a, b in combinations(sorted(support), 2) if a ^ b == d}
        others = centres - {d}
        assert edges == {frozenset((0, d)), frozenset(others)}
    for x in ordinary:
        assert rank(x ^ w for w in centres) == 3
    for c in centres:
        f = {c ^ x for x in ordinary}
        ell = v | {c ^ x for x in v}
        assert len(ell) == 16 and rank(f) == 4
        for subset in combinations(f, 5):
            assert span(subset) == ell
        assert (centres - {c}).isdisjoint(ell)
        # The component on L has the two V-cosets as sides and all cross
        # edges except the matching x <-> c+x. Translation gives its mate.
        side0, side1 = v, ell - v
        for a, b in combinations(ell, 2):
            expected = ((a in side0) != (b in side0)) and (a ^ b != c)
            assert ((a ^ b) in f) == expected
        assert not any((a ^ b) in f for a in ell for b in set(range(32)) - ell)
    return {"unique_edges": 21, "direction_multiplicities": dict(sorted(Counter(multiplicity.values()).items())),
            "centres": sorted(centres), "ordinary": sorted(ordinary), "five_period_subsets_checked": 3 * 21}


def verify_budget():
    # With centre minimum a in [8,11], two ordinary weights >=16 or one
    # ordinary weight 32 are impossible. All seven ordinary weights >=8.
    assert all(3 * a + 74 > 93 and 3 * a + 82 > 93 for a in range(8, 12))
    assert 6 * 4 + 2 == 26 > 9 * 9 // 4
    assert all(3 * a + 66 > 93 for a in (10, 11))
    assert 7 * 4 == 28 > 27
    assert 3 * 12 + 7 * 8 + 2 == 94
    assert 32 + 32 + 16 + 7 * 2 + 2 == 96
    assert 32 + 16 + 16 + 7 * 5 + 2 == 101
    assert 3 * 16 + 7 * 6 + 2 == 92
    # Exhaust all ways to spend at most one point above the resulting
    # baseline. The final proof covers all twelve possibilities, including
    # the total-92 case; no padding argument is needed.
    baseline = [16] * 3 + [6] * 7 + [2]
    profiles = [baseline] + [baseline[:i] + [baseline[i] + 1] + baseline[i + 1:] for i in range(11)]
    for profile in profiles:
        centres, ordinary, origin = profile[:3], profile[3:10], profile[10]
        assert sum(c == 16 for c in centres) >= 2
        assert sum(w == 6 for w in ordinary) >= 6
        assert max(centres) <= 17 and origin <= 3
        assert (origin // 2) * max(c // 2 for c in centres) <= 8 < 16
    return {"budget_baseline": 92, "slack_allocations_checked": len(profiles)}


def main():
    if not __debug__:
        raise SystemExit("Run without -O")
    v = set(range(8)); w = {0, 8, 16, 24}
    geometry = verify_geometry(v, w)
    g = [t * t // 4 - max(0, t - 8) for t in range(17)]
    splits = [g[t] + g[11 - t] for t in range(6)]
    assert splits == [27, 23, 20, 18, 16, 15]
    assert max(splits) == 27
    source = ROOT / 'research_round6/imported_claude_round4/data/orbits_all.txt'
    matches = []
    candidate_count = 0
    for line in source.read_text().splitlines():
        k, mask, stabilizer, covering = map(int, line.split())
        if k != 10 or not covering:
            continue
        candidate_count += 1
        support = [0] + [x for x in range(1, 32) if mask >> x & 1]
        witness = classify(support)
        if witness:
            verify_geometry(set(witness['V']), set(witness['W']))
            matches.append({"mask": mask, "support": support, "stabilizer": stabilizer, "witness": witness})
    assert candidate_count == 13
    assert [r['mask'] for r in matches] == [8481174, 286331166, 2172748182]
    result = {"status": "PASS", "theorem": "No at-most-93-point Kakeya set has pair-active support affine-equivalent to V union W, dimensions 3 and 2, complementary in F2^5",
              "maximum_fibre_hypothesis": None, "rings": ["Z/4Z", "F2[epsilon]/epsilon^2"],
              "canonical_geometry": geometry, "eleven_point_component_split_bounds": splits,
              "cube_bounds": cube_bounds(), "budget": verify_budget(),
              "marked_catalogue_candidates": candidate_count, "matching_marked_cases": matches,
              "catalogue_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "formalized_in_proof_assistant": False}
    target = HERE / 'SUPPORT11_COMPLEMENTARY_SUBSPACES_REPLAY.json'
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({"status": result['status'], "matching_marked_masks": [r['mask'] for r in matches],
                      "scope": result['theorem']}, indent=2))


if __name__ == '__main__':
    main()
