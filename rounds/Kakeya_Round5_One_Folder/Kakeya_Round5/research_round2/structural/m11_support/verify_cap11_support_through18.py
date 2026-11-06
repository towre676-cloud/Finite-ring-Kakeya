"""Complete independent replay of exact-M11 support>=18 exclusions.

The arithmetic recurrence is imported from the independent backward checker,
not the C++ producer. Every partition is regenerated and rechecked here.
"""
from collections import Counter
from pathlib import Path
import argparse
import json
import time

from verify_cap11_support import (
    HERE, WORKSPACE, CUTOFFS, allocation, complete_graph_bound, tails, sha)


def geometry_certificate(weights):
    low8 = weights[8:]
    p8 = sum(w*(w-1)//2 for w in low8)
    q8 = sum(w*w//4 for w in low8)
    common = dict(weights=weights, support=len(weights),
                  low8_pair_mass=p8, low8_halfspace_pair_mass=q8)
    if p8 <= 35 and q8 < 24:
        return dict(common, method='EIGHT_HEAVY_STRICT_HALFSPACE',
                    forced_missing_directions=6, required_low_pair_mass=24)
    p9 = sum(w*(w-1)//2 for w in weights[9:])
    if p9 < 12:
        return dict(common, method='NINE_HEAVY_LIGHT_PAIR_DEFICIT',
                    low9_pair_mass=p9, required_low_pair_mass=12,
                    minimum_missing_directions=3)
    weak_saturated = next((w for w in low8 if w in (6, 7)), None)
    if p8 <= 35 and q8 == 24 and weak_saturated is not None:
        mass = weak_saturated*weak_saturated//4
        max_at_three_ports = 7 if weak_saturated == 6 else 9
        assert mass > max_at_three_ports
        return dict(common, method='EIGHT_HEAVY_SATURATED_PORT_DEFICIT',
                    forced_missing_directions=6, required_low_pair_mass=24,
                    low_fibre_weight=weak_saturated,
                    forced_fibre_pair_mass=mass,
                    maximum_heavy_ports=3,
                    maximum_pair_mass_at_three_ports=max_at_three_ports)
    low10 = weights[10:]
    if all(w == 2 for w in low10):
        weak = sum(w <= 6 for w in weights[:10])
        demand = min(4*r+weak*max(0, 3-r) for r in range(32))
        if len(low10) < demand:
            return dict(common, method='TEN_HEAVY_UNIQUE_EDGE_DEFICIT',
                        weak_heavy_vertices=weak,
                        low10_pair_mass=len(low10),
                        minimum_required_low_pair_mass=demand)
    return None


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, default=WORKSPACE)
    args = parser.parse_args()
    started = time.monotonic()
    rows = []
    geometric = []
    method_counts = Counter()
    for support in range(32, 17, -1):
        row = dict(support=support, maximum=11, profiles=0,
                   resource_exclusions=0, geometric_exclusions=0,
                   max_resource_certificate_doubled=0)
        cutoffs = Counter()
        methods = Counter()
        for tail in tails(support-1, 82, 11):
            weights = (11,)+tail
            assert sum(weights) == 93 and len(weights) == support
            assert all(11 >= a >= b >= 2 for a, b in zip(weights, weights[1:]))
            row['profiles'] += 1
            bounds = []
            for cutoff in CUTOFFS:
                upper = complete_graph_bound(weights, cutoff)
                bounds.append(upper)
                if upper < 992:
                    row['resource_exclusions'] += 1
                    row['max_resource_certificate_doubled'] = max(
                        row['max_resource_certificate_doubled'], upper)
                    cutoffs[cutoff] += 1
                    break
            else:
                cert = geometry_certificate(weights)
                assert cert is not None, ('UNRESOLVED', weights, bounds)
                cert['resource_bounds'] = bounds
                geometric.append(cert)
                methods[cert['method']] += 1
                method_counts[cert['method']] += 1
                row['geometric_exclusions'] += 1
        assert row['profiles'] == row['resource_exclusions']+row['geometric_exclusions']
        row['cutoff_histogram'] = dict(sorted(cutoffs.items()))
        row['geometry_method_histogram'] = dict(sorted(methods.items()))
        rows.append(row)
        print(json.dumps(dict(row, elapsed_seconds=round(
            time.monotonic()-started, 3))), flush=True)

    frozen = args.source_root / 'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional'
    frontier_path = frozen/'M11_DIRECTIONAL_FRONTIER.json'
    support_path = frozen/'inputs/CAP11_STRUCTURAL_REDUCTION.json'
    frontier = json.loads(frontier_path.read_text())
    supports = json.loads(support_path.read_text())
    by_orbit = {r['orbit']: r for r in supports['records']}
    before = set(frontier['remaining_orbits'])
    assert len(before) == frontier['remaining_affine_support_classes'] == 130
    closed = sorted(o for o in before if by_orbit[o]['support_size'] >= 18)
    remaining = sorted(before-set(closed))
    before_counts = Counter(by_orbit[o]['support_size'] for o in before)
    closed_counts = Counter(by_orbit[o]['support_size'] for o in closed)
    remaining_counts = Counter(by_orbit[o]['support_size'] for o in remaining)
    assert {str(k): v for k, v in sorted(before_counts.items())} == frontier['remaining_counts_by_support']
    assert len(closed) == 73 and len(remaining) == 57
    receipt = dict(
        status='PASS',
        scope='n5,both rings,total<=93,exact maximum11,pair-active support>=18',
        necessary_support_upper_bound=17,
        proof_obligation_doubled=992,
        total_profiles=sum(r['profiles'] for r in rows),
        resource_exclusions=sum(r['resource_exclusions'] for r in rows),
        geometric_exclusions=len(geometric),
        geometry_method_histogram=dict(sorted(method_counts.items())),
        records=rows,
        previous_remaining_support_classes=130,
        new_whole_support_class_exclusions=len(closed),
        remaining_support_classes=len(remaining),
        new_excluded_orbits=closed, remaining_orbits=remaining,
        excluded_counts_by_support=dict(sorted(closed_counts.items())),
        remaining_counts_by_support=dict(sorted(remaining_counts.items())),
        support18_additional_closed_orbits=sorted(
            o for o in before if by_orbit[o]['support_size'] == 18),
        frozen_inputs=[dict(path=str(p.relative_to(args.source_root)),
                            sha256=sha(p), bytes=p.stat().st_size)
                       for p in (frontier_path, support_path)],
        local_optimization_keys=allocation.cache_info().currsize,
        elapsed_seconds=time.monotonic()-started)
    assert receipt['total_profiles'] == 121336
    assert receipt['resource_exclusions'] == 121147
    assert receipt['geometric_exclusions'] == 189
    (HERE/'M11_SUPPORT_THROUGH18_GEOMETRIC_CERTIFICATES.json').write_text(
        json.dumps(geometric, indent=2)+'\n')
    (HERE/'M11_SUPPORT_THROUGH18_INDEPENDENT_REPLAY.json').write_text(
        json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: receipt[k] for k in (
        'status', 'total_profiles', 'resource_exclusions',
        'geometric_exclusions', 'new_whole_support_class_exclusions',
        'remaining_support_classes', 'elapsed_seconds')}), flush=True)


if __name__ == '__main__':
    run()
