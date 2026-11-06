"""Exact M11 support16 checkpoint: partition coverage and assignment duals.

This is a certificate producer.  verify_s16_checkpoint.py checks the integer
duals without running an assignment optimizer.  No exploratory spectrum or
cube-energy cut is used in this checkpoint.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research_round2/structural/m11_support'))
sys.path.insert(0, str(HERE.parent))
from verify_cap11_support import tails, complete_graph_bound, CUTOFFS
from verify_cap11_support_through18 import geometry_certificate
from certify_s17_envelopes import max_assignment

SOURCE = ROOT / 'research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json'
PRIOR = HERE.parent / 'M11_CURRENT_FRONTIER_ROUND3.json'
E3 = (0, 0, 1, 2, 4, 5, 7, 9, 12, 12, 13, 14)


def new_geometry(weights):
    weak = sum(w <= 7 for w in weights[:10])
    lowmass = sum(w*(w-1)//2 for w in weights[10:])
    if lowmass < min(3*weak, 12):
        return 'TEN_HEAVY_WEAK_ENDPOINTS'
    halfmass = sum(w*w//4 for w in weights[9:])
    if halfmass < 12:
        return 'NINE_HEAVY_SUMFREE'
    if halfmass < 16 and sum(E3[w] for w in weights[9:]) < 12:
        return 'NINE_HEAVY_THREE_CUBE_DIRECTIONS'
    return None


def sharpened_envelopes(record):
    support = record['support']
    forced = {a: [] for a in support}
    for d in range(1, 32):
        edges = [(a, a ^ d) for a in support if a < (a ^ d) and (a ^ d) in support]
        if len(edges) == 1:
            for a in edges[0]:
                forced[a].append(d)
    result = {a: {int(w): int(q) for w, q in record['local_upper_envelopes'][str(a)].items()}
              for a in support}
    improvements = []
    for a in support:
        if forced[a] and result[a].get(8) == 70:
            result[a][8] = 64
            improvements.append(dict(residue=a, forced_directions=forced[a],
                                     weight=8, old_bound=70, new_bound=64))
    return result, improvements


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    started = time.monotonic()
    source = json.loads(SOURCE.read_text())
    records = {r['orbit']: r for r in source['records']}
    prior = json.loads(PRIOR.read_text())
    orbit_ids = [o for o in prior['remaining_orbits'] if records[o]['support_size'] == 16]
    assert len(orbit_ids) == 23
    counts = Counter()
    profiles = []
    for tail in tails(15, 82, 11):
        weights = (11,) + tail
        counts['total'] += 1
        for cutoff in CUTOFFS:
            if complete_graph_bound(weights, cutoff) < 992:
                counts['complete_graph_resource'] += 1
                break
        else:
            inherited = geometry_certificate(weights)
            if inherited is not None:
                counts['inherited_geometry'] += 1
            else:
                method = new_geometry(weights)
                if method is None:
                    profiles.append(weights)
                else:
                    counts[method] += 1
    counts['global_residual_profiles'] = len(profiles)
    print(json.dumps(dict(stage='global_partitions', counts=counts,
                         seconds=time.monotonic()-started)), flush=True)
    certs = []
    summaries = []
    all_improvements = []
    for orbit in orbit_ids:
        record = records[orbit]
        envelopes, improvements = sharpened_envelopes(record)
        all_improvements.extend(dict(orbit=orbit, **row) for row in improvements)
        survivor_ids = []
        maximum_cut_bound = -10**9
        for profile_id, weights in enumerate(profiles):
            cost = [[envelopes[a][w] if w >= record['minimum_weights'][str(a)] else -100000
                     for w in weights] for a in record['support']]
            bound, alpha, beta, assignment = max_assignment(cost)
            # Compact integer records; field names are declared in the manifest.
            certs.append([orbit, profile_id, bound, alpha, beta, assignment])
            if bound >= 992:
                survivor_ids.append(profile_id)
            else:
                maximum_cut_bound = max(maximum_cut_bound, bound)
        summaries.append(dict(orbit=orbit, status='OPEN' if survivor_ids else 'CLOSED',
                              surviving_profile_ids=survivor_ids,
                              maximum_excluded_energy_bound=maximum_cut_bound))
        print(json.dumps(dict(stage='support', orbit=orbit,
                              surviving_profiles=len(survivor_ids))), flush=True)
    closed = [r['orbit'] for r in summaries if r['status'] == 'CLOSED']
    assert closed == [177, 187, 198, 201, 202, 203], closed
    remaining = [o for o in prior['remaining_orbits'] if o not in closed]
    manifest = dict(status='PRODUCED_EXACT_CERTIFICATES',
        scope='n5,both rings,total<=93,exact maximum11,pair-active support16',
        source=dict(path=str(SOURCE.relative_to(ROOT)), sha256=sha(SOURCE)),
        prior_frontier=dict(path=str(PRIOR.relative_to(ROOT)), sha256=sha(PRIOR)),
        partition_counts=dict(counts), profiles=profiles,
        certificate_fields=['orbit', 'profile_id', 'maximum_energy', 'row_dual',
                            'column_dual', 'maximizing_assignment'],
        assignment_certificate_count=len(certs), local_envelope_improvements=all_improvements,
        records=summaries, newly_closed_orbits=closed,
        previous_open_affine_support_classes=52,
        remaining_open_affine_support_classes=len(remaining), remaining_orbits=remaining,
        remaining_counts_by_support=dict(sorted(Counter(records[o]['support_size'] for o in remaining).items())),
        cube_energy_profile_exclusions_used=False,
        exploratory_weight9_or_weight11_refinements_used=False,
        seconds=time.monotonic()-started)
    (HERE / 'S16_ASSIGNMENT_DUAL_CERTIFICATES.json').write_text(json.dumps(certs, separators=(',', ':'))+'\n')
    (HERE / 'S16_EXACT_CHECKPOINT.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k: manifest[k] for k in ('status', 'partition_counts',
        'assignment_certificate_count', 'newly_closed_orbits',
        'remaining_open_affine_support_classes', 'seconds')}), flush=True)


if __name__ == '__main__':
    run()
