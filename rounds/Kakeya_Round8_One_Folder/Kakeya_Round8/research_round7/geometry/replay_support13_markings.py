#!/usr/bin/env python3
"""Read-only replay of the frozen affine marked-support transport map.

The producer records timing metadata, so this verifier never rewrites its
map. It checks every explicit affine witness and the complete55-case
partition directly. No canonicalization executable needs to be trusted
for these equivalence witnesses.
"""
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def apply(columns, value):
    result = 0
    for i in range(5):
        if value >> i & 1:
            result ^= columns[i]
    return result


def main():
    start = time.monotonic()
    path = HERE / 'SUPPORT13_MARKING_MAP.json'
    original_hash = sha(path)
    data = json.loads(path.read_text())
    assert data['status'] == 'PASS_COMPLETE_55_MARKED_TO_13_UNMARKED_AFFINE_SUPPORTS'
    for relative, digest in data['source_hashes'].items():
        assert sha(ROOT / relative) == digest, relative
    queue = json.loads((ROOT / 'research_round6/next_frontier/SUPPORT13_CASE_QUEUE.json').read_text())
    cases = {row['nonzero_support_mask']: row for row in queue['cases']}
    assert len(cases) == 55 and len(data['groups']) == 13
    old_path = ROOT / ('research_sources/extracted/Kakeya_Reconciled_Proofs_2026-10-27/'
                       'late_parallel_2214/extracted/m11_directional/inputs/CAP11_STRUCTURAL_REDUCTION.json')
    old = {row['orbit']: row for row in json.loads(old_path.read_text())['records']}
    frontier = json.loads((ROOT / 'research_round3/m11/s16/M11_CURRENT_FRONTIER_AFTER_S16.json').read_text())
    remaining = set(frontier['remaining_orbits'])
    all_targets, all_ids = [], []
    verified = 0
    for group in data['groups']:
        orbit = group['unmarked_affine_orbit_id']
        all_ids.append(orbit)
        support = group['representative_support']
        assert support == old[orbit]['support'] and len(support) == 13
        assert group['representative_full_mask'] == sum(1 << x for x in support)
        assert group['exact_maximum11_still_open_in_inherited_frontier'] == (orbit in remaining)
        transports = group['all_thirteen_hub_choices']
        assert len(transports) == 13
        assert {row['largest_vertex_in_representative'] for row in transports} == set(support)
        targets = set()
        for row in transports:
            vertex = row['largest_vertex_in_representative']
            columns = row['linear_columns_after_translation']
            assert len(columns) == 5 and all(1 <= x < 32 for x in columns)
            assert {apply(columns, x) for x in range(32)} == set(range(32))
            target = row['target_marked_nonzero_mask']
            assert target in cases
            assert {apply(columns, x ^ vertex) for x in support} == set(cases[target]['support'])
            assert apply(columns, vertex ^ vertex) == 0
            targets.add(target)
            verified += 1
        assert sorted(targets) == group['marked_nonzero_masks']
        assert len(targets) == group['marked_case_count']
        all_targets += sorted(targets)
    assert len(set(all_ids)) == 13
    assert len(all_targets) == len(set(all_targets)) == 55 and set(all_targets) == set(cases)
    assert verified == 169
    assert sorted(g['unmarked_affine_orbit_id'] for g in data['groups']
                  if g['exact_maximum11_still_open_in_inherited_frontier']) == [105, 109, 110, 111]
    assert sum(g['marked_case_count'] for g in data['groups']
               if g['exact_maximum11_still_open_in_inherited_frontier']) == 14
    assert sha(path) == original_hash
    receipt = {'status': 'PASS_READ_ONLY_55_MARKED_CASE_AFFINE_TRANSPORT_REPLAY',
               'map_sha256': original_hash, 'map_unchanged': True,
               'verified_invertible_affine_hub_maps': verified,
               'marked_case_count': 55, 'unmarked_affine_support_classes': 13,
               'inherited_maximum11_open_affine_classes': 4,
               'inherited_maximum11_open_marked_cases': 14,
               'new_exclusions_credited': 0,
               'seconds': round(time.monotonic() - start, 6)}
    (HERE / 'SUPPORT13_MARKING_REPLAY.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
