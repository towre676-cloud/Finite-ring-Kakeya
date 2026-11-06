"""Bounded cross-check of the new joint cube certificates and stage scopes.

This does not replace the complete inventory replay. It independently solves
every joint local row by a bounded-choice DP, verifies all actual-cube branches,
checks generic-test hypotheses and strict stored thresholds, and verifies
disjointness and exact subtraction of the524 new cuts. No producer is imported.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT/'research_round4/middle_inventory'
CENSUS = ROOT/'research_round2/geometric/PAIR_SPECTRUM_CENSUS.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def check_weight(w, s, m):
    assert 10 <= s <= 17 and 12 <= m <= 18
    assert len(w) == s and sum(w) == 93 and w[0] == m and min(w) >= 2
    assert w == tuple(sorted(w, reverse=True))
    assert s*m >= 120 > 93 and w.count(8) <= 10


def one_spectrum(h, r, price):
    # Independent bounded-choice DP; no expanded sorting or greedy gain table.
    energy = sum(p*p*n for p, n in enumerate(h))
    states = {0: 0}
    for p, n in enumerate(h):
        if n == 0:
            continue
        gain = max(0, 2*min(16, 4*p)-p*p-price)
        next_states = {}
        for used, score in states.items():
            for take in range(min(n, r-used)+1):
                size = used+take
                next_states[size] = max(next_states.get(size, -1), score+take*gain)
        states = next_states
    return energy+max(states.values())


def main():
    start = time.monotonic()
    census = json.loads(CENSUS.read_text())
    spectra = {int(w): sorted(tuple(r['hist']) for r in rows) for w, rows in census['weights'].items()}
    for w, rows in spectra.items():
        for h in rows:
            assert sum(h) == 31 and sum(p*n for p,n in enumerate(h)) == w*(w-1)//2
    assert max(sum(p*p*n for p,n in enumerate(h)) for h in spectra[8] if h[4] != 7) == 70
    assert all(sum(p*p*n for p,n in enumerate(h)) == 112 for h in spectra[8] if h[4] == 7)
    saved = json.loads((SOURCE/'CUBE_JOINT_LOCAL_TABLE.json').read_text())
    assert saved['census_sha256'] == sha(CENSUS)
    table = {}
    spectra_evaluated = 0
    for row in saved['rows']:
        w, r, price = row['weight'], row['cubes'], row['twice_price']
        key = w, r, price
        assert key not in table and 2 <= w <= 18 and 0 <= r <= 10 and 8 <= price <= 16
        values = []
        for i, h in enumerate(spectra[w]):
            if w == 8 and h[4] == 7:
                continue
            values.append((one_spectrum(h, r, price), i))
            spectra_evaluated += 1
        maximum = max(v for v, _ in values)
        assert maximum == row['bound']
        assert (maximum, row['attaining_spectrum_index']) in values
        table[key] = maximum
    assert set(table) == {(w,r,p) for w in range(2,19) for r in range(11) for p in range(8,17)}

    cuts = {}
    branch_count, minimum_gap = 0, 10**9
    by_cell = Counter()
    for row in map(json.loads, (SOURCE/'CUBE_JOINT_ENERGY_CUTS.jsonl').open()):
        w = tuple(row['weights'])
        check_weight(w, row['support'], row['maximum'])
        assert w not in cuts
        assert [b['cubes'] for b in row['branches']] == list(range(w.count(8)+1))
        for b in row['branches']:
            r, price = b['cubes'], b['twice_price']
            assert 8 <= price <= 16
            remaining = list(w)
            for _ in range(r):
                remaining.remove(8)
            upper = 7*price*r+(32-2*price)*(r*r//4)
            upper += sum(table[v,r,price] for v in remaining)
            assert upper == b['upper_doubled'] < 992
            minimum_gap = min(minimum_gap, 992-upper)
            branch_count += 1
        cuts[w] = row
        by_cell[len(w), w[0]] += 1
    assert len(cuts) == 524 and branch_count == 2498

    # Check all recorded generic-test scopes and disjointness. Their resource
    # optima are fully recomputed by the separate accepted inventory verifier.
    methods = Counter()
    for line in (SOURCE/'geometry_and_spectrum_cuts.txt').open():
        pieces = line.split()
        method, s, m, n = pieces[0], *map(int, pieces[1:4])
        values = list(map(int, pieces[4:4+n]))
        w = tuple(map(int, pieces[4+n:]))
        check_weight(w, s, m)
        assert w not in cuts
        if method == 'INHERITED_EXACT_SPECTRUM':
            assert not values
        elif method in ('TOTAL_PAIR_ENERGY', 'THREE_HEAVY_SINGLE_EXCEPTION'):
            assert len(values) == 1 and values[0] < 992
        elif method == 'TWO_HEAVY_DELETED_DIRECTION':
            assert len(values) == 1 and values[0] < 960
        elif method == 'EIGHT_HEAVY_MISSING_DIRECTIONS':
            assert len(values) == 2 and values[0] < 288 and values[1] < 192 and s > 8
        elif method == 'NINE_HEAVY_SUMFREE_DIRECTIONS':
            assert len(values) == 1 and values[0] < 96 and s > 9
        elif method == 'HALFSPACE_MAXIMAL_DIRECTION_BONUS':
            assert len(values) == 2 and values[0] < 288 and values[1] < 96
            assert max(v//2 for v in w[8:]) <= 8
        elif method == 'TEN_HEAVY_WEAK_UNIQUE_DIRECTIONS':
            assert w[0]//2 == 6 and all(v//2 <= 4 for v in w[1:10])
            assert all(v <= 3 for v in w[10:])
            weak = sum(v//2 <= 3 for v in w[:10])
            mass = sum(v*(v-1)//2 for v in w[10:])
            assert values == [mass, min(3*weak,12)] and values[0] < values[1]
        else:
            raise AssertionError(method)
        methods[method] += 1
    assert methods['INHERITED_EXACT_SPECTRUM'] == 23164
    assert sum(methods.values())-methods['INHERITED_EXACT_SPECTRUM'] == 135877

    expected_final_hash = hashlib.sha256()
    cut_occurrences = Counter()
    before_count = final_count = 0
    for line in (SOURCE/'final_weight_survivors.txt').open('rb'):
        s,m,b,*weights = map(int,line.split())
        w = tuple(weights)
        check_weight(w,s,m)
        before_count += 1
        if w in cuts:
            cut_occurrences[w] += 1
        else:
            expected_final_hash.update(line)
            final_count += 1
    assert before_count == 276791 and final_count == 276267
    assert set(cut_occurrences) == set(cuts) and set(cut_occurrences.values()) == {1}
    assert expected_final_hash.hexdigest() == sha(SOURCE/'after_cube_weight_survivors.txt')
    receipt = json.loads((SOURCE/'MIDDLE_COMPLETE_INVENTORY.json').read_text())
    assert receipt['status'] == 'PASS'
    assert receipt['additional_joint_cube_energy_cuts'] == 524
    assert receipt['remaining_weight_profiles'] == 276267
    result = dict(status='PASS_BOUNDED_MATHEMATICAL_AND_CODE_CROSS_CHECK',
                  scope='New joint-spectrum cube screen plus generic-screen hypothesis audit and disjoint accounting; complete quota arithmetic is delegated to its separately reviewed replay.',
                  joint_local_rows=len(table), spectra_evaluated=spectra_evaluated,
                  new_joint_weight_profile_cuts=len(cuts), actual_cube_branches=branch_count,
                  minimum_strict_doubled_gap=minimum_gap,
                  prior_inherited_spectrum_cuts=23164, prior_generic_geometry_cuts=135877,
                  final_weight_profiles=final_count,
                  joint_cuts_by_cell=[dict(support=s,maximum=m,cuts=n) for (s,m),n in sorted(by_cell.items())],
                  generic_method_counts=dict(methods),
                  epistemic_scope='Cross-check by another model agent within the same session, not external human independence.',
                  hashes={str(p.relative_to(ROOT)):sha(p) for p in [
                      SOURCE/'MIDDLE_INVENTORY_PROOF.md', SOURCE/'screen_geometry.cpp',
                      SOURCE/'screen_cube_joint_energy.py', SOURCE/'verify_middle_inventory.py',
                      SOURCE/'CUBE_JOINT_LOCAL_TABLE.json', SOURCE/'CUBE_JOINT_ENERGY_CUTS.jsonl',
                      SOURCE/'geometry_and_spectrum_cuts.txt', SOURCE/'final_weight_survivors.txt',
                      SOURCE/'after_cube_weight_survivors.txt', CENSUS,
                  ]}, seconds=round(time.monotonic()-start,3))
    (HERE/'MIDDLE_CUBE_SCREEN_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','joint_local_rows','spectra_evaluated','new_joint_weight_profile_cuts','actual_cube_branches','minimum_strict_doubled_gap','final_weight_profiles','seconds')},indent=2))


if __name__ == '__main__':
    main()
