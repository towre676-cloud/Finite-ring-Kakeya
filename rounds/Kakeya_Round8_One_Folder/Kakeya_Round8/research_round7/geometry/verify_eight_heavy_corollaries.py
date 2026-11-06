#!/usr/bin/env python3
"""Finite algebra and integer controls for the eight-heavy corollaries."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    high_relations = [mask for mask in range(1, 256) if mask.bit_count() in (6, 8)]
    relation_pairs = 0
    for a, b in itertools.combinations(high_relations, 2):
        assert (a ^ b).bit_count() in (2, 4)
        relation_pairs += 1
    plane = (0, 1, 2, 3)
    multiplicities = {d: sum(a ^ b == d for a, b in itertools.combinations(plane, 2))
                      for d in (1, 2, 3)}
    assert multiplicities == {1: 2, 2: 2, 3: 2}
    assert 28 - sum(value - 1 for value in multiplicities.values()) == 25
    assert max(n for n in range(9) if 42 + 14 * n <= 93) == 3
    rows = []
    for maximum in range(2, 19):
        allowed = []
        for t in range(6):
            bound = (maximum // 2) * (5 + 2 * t) if maximum <= 17 else 8 * (5 + 2 * t) + 3
            if bound >= 96:
                allowed.append(t)
        expected = [] if maximum <= 13 else [5] if maximum <= 15 else [4, 5]
        assert allowed == expected
        rows.append({'maximum': maximum, 'possible_light_weight3_counts_by_bound': allowed})
    files = (HERE / 'SUPPORT13_EIGHT_HEAVY_COROLLARIES.md', Path(__file__))
    result = {'status': 'PASS_EIGHT_HEAVY_COROLLARY_CONTROLS',
              'distinct_high_weight_relation_pairs': relation_pairs,
              'plane_direction_multiplicities': multiplicities,
              'max_weight18_fibres_under_budget': 3,
              'integer_controls': rows,
              'new_sat_exclusions_claimed': 0,
              'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
    (HERE / 'SUPPORT13_EIGHT_HEAVY_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
