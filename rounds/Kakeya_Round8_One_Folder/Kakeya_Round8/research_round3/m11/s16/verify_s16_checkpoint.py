"""Replay M11 support16 using integer inequalities, without an optimizer.

The partition generator, new geometric decisions, forced-period discovery,
and dual checks are independent of the certificate producer.  The inherited
round2 complete-graph and geometry verifiers remain explicit dependencies.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research_round2/structural/m11_support'))
from verify_cap11_support import complete_graph_bound, CUTOFFS
from verify_cap11_support_through18 import geometry_certificate


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def all_profiles():
    def descend(prefix, slots, mass):
        if slots == 0:
            if mass == 0:
                yield tuple(prefix)
            return
        for value in range(min(prefix[-1], mass-2*(slots-1)), 1, -1):
            rest = mass-value
            if 2*(slots-1) <= rest <= value*(slots-1):
                yield from descend(prefix+[value], slots-1, rest)
    yield from descend([11], 15, 82)


def cube_edge_table():
    one = [-10**6]*9
    for mask in range(256):
        vertices = [x for x in range(8) if (mask >> x) & 1]
        edges = sum(1 for x, y in combinations(vertices, 2)
                    if x ^ y in (1, 2, 4))
        one[len(vertices)] = max(one[len(vertices)], edges)
    total = [0]+[-10**6]*11
    for _ in range(4):
        total = [max(total[w-k]+one[k] for k in range(min(8, w)+1))
                 for w in range(12)]
    assert total == [0, 0, 1, 2, 4, 5, 7, 9, 12, 12, 13, 14]
    return total


def periodic_eight_control():
    counts = Counter()
    for quotient in combinations(range(16), 4):
        fibre = [(x << 1) | bit for x in quotient for bit in (0, 1)]
        pairs = Counter(x ^ y for x, y in combinations(fibre, 2))
        energy = sum(n*n for n in pairs.values())
        assert energy in (64, 112)
        if energy == 112:
            assert sorted(pairs.values()) == [4]*7
        counts[energy] += 1
    assert counts == {64: 1680, 112: 140}
    return dict(sorted(counts.items()))


def independent_geometry(weights, cube_table):
    weak = len([w for w in weights[:10] if w//2 <= 3])
    low_pairs = sum(w*(w-1)//2 for w in weights[10:])
    required = min(4*r+weak*max(0, 3-r) for r in range(32))
    assert required == min(3*weak, 12)
    if low_pairs < required:
        return 'TEN_HEAVY_WEAK_ENDPOINTS'
    low = weights[9:]
    halfspace = sum((w//2)*(w-w//2) for w in low)
    if halfspace < 3*4:
        return 'NINE_HEAVY_SUMFREE'
    if halfspace < 4*4 and sum(cube_table[w] for w in low) < 3*4:
        return 'NINE_HEAVY_THREE_CUBE_DIRECTIONS'
    return None


def verify():
    started = time.monotonic()
    checkpoint = json.loads((HERE / 'S16_EXACT_CHECKPOINT.json').read_text())
    for key in ('source', 'prior_frontier'):
        input_file = ROOT / checkpoint[key]['path']
        assert sha(input_file) == checkpoint[key]['sha256']
    records = {r['orbit']: r for r in json.loads((ROOT / checkpoint['source']['path']).read_text())['records']}
    prior = json.loads((ROOT / checkpoint['prior_frontier']['path']).read_text())
    orbits = [o for o in prior['remaining_orbits'] if records[o]['support_size'] == 16]
    assert len(orbits) == 23
    cube_table = cube_edge_table()
    periodic_counts = periodic_eight_control()
    expected = set()
    counts = Counter()
    for weights in all_profiles():
        assert len(weights) == 16 and sum(weights) == 93 and weights[0] == 11
        counts['total'] += 1
        if any(complete_graph_bound(weights, c) < 992 for c in CUTOFFS):
            counts['complete_graph_resource'] += 1
        elif geometry_certificate(weights) is not None:
            counts['inherited_geometry'] += 1
        else:
            method = independent_geometry(weights, cube_table)
            if method:
                counts[method] += 1
            else:
                expected.add(weights)
    counts['global_residual_profiles'] = len(expected)
    profiles = [tuple(p) for p in checkpoint['profiles']]
    assert len(profiles) == len(set(profiles))
    assert set(profiles) == expected
    assert dict(counts) == checkpoint['partition_counts']
    print(json.dumps(dict(stage='partition_replay', counts=counts)), flush=True)

    envelopes = {}
    improvements = []
    for orbit in orbits:
        record = records[orbit]
        support = set(record['support'])
        unique_edges = {}
        for x, y in combinations(support, 2):
            unique_edges.setdefault(x ^ y, []).append((x, y))
        forced = {a: [] for a in support}
        for d, edges in unique_edges.items():
            if len(edges) == 1:
                for a in edges[0]:
                    forced[a].append(d)
        local = {a: {int(w): int(q) for w, q in record['local_upper_envelopes'][str(a)].items()}
                 for a in record['support']}
        for a in record['support']:
            if forced[a] and local[a].get(8) == 70:
                # A period forces either full energy64 or a cube spectrum.
                # Cube active energy is divisible by16; <=70 therefore <=64.
                local[a][8] = 64
                improvements.append(dict(orbit=orbit, residue=a,
                    forced_directions=sorted(forced[a]), weight=8,
                    old_bound=70, new_bound=64))
        envelopes[orbit] = local
    assert improvements == checkpoint['local_envelope_improvements']

    certs = json.loads((HERE / 'S16_ASSIGNMENT_DUAL_CERTIFICATES.json').read_text())
    assert len(certs) == len(orbits)*len(profiles) == checkpoint['assignment_certificate_count']
    seen = set()
    survivors = {o: [] for o in orbits}
    max_cut = {o: -10**9 for o in orbits}
    inequalities = 0
    for orbit, profile_id, upper, alpha, beta, assignment in certs:
        assert orbit in orbits and 0 <= profile_id < len(profiles)
        assert (orbit, profile_id) not in seen
        seen.add((orbit, profile_id))
        weights = profiles[profile_id]
        record = records[orbit]
        assert all(isinstance(x, int) for x in [upper]+alpha+beta+assignment)
        assert len(alpha) == len(beta) == 16
        assert sorted(assignment) == list(range(16))
        assert sum(alpha)+sum(beta) == upper
        attained = 0
        for i, a in enumerate(record['support']):
            for j, w in enumerate(weights):
                if w < record['minimum_weights'][str(a)]:
                    continue
                assert alpha[i]+beta[j] >= envelopes[orbit][a][w]
                inequalities += 1
            w = weights[assignment[i]]
            attained += envelopes[orbit][a][w] if w >= record['minimum_weights'][str(a)] else -100000
        assert attained == upper
        if upper >= 992:
            assert all(weights[assignment[i]] >= record['minimum_weights'][str(a)]
                       for i, a in enumerate(record['support']))
            survivors[orbit].append(profile_id)
        else:
            max_cut[orbit] = max(max_cut[orbit], upper)
    assert len(seen) == len(orbits)*len(profiles)
    summaries = [dict(orbit=o, status='OPEN' if survivors[o] else 'CLOSED',
                      surviving_profile_ids=survivors[o],
                      maximum_excluded_energy_bound=max_cut[o]) for o in orbits]
    assert summaries == checkpoint['records']
    closed = [o for o in orbits if not survivors[o]]
    assert closed == checkpoint['newly_closed_orbits'] == [177, 187, 198, 201, 202, 203]
    remaining = [o for o in prior['remaining_orbits'] if o not in closed]
    support_counts = dict(sorted(Counter(records[o]['support_size'] for o in remaining).items()))
    assert len(remaining) == 46 and support_counts == {13: 4, 14: 9, 15: 16, 16: 17}
    result = dict(status='PASS',
        scope=checkpoint['scope'], partition_counts=dict(counts),
        exact_assignment_dual_certificates=len(certs),
        valid_assignment_edge_inequalities=inequalities,
        cube_direction_edge_maxima=cube_table,
        normalized_periodic_eight_set_control=periodic_counts,
        local_envelope_improvements=improvements,
        new_whole_affine_support_class_exclusions=closed,
        previous_remaining_affine_support_classes=52,
        remaining_affine_support_classes=46,
        remaining_orbits=remaining, remaining_counts_by_support=support_counts,
        records=[dict(orbit=o, surviving_profile_count=len(survivors[o]),
                      surviving_weight_profiles=[profiles[i] for i in survivors[o]]) for o in orbits],
        full_M11_branch_closed=False, unrestricted_n5_theorem_proved=False,
        inputs=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in
                (HERE/'S16_EXACT_CHECKPOINT.json', HERE/'S16_ASSIGNMENT_DUAL_CERTIFICATES.json')],
        seconds=time.monotonic()-started)
    (HERE/'S16_INDEPENDENT_REPLAY.json').write_text(json.dumps(result, indent=2)+'\n')
    frontier = {key: result[key] for key in ('status',
        'new_whole_affine_support_class_exclusions',
        'previous_remaining_affine_support_classes',
        'remaining_affine_support_classes', 'remaining_orbits',
        'remaining_counts_by_support', 'full_M11_branch_closed',
        'unrestricted_n5_theorem_proved')}
    frontier.update(dimension=5, rings=['Z/4Z', 'F2[epsilon]/(epsilon^2)'],
                    maximum_fibre=11, total_mass_at_most=93,
                    prior_frontier=checkpoint['prior_frontier'],
                    proof='M11_SIX_SUPPORT16_CLASS_EXCLUSIONS.md',
                    verification_receipt='S16_INDEPENDENT_REPLAY.json')
    (HERE/'M11_CURRENT_FRONTIER_AFTER_S16.json').write_text(json.dumps(frontier, indent=2)+'\n')
    print(json.dumps({key: result[key] for key in ('status', 'partition_counts',
        'exact_assignment_dual_certificates', 'valid_assignment_edge_inequalities',
        'new_whole_affine_support_class_exclusions', 'remaining_affine_support_classes',
        'seconds')}), flush=True)


if __name__ == '__main__':
    verify()
