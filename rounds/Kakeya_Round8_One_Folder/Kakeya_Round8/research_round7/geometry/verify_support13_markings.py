#!/usr/bin/env python3
"""Group the complete marked S13 catalogue into affine support geometries.

All point-mark changes are supplied with explicit invertible affine maps.
In particular this does not silently move a largest fibre to a different
vertex while retaining a previously certified distinguished-hub instance.
"""
import hashlib
import json
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
QUEUE = ROOT / 'research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json'
OLD = ROOT / ('research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/'
              'late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json')
FRONTIER = ROOT / 'research_round3/m11/s16/M11_CURRENT_FRONTIER_AFTER_S16.json'


def mask(points):
    return sum(1 << x for x in points)


def apply(columns, x):
    result = 0
    for i in range(5):
        if x >> i & 1:
            result ^= columns[i]
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    cases = json.loads(QUEUE.read_text())['cases']
    assert len(cases) == 55
    marked = {case['nonzero_support_mask']: case for case in cases}
    assert len(marked) == 55
    old = [record for record in json.loads(OLD.read_text())['records']
           if record['support_size'] == 13 and
           {a ^ b for a in record['support'] for b in record['support']} == set(range(32))]
    assert len(old) == 13
    all_supports = [case['support'] for case in cases] + [record['support'] for record in old]
    inputs = sorted({mask(x ^ v for x in support if x != v)
                     for support in all_supports for v in support})
    source = HERE / 'marking_map.cpp'
    with tempfile.TemporaryDirectory(prefix='kakeya_s13_markings_') as temp:
        binary = Path(temp) / 'marking_map'
        subprocess.run(['g++', '-O2', '-std=c++17', str(source), '-o', str(binary)], check=True)
        result = subprocess.run([str(binary)], input=''.join(f'{x}\n' for x in inputs),
                                text=True, capture_output=True, check=True)
    canonical = {}
    for line in result.stdout.splitlines():
        values = list(map(int, line.split()))
        assert len(values) == 7
        source_mask, target_mask, *columns = values
        assert source_mask not in canonical
        assert {apply(columns, x) for x in range(32)} == set(range(32))
        assert all(apply(columns, a ^ b) == apply(columns, a) ^ apply(columns, b)
                   for a in range(32) for b in range(32))
        assert mask(apply(columns, x) for x in range(1, 32) if source_mask >> x & 1) == target_mask
        assert target_mask in marked
        canonical[source_mask] = (target_mask, columns)
    assert set(canonical) == set(inputs)
    for key in marked:
        assert canonical[key][0] == key

    def images(support):
        return {canonical[mask(x ^ v for x in support if x != v)][0] for v in support}

    group_images = {min(images(record['support'])): (record, images(record['support'])) for record in old}
    assert len(group_images) == len(old)
    assert set().union(*(values for record, values in group_images.values())) == set(marked)
    assert sum(len(values) for record, values in group_images.values()) == len(marked)

    remaining_orbits = set(json.loads(FRONTIER.read_text())['remaining_orbits'])
    groups = []
    mark_records = []
    for group_key, (record, group) in sorted(group_images.items()):
        representative = record['support']
        transports = []
        for vertex in representative:
            shifted = mask(x ^ vertex for x in representative if x != vertex)
            target, columns = canonical[shifted]
            assert {apply(columns, x ^ vertex) for x in representative} == set(marked[target]['support'])
            transports.append({'largest_vertex_in_representative': vertex,
                               'target_marked_nonzero_mask': target,
                               'linear_columns_after_translation': columns,
                               'formula': 'target(x)=L(x XOR largest_vertex)'})
        for target in sorted(group):
            assert images(marked[target]['support']) == group
            mark_records.append({'marked_nonzero_mask': target,
                                 'unmarked_affine_orbit_id': record['orbit'],
                                 'unmarked_representative': representative,
                                 'all_marked_cases_in_this_unmarked_class': sorted(group),
                                 'exact_maximum11_still_open_in_inherited_frontier': record['orbit'] in remaining_orbits})
        groups.append({'unmarked_affine_orbit_id': record['orbit'],
                       'representative_support': representative,
                       'representative_full_mask': record['mask'],
                       'marked_case_count': len(group),
                       'marked_nonzero_masks': sorted(group),
                       'all_thirteen_hub_choices': transports,
                       'exact_maximum11_still_open_in_inherited_frontier': record['orbit'] in remaining_orbits})

    open_groups = [g for g in groups if g['exact_maximum11_still_open_in_inherited_frontier']]
    assert sorted(g['unmarked_affine_orbit_id'] for g in open_groups) == [105, 109, 110, 111]
    result = {'status': 'PASS_COMPLETE_55_MARKED_TO_13_UNMARKED_AFFINE_SUPPORTS',
              'support_size': 13, 'marked_case_count': 55, 'unmarked_affine_class_count': 13,
              'exact_maximum11_remaining_affine_class_count': len(open_groups),
              'exact_maximum11_remaining_marked_case_count': sum(g['marked_case_count'] for g in open_groups),
              'maximum11_remaining_affine_ids': [105, 109, 110, 111],
              'verified_linear_maps': len(canonical),
              'verified_hub_transports': sum(len(g['all_thirteen_hub_choices']) for g in groups),
              'scope_note': 'A whole unmarked support is excluded only when every listed marked case has a certificate covering the claimed maximum range. A certified hub cannot be moved arbitrarily.',
              'max11_dependency_note': 'The inherited exact-maximum11 frontier reduces thirteen affine support13 geometries to four. This map proves equivalences, not those inherited exclusions.',
              'new_exclusions_credited': 0,
              'groups': sorted(groups, key=lambda g: g['unmarked_affine_orbit_id']),
              'marked_cases': sorted(mark_records, key=lambda g: g['marked_nonzero_mask']),
              'source_hashes': {str(p.relative_to(ROOT)): sha(p) for p in
                               [source, Path(__file__).resolve(), QUEUE, OLD, FRONTIER]},
              'seconds': round(time.monotonic() - start, 6)}
    (HERE / 'SUPPORT13_MARKING_MAP.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('groups', 'marked_cases', 'source_hashes')}, indent=2))
    print('GROUPS:', [(g['unmarked_affine_orbit_id'], g['marked_case_count'],
                       g['marked_nonzero_masks']) for g in result['groups']])


if __name__ == '__main__':
    main()
