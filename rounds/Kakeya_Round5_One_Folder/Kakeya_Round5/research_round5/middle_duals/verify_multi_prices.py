"""Independently replay rational multi-heavy incidence-price exclusions.

Only Python's standard library is required. This file imports neither the
producer nor SciPy. Every local maximum is recomputed by a backward nine-slot
recursion without active-count grouping or LP optimization.
"""
from collections import Counter
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / 'research_round4/middle_inventory/after_priced_nine_survivors.txt'


def pair_cap(p, q):
    a, b = sorted((p, q))
    if a == 3 and b in (5, 6, 7):
        return b+8
    return min(16, p*q)


def max_direction_quota(w):
    if w % 2 == 0:
        return (w & -w)-1
    return max((w-1) & -(w-1), (w+1) & -(w+1))-1


@lru_cache(None)
def exact_row(w, heavy, ell, prices, den):
    c = w//2
    mass = w*w//4
    quota = (max_direction_quota(w)+1)//2
    @lru_cache(None)
    def backward(index, remaining_mass, remaining_full):
        if index < 0:
            return 0
        best = None
        for p in range(min(c, remaining_mass)+1):
            full = int(p == c)
            if full > remaining_full:
                continue
            score = (2*pair_cap(p, heavy[index])-ell*p)*den
            if p > 0:
                score -= prices[index]
            value = score+backward(index-1, remaining_mass-p, remaining_full-full)
            best = value if best is None else max(best, value)
        assert best is not None
        return best
    return ell*mass*den+backward(8, mass, min(9, quota))


def main():
    if sys.flags.optimize:
        raise SystemExit('Assertions must be enabled; do not run with -O.')
    parser = argparse.ArgumentParser()
    parser.add_argument('--tag', default='full')
    args = parser.parse_args()
    assert args.tag.replace('_','').isalnum()
    start = time.monotonic()
    tag = args.tag.upper()
    cert_path = HERE/(tag+'_MULTI_PRICE_CUTS.jsonl')
    producer_path = HERE/(tag+'_MULTI_PRICE_PRODUCER.json')
    declared = json.loads(producer_path.read_text())
    assert declared['input_sha256'] == sha256(INPUT.read_bytes()).hexdigest()
    baseline = {}
    cells_before = Counter()
    for raw in INPUT.read_bytes().splitlines(keepends=True):
        s, m, old, *weights = map(int, raw.split())
        weights = tuple(weights)
        assert len(weights) == s and weights[0] == m and sum(weights) == 93
        assert weights == tuple(sorted(weights, reverse=True)) and min(weights) >= 2
        assert weights not in baseline
        baseline[weights] = raw
        cells_before[s,m] += 1
    assert len(baseline) == 275755
    cuts = {}
    by_cell = Counter()
    price_denominators = Counter()
    numerator_gaps = []
    for cert in map(json.loads, cert_path.open()):
        weights = tuple(cert['weights'])
        assert weights in baseline and weights not in cuts
        assert cert['support'] == len(weights) and cert['maximum'] == weights[0]
        assert declared['minimum_support'] <= len(weights) <= declared['maximum_support']
        heavy = tuple(w//2 for w in weights[:9])
        assert list(heavy) == cert['heavy_caps'] and len(heavy) == 9
        ell = weights[9]//2
        assert all(w//2 <= ell for w in weights[9:])
        prices = tuple(cert['price_numerators'])
        den = cert['price_denominator']
        assert type(den) is int and den > 0
        assert len(prices) == 9 and all(type(p) is int and p >= 0 for p in prices)
        assert sum(prices) == cert['price_sum_numerator'] <= 32*den
        light = Counter(weights[9:])
        rows = []
        for w, count in sorted(light.items()):
            upper = exact_row(w, heavy, ell, prices, den)
            rows.append({'weight':w,'multiplicity':count,'upper_numerator':upper})
        assert rows == cert['light_rows']
        upper = 3*sum(prices)+sum(row['multiplicity']*row['upper_numerator'] for row in rows)
        assert upper == cert['upper_numerator'] < cert['required_numerator'] == 96*den
        numerator_gaps.append((96*den-upper, den))
        cuts[weights] = cert
        by_cell[len(weights),weights[0]] += 1
        price_denominators[den] += 1
    assert len(cuts) == declared['cuts']
    final_path = HERE/declared['survivors']
    expected = b''.join(raw for w, raw in baseline.items() if w not in cuts)
    assert final_path.read_bytes() == expected
    final_cells = cells_before-by_cell
    assert sum(final_cells.values()) == declared['remaining_profiles'] == len(baseline)-len(cuts)
    for row in declared['records']:
        assert row['cuts'] == by_cell[row['support'],row['maximum']]
    closed = [{'support':s,'maximum':m} for s,m in sorted(cells_before)
              if cells_before[s,m] > 0 and final_cells[s,m] == 0]
    report = {
        'status':'PASS_INDEPENDENT_EXACT_MULTI_PRICE_REPLAY',
        'input_profiles':len(baseline), 'additional_disjoint_profile_exclusions':len(cuts),
        'remaining_weight_profiles':len(baseline)-len(cuts),
        'newly_empty_cells':closed, 'remaining_nonempty_cells':len(final_cells),
        'local_rows_recomputed':exact_row.cache_info().currsize,
        'price_denominators':dict(sorted(price_denominators.items())),
        'minimum_doubled_gap':None if not numerator_gaps else min(a/b for a,b in numerator_gaps),
        'records':[{'support':s,'maximum':m,'input':n,'cuts':by_cell[s,m],
                    'remaining':final_cells[s,m]} for (s,m),n in sorted(cells_before.items())],
        'supports':[{'support':s, 'input':sum(n for (ss,m),n in cells_before.items() if ss==s),
                     'cuts':sum(n for (ss,m),n in by_cell.items() if ss==s),
                     'remaining':sum(n for (ss,m),n in final_cells.items() if ss==s)} for s in range(10,18)],
        'validity_scope':'Nonnegative prices at all nine selected heavy vertices with total price<=32; common local pair and maximal-direction budgets; exact rational upper bounds below96 extrapolate to every missing count r>=3.',
        'optimization_scope':'The certificate checker proves every credited exclusion. It does not trust the floating optimizer and does not claim optimality of its results on surviving profiles.',
        'remaining_object_type':'Weight-profile relaxation survivors, not residue placements, compatible shapes, or Kakeya constructions.',
        'dependencies':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in [
            INPUT,cert_path,producer_path,final_path,Path(__file__).resolve(),
            ROOT/'research_round3/middle/RESOURCE_COMPATIBILITY_LEMMAS.md',
            ROOT/'research_round2/middle/DIFFERENCE_AND_LIGHT_RESOURCE_LEMMAS.md',
        ]},
        'seconds':round(time.monotonic()-start,3),
    }
    (HERE/(tag+'_MULTI_PRICE_INDEPENDENT_REPLAY.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','input_profiles','additional_disjoint_profile_exclusions',
                       'remaining_weight_profiles','newly_empty_cells','remaining_nonempty_cells',
                       'local_rows_recomputed','price_denominators','minimum_doubled_gap','seconds']},indent=2))


if __name__ == '__main__':
    main()
