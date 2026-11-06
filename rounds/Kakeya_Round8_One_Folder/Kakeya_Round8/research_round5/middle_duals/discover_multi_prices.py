"""Discover exact rational nine-heavy incidence-price certificates.

SciPy/HiGHS is only a discovery oracle. A proposed rational price is evaluated
against every local active-count pattern before any profile is removed. The
separate verifier does not import this code or require SciPy.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from math import lcm
from pathlib import Path
import argparse
import json
import time

import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / 'research_round4/middle_inventory/after_priced_nine_survivors.txt'


def capacity(p, q):
    return max(p, q) + 8 if min(p, q) == 3 and 5 <= max(p, q) <= 7 else min(16, p*q)


def quota(w):
    return (w & -w)-1 if w % 2 == 0 else max((w-1) & -(w-1), (w+1) & -(w+1))-1


@lru_cache(None)
def features(w, heavy, ell):
    """Best unpriced score for every vector of active counts by heavy cap.

Forward DP retains used pair mass, maximal-count quota, and active-count
vector simultaneously. Equal-cap heavy vertices are interchangeable here.
    """
    groups = tuple(sorted(set(heavy), reverse=True))
    gi = {c: i for i, c in enumerate(groups)}
    mass, cap, full_limit = w*w//4, w//2, min(9, (quota(w)+1)//2)
    states = {(0, 0, (0,)*len(groups)): 0}
    for h in heavy:
        new = {}
        for (used, full, active), score in states.items():
            for p in range(min(cap, mass-used)+1):
                ff = full + (p == cap)
                if ff > full_limit:
                    continue
                aa = list(active)
                aa[gi[h]] += p > 0
                key = used+p, ff, tuple(aa)
                value = score + 2*capacity(p, h) - ell*p
                if value > new.get(key, -10**9):
                    new[key] = value
        states = new
    result = {}
    for (_, _, active), score in states.items():
        result[active] = max(result.get(active, -10**9), ell*mass+score)
    return tuple(sorted(result.items()))


def solve(weights):
    heavy = tuple(w//2 for w in weights[:9])
    groups = tuple(sorted(set(heavy), reverse=True))
    counts = Counter(heavy)
    ell = weights[9]//2
    light = Counter(weights[9:])
    ws = sorted(light)
    rows, rhs = [], []
    tables = {}
    for i, w in enumerate(ws):
        tab = features(w, heavy, ell)
        tables[w] = tab
        for active, score in tab:
            row = [-float(n) for n in active]+[0.0]*len(ws)
            row[len(groups)+i] = -1
            rows.append(row)
            rhs.append(-float(score))
    rows.append([float(counts[h]) for h in groups]+[0.0]*len(ws))
    rhs.append(32.0)
    objective = [3.0*counts[h] for h in groups]+[float(light[w]) for w in ws]
    result = linprog(np.array(objective), A_ub=np.array(rows), b_ub=np.array(rhs),
                     bounds=[(0, None)]*len(groups)+[(None, None)]*len(ws),
                     method='highs')
    assert result.success, result.message
    if result.fun >= 96-1e-7:
        return None, float(result.fun)
    prices = tuple(Fraction(float(x)).limit_denominator(10000) for x in result.x[:len(groups)])
    assert min(prices) >= 0
    if sum(counts[h]*p for h, p in zip(groups, prices)) > 32:
        raise AssertionError(('Rationalized price exceeds slope budget', weights, prices))
    den = lcm(*(p.denominator for p in prices))
    nums = tuple(int(p*den) for p in prices)
    local = []
    for w in ws:
        upper = max(score*den-sum(n*p for n, p in zip(active, nums))
                    for active, score in tables[w])
        local.append({'weight':w, 'multiplicity':light[w], 'upper_numerator':upper})
    cost = sum(counts[h]*p for h, p in zip(groups, nums))
    upper = 3*cost+sum(row['multiplicity']*row['upper_numerator'] for row in local)
    assert upper < 96*den, ('Numerical candidate did not certify', result.fun, upper, den)
    price_by_cap = dict(zip(groups, nums))
    return {
        'support':len(weights), 'maximum':weights[0], 'weights':weights,
        'price_denominator':den,
        'heavy_caps':heavy,
        'price_numerators':[price_by_cap[h] for h in heavy],
        'price_sum_numerator':cost,
        'upper_numerator':upper,
        'required_numerator':96*den,
        'light_rows':local,
        'discovery_float_objective':float(result.fun),
    }, float(result.fun)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--minimum-support', type=int, default=16)
    parser.add_argument('--maximum-support', type=int, default=17)
    parser.add_argument('--limit', type=int)
    parser.add_argument('--tag', default='benchmark')
    args = parser.parse_args()
    assert 10 <= args.minimum_support <= args.maximum_support <= 17
    assert args.tag.replace('_','').isalnum()
    start = time.monotonic()
    cuts = {}
    by = Counter()
    searched = Counter()
    opt = Counter()
    lines = INPUT.read_text().splitlines(keepends=True)
    path = HERE / (args.tag.upper()+'_MULTI_PRICE_CUTS.jsonl')
    with path.open('w') as out:
        for raw in lines:
            s, m, old, *w = map(int, raw.split())
            if not args.minimum_support <= s <= args.maximum_support:
                continue
            if args.limit is not None and sum(searched.values()) >= args.limit:
                break
            cert, value = solve(tuple(w))
            searched[s,m] += 1
            opt['below96' if value < 96-1e-7 else 'equal96' if abs(value-96)<1e-7 else 'above96'] += 1
            if cert:
                key = tuple(w)
                assert key not in cuts
                cuts[key] = cert
                by[s,m] += 1
                out.write(json.dumps(cert, separators=(',',':'))+'\n')
                out.flush()
            if sum(searched.values()) % 250 == 0:
                print(json.dumps({'searched':sum(searched.values()), 'cuts':len(cuts),
                                  'local_keys':features.cache_info().currsize,
                                  'seconds':round(time.monotonic()-start,3)}),flush=True)
    # Rewrite the complete certificate collection after discovery. This also
    # makes the final payload independent of intermediate progress-file reads.
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(''.join(json.dumps(cert,separators=(',',':'))+'\n'
                                 for cert in cuts.values()))
    temporary.replace(path)
    survivor_path = HERE/(args.tag.lower()+'_after_multi_price_survivors.txt')
    with survivor_path.open('w') as out:
        for raw in lines:
            vals = tuple(map(int, raw.split()))
            if vals[3:] not in cuts:
                out.write(raw)
    report = {
        'status':'PRODUCED_EXACT_RATIONAL_CANDIDATES',
        'input_profiles':len(lines), 'searched_profiles':sum(searched.values()),
        'cuts':len(cuts), 'remaining_profiles':len(lines)-len(cuts),
        'minimum_support':args.minimum_support,'maximum_support':args.maximum_support,
        'limit':args.limit,'local_feature_keys':features.cache_info().currsize,
        'floating_optimum_diagnostics':dict(opt),
        'records':[{'support':s,'maximum':m,'searched':n,'cuts':by[s,m]}
                   for (s,m),n in sorted(searched.items())],
        'input_sha256':sha256(INPUT.read_bytes()).hexdigest(),
        'certificates':path.name,'survivors':survivor_path.name,
        'scope':'Exact upper-bound certificates after rationalizing discovered prices; this producer is not the independent replay and does not prove LP optimality for remaining profiles.',
        'seconds':round(time.monotonic()-start,3),
    }
    (HERE/(args.tag.upper()+'_MULTI_PRICE_PRODUCER.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)


if __name__ == '__main__':
    main()
