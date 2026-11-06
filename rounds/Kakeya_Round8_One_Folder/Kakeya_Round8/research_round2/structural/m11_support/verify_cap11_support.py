"""Independent cap11 replay: regenerate partitions, backward allocation, analytic boundary cuts.

No producer output is used to decide an exclusion. Standard-library only.
Run from any working directory. The two frozen M11 inputs are located relative
to this checkpoint's workspace root, or through the optional --source-root.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
import argparse
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
CUTOFFS = (2, 3, 1, 4, 0, 5)


def edge_cap(p, q):
    if min(p, q) == 3 and 5 <= max(p, q) <= 7:
        return max(p, q) + 8
    return min(16, p*q)


def maximal_direction_quota(w):
    power2 = lambda n: n & -n
    if w % 2 == 0:
        return power2(w)-1
    return max(power2(w-1), power2(w+1))-1


@lru_cache(None)
def allocation(w, neighbours, cutoff):
    """Twice the optimal endpoint score, including unused-mass charge."""
    cap = w//2
    budget = w*(w-1)//2
    quota = min(maximal_direction_quota(w), len(neighbours))

    @lru_cache(None)
    def recurse(position, remaining_mass, remaining_maxima):
        if position == len(neighbours):
            return 0
        partner_cap = neighbours[position]
        candidates = []
        for used in range(min(cap, remaining_mass)+1):
            at_maximum = int(used == cap)
            if at_maximum > remaining_maxima:
                continue
            candidates.append(
                2*edge_cap(used, partner_cap)-cutoff*used
                + recurse(position+1, remaining_mass-used,
                          remaining_maxima-at_maximum))
        return max(candidates)

    return cutoff*budget + recurse(
        0, min(budget, cap*len(neighbours)), quota)


def complete_graph_bound(weights, cutoff):
    counts = Counter(weights)
    heavy_caps = tuple(sorted(w//2 for w in weights if w//2 > cutoff))
    result = sum(2*edge_cap(p, q)
                 for i, p in enumerate(heavy_caps) for q in heavy_caps[:i])
    result += sum(multiplicity*allocation(w, heavy_caps, cutoff)
                  for w, multiplicity in counts.items() if w//2 <= cutoff)
    endpoint_losses = []
    for w, multiplicity in counts.items():
        if w//2 <= cutoff:
            continue
        other_caps = list(heavy_caps)
        other_caps.remove(w//2)
        other_caps = tuple(other_caps)
        twice_achievable = allocation(w, other_caps, 0)
        assert twice_achievable % 2 == 0
        loss = sum(edge_cap(w//2, c) for c in other_caps)-twice_achievable//2
        assert loss >= 0
        endpoint_losses.extend([loss]*multiplicity)
    total_loss = max(max(endpoint_losses, default=0),
                     (sum(endpoint_losses)+1)//2)
    return result-2*total_loss


def tails(length, total, upper, prefix=()):
    """All nonincreasing tails, enumerated independently in ascending next part."""
    if length == 0:
        if total == 0:
            yield prefix
        return
    lower = max(2, (total+length-1)//length)
    upper = min(upper, total-2*(length-1))
    for next_weight in range(lower, upper+1):
        yield from tails(length-1, total-next_weight, next_weight,
                         prefix+(next_weight,))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=WORKSPACE)
    args = parser.parse_args()
    started = time.monotonic()
    records = []
    geometric_cuts = []
    for support in range(32, 18, -1):
        summary = dict(support=support, maximum=11, profiles=0,
                       resource_exclusions=0, geometric_exclusions=0,
                       max_resource_certificate_doubled=0)
        cutoff_counts = Counter()
        for tail in tails(support-1, 82, 11):
            weights = (11,)+tail
            assert len(weights) == support and sum(weights) == 93
            assert all(11 >= a >= b >= 2 for a, b in zip(weights, weights[1:]))
            summary['profiles'] += 1
            bounds = []
            for cutoff in CUTOFFS:
                bound = complete_graph_bound(weights, cutoff)
                bounds.append(bound)
                if bound < 992:
                    summary['resource_exclusions'] += 1
                    summary['max_resource_certificate_doubled'] = max(
                        summary['max_resource_certificate_doubled'], bound)
                    cutoff_counts[cutoff] += 1
                    break
            else:
                # Geometry theorem: eight heavy residues miss r>=6 directions;
                # pair caps<=5 force >=4 low pairs per missing direction.
                # P<=31 forces r<=7, and the eight-residue gap forces r=6.
                # The six missing directions lie in a halfspace, so Q<24 cuts.
                low = weights[8:]
                pair_mass = sum(w*(w-1)//2 for w in low)
                halfspace_mass = sum(w*w//4 for w in low)
                assert pair_mass <= 31 and halfspace_mass < 24, (
                    'UNRESOLVED', weights, bounds, pair_mass, halfspace_mass)
                summary['geometric_exclusions'] += 1
                geometric_cuts.append(dict(
                    support=support, weights=weights, resource_bounds=bounds,
                    low_pair_mass=pair_mass,
                    low_halfspace_pair_mass=halfspace_mass,
                    forced_missing_directions=6,
                    required_low_pair_mass=24,
                    method='EIGHT_HEAVY_MISSING_DIRECTIONS'))
        summary['cutoff_histogram'] = dict(sorted(cutoff_counts.items()))
        assert summary['profiles'] == (summary['resource_exclusions']
                                       + summary['geometric_exclusions'])
        records.append(summary)
        print(json.dumps(dict(summary, elapsed_seconds=round(
            time.monotonic()-started, 3))), flush=True)

    frozen = args.source_root / 'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional'
    frontier_path = frozen / 'M11_DIRECTIONAL_FRONTIER.json'
    supports_path = frozen / 'inputs/CAP11_STRUCTURAL_REDUCTION.json'
    frontier = json.loads(frontier_path.read_text())
    supports = json.loads(supports_path.read_text())
    by_orbit = {r['orbit']: r for r in supports['records']}
    prior = set(frontier['remaining_orbits'])
    assert len(prior) == frontier['remaining_affine_support_classes'] == 130
    closed = sorted(orbit for orbit in prior if by_orbit[orbit]['support_size'] >= 19)
    remaining = sorted(prior-set(closed))
    before_counts = Counter(by_orbit[o]['support_size'] for o in prior)
    closed_counts = Counter(by_orbit[o]['support_size'] for o in closed)
    remaining_counts = Counter(by_orbit[o]['support_size'] for o in remaining)
    assert {str(k): v for k, v in sorted(before_counts.items())} == frontier['remaining_counts_by_support']
    assert len(closed) == 59 and len(remaining) == 71
    receipt = dict(
        status='PASS', scope='n5, both rings, total<=93, exact maximum11, pair-active support>=19',
        normalization='Delete singleton fibres, then pad existing pair-active fibres to total93 without exceeding11.',
        proof_obligation_doubled=992,
        total_profiles=sum(r['profiles'] for r in records),
        resource_exclusions=sum(r['resource_exclusions'] for r in records),
        geometric_exclusions=len(geometric_cuts), records=records,
        previous_remaining_support_classes=130,
        new_whole_support_class_exclusions=len(closed),
        remaining_support_classes=len(remaining),
        new_excluded_orbits=closed, remaining_orbits=remaining,
        excluded_counts_by_support=dict(sorted(closed_counts.items())),
        remaining_counts_by_support=dict(sorted(remaining_counts.items())),
        frozen_inputs=[dict(path=str(p.relative_to(args.source_root)),
                            sha256=sha(p), bytes=p.stat().st_size)
                       for p in (frontier_path, supports_path)],
        local_optimization_keys=allocation.cache_info().currsize,
        elapsed_seconds=time.monotonic()-started)
    (HERE/'M11_SUPPORT_GEOMETRIC_CERTIFICATES.json').write_text(
        json.dumps(geometric_cuts, indent=2)+'\n')
    (HERE/'M11_SUPPORT_INDEPENDENT_REPLAY.json').write_text(
        json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({key: receipt[key] for key in (
        'status', 'total_profiles', 'resource_exclusions',
        'geometric_exclusions', 'new_whole_support_class_exclusions',
        'remaining_support_classes', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    run()
