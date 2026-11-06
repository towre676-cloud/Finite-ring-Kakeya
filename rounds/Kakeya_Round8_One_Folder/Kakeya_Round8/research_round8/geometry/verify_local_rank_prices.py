#!/usr/bin/env python3
"""Independent actual-fibre verification of the rank-sensitive h10 prices.

No imported spectrum, sumset table or SAT solver is read. Every relevant
rank-r fibre is affinely equivalent to a set containing 0,e1,...,er.
The stronger local dual uses U-intercept6; the elementary proof may use
intercept85 and this calculation is then corroboration rather than premise.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRICE = (0, 1, 4, 9, 16, 17)


def pair_counts(points):
    counts = [0] * 32
    for a, b in combinations(points, 2):
        counts[a ^ b] += 1
    return counts[1:]


def main():
    started = time.monotonic()
    local = {}
    checked = 0
    for rank in (3, 4, 5):
        basis = {0} | {1 << bit for bit in range(rank)}
        remaining = sorted(set(range(1 << rank)) - basis)
        for weight in range(rank + 1, min(11, 1 << rank) + 1):
            best3, best9, witness3, witness9, count = -1, -1, None, None, 0
            for tail in combinations(remaining, weight - rank - 1):
                points = sorted(basis | set(tail))
                prices = sorted((PRICE[p] for p in pair_counts(points)), reverse=True)
                top3, top9 = sum(prices[:3]), sum(prices[:9])
                assert 4 * top3 <= 45 * weight - 213 + 45 * (rank == 3)
                if rank == 5:
                    assert 4 * top9 <= 45 * weight + 6
                    assert 4 * top9 <= 45 * weight + 85
                if top3 > best3:
                    best3, witness3 = top3, points
                if top9 > best9:
                    best9, witness9 = top9, points
                count += 1
            local[rank, weight] = {'affine_rank': rank, 'weight': weight,
                                   'normalized_actual_fibres_checked': count,
                                   'maximum_top3_price': best3, 'top3_witness': witness3,
                                   'maximum_top9_price': best9, 'top9_witness': witness9}
            checked += count
    assert checked == 85184

    # Every three-set is affinely equivalent to this triangle in F2^4.
    triangle = (0, 1, 2)
    max35, tested35 = 0, 0
    for other in combinations(range(16), 5):
        capacity = len({a ^ b for a in triangle for b in other})
        assert capacity <= 13
        max35 = max(max35, capacity)
        tested35 += 1
    assert max35 == 13 and tested35 == 4368
    scalar_rows = []
    for p in range(6):
        for q in range(6):
            bound = min(16, p * q)
            if sorted((p, q)) == [3, 5]:
                bound = 13
            assert 2 * bound <= PRICE[p] + PRICE[q]
            scalar_rows.append({'p': p, 'q': q, 'sumset_capacity_bound': bound,
                                'doubled_bound': 2 * bound,
                                'endpoint_prices': PRICE[p] + PRICE[q]})

    # Independent integer optimization of the complete aggregate relaxation.
    # One chosen U- or W-fibre is the actual marked maximum11 hub.
    def optimize(hub_component):
        states = {(0, 0): (0, [])}
        roles = ['U'] * 3 + ['W'] * 7 + ['L'] * 3
        hub_index = 0 if hub_component == 'U' else 3
        for index, role in enumerate(roles):
            options = []
            if role == 'U':
                options = [(weight, 0, row['maximum_top9_price'], 5)
                           for (rank, weight), row in local.items() if rank == 5]
            elif role == 'W':
                options = [(weight, int(rank == 3), row['maximum_top3_price'], rank)
                           for (rank, weight), row in local.items()]
            else:
                options = [(2, 0, 10, None), (3, 0, 30, None)]
            if index == hub_index:
                options = [option for option in options if option[0] == 11]
            updated = {}
            for (total, rank3), (score, witness) in states.items():
                for weight, extra3, value, rank in options:
                    key = total + weight, rank3 + extra3
                    if key[0] > 93 or key[1] > 2:
                        continue
                    candidate = score + value
                    if key not in updated or candidate > updated[key][0]:
                        updated[key] = (candidate, witness + [{'role': role, 'weight': weight,
                                                              'rank': rank, 'price': value}])
            states = updated
        key, (score, witness) = max(states.items(), key=lambda item: item[1][0])
        assert score < 768
        return {'hub_component': hub_component, 'maximum_price': score,
                'required_price': 768, 'total_weight': key[0],
                'rank3_W_fibres': key[1], 'maximizing_relaxed_assignment': witness}

    dp = [optimize('W'), optimize('U')]
    assert [row['maximum_price'] for row in dp] == [663, 685]
    stronger = 45 * 93 + 3 * 6 - 7 * 213 + 2 * 45 - 3 * 15
    elementary = 45 * 93 + 3 * 85 - 7 * 213 + 2 * 45 - 3 * 15
    assert stronger == 2757 and elementary == 2994 and elementary < 4 * 768
    result = {'status': 'PASS_INDEPENDENT_NORMALIZED_FIBRE_PRICE_AND_AGGREGATE_REPLAY',
              'imported_census_or_Mtable_read': False, 'SAT_solver_invoked': False,
              'normalized_actual_fibres_checked': checked,
              'normalization_completeness': 'Every affine-rank-r fibre admits an affine basis mapped to0,e1,...,er; all remaining points are enumerated.',
              'local_price_maxima': list(local.values()),
              'three_by_five_partner_sets_checked': tested35, 'three_by_five_maximum': max35,
              'scalar_price_controls': scalar_rows,
              'independent_aggregate_DP': dp,
              'stronger_fourfold_price_bound': stronger,
              'elementary_fourfold_price_bound': elementary,
              'required_fourfold_price': 3072,
              'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'seconds': round(time.monotonic() - started, 6)}
    (HERE / 'LOCAL_RANK_PRICE_REPLAY.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: value for k, value in result.items()
                      if k not in ('local_price_maxima', 'scalar_price_controls', 'independent_aggregate_DP')}, indent=2))
    print('independent DP bounds:', [row['maximum_price'] for row in dp])


if __name__ == '__main__':
    main()
