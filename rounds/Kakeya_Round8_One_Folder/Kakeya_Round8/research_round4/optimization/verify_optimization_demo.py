"""Independent standard-library replay of the type-LP demonstrations.

Does not import the model builder. Tables are checked by literal arithmetic
in the two rings. Linear certificates and witnesses use exact Fractions.
"""
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent


def point(n, residue, tangent):
    return tuple(((residue >> i) & 1) + 2*((tangent >> i) & 1) for i in range(n))


def line_point(anchor, direction, scalar, ring):
    if ring == 'z4':
        return tuple((x + scalar*y) % 4 for x, y in zip(anchor, direction))
    lo, hi = scalar & 1, scalar >> 1
    result = []
    for x, y in zip(anchor, direction):
        yl, yh = y & 1, y >> 1
        multiple = (lo*yl) + 2*((lo*yh) ^ (hi*yl))
        result.append(x ^ multiple)
    return tuple(result)


def direct_coverage(n, fibres, ring, directions=None):
    points = {point(n, a, b) for a, values in fibres.items() for b in values}
    result = {}
    for d in (range(1, 1 << n) if directions is None else directions):
        # One representative of each unit-multiple pair of primitive vectors.
        representatives = [v for v in range(1 << n) if v < (v ^ d)]
        covered = []
        for v in representatives:
            direction = point(n, d, v)
            if any(all(line_point(anchor, direction, t, ring) in points for t in range(4))
                   for anchor in points):
                covered.append(v)
        result[d] = covered
    return result


@lru_cache(None)
def direct_edge(n, a, b, left, right, ring):
    return tuple(direct_coverage(n, {a: left, b: right}, ring, [a ^ b])[a ^ b])


def clean(coefficients):
    return {v: q for v, q in coefficients.items() if q}


def check_semantics(model):
    assert model['schema'] == 'finite-type-marginal-lp-v1'
    n, ring, mode = model['n'], model['ring'], model['mode']
    assert n == 2 and ring in ('dual', 'z4') and mode in ('capacity', 'labels')
    support = model['support']
    domains = {int(a): tuple(tuple(t) for t in ts) for a, ts in model['domains'].items()}
    assert sorted(domains) == support
    # In these examples every domain contains every subset of its assigned size.
    for ts in domains.values():
        w = len(ts[0])
        assert ts == tuple(combinations(range(1 << n), w))
    x = lambda a, i: f'x:{a}:{i}'
    y = lambda a, b, i, j: f'y:{a}:{b}:{i}:{j}'
    expected_variables = {x(a, i) for a in support for i in range(len(domains[a]))}
    expected_equalities = {f'node:{a}': ({x(a, i): 1 for i in range(len(domains[a]))}, 1)
                           for a in support}
    expected_inequalities = {}
    for d in range(1, 1 << n):
        if mode == 'capacity':
            expected_inequalities[f'capacity:{d}'] = ({}, -(1 << (n-1)))
        else:
            for z in range(1 << n):
                if z < (z ^ d):
                    expected_inequalities[f'label:{d}:{z}'] = ({}, -1)
    expected_edges = set(combinations(support, 2))
    edges_seen = set()
    table_checks = 0
    for table in model['edge_tables']:
        a, b = table['a'], table['b']
        assert (a, b) in expected_edges and (a, b) not in edges_seen
        edges_seen.add((a, b))
        assert table['direction'] == a ^ b
        pair_seen = set()
        for entry in table['entries']:
            i, j = entry['left'], entry['right']
            assert (i, j) not in pair_seen
            pair_seen.add((i, j))
            observed = direct_edge(n, a, b, domains[a][i], domains[b][j], ring)
            assert list(observed) == entry['labels']
            assert len(observed) == entry['capacity']
            name = y(a, b, i, j)
            expected_variables.add(name)
            if mode == 'capacity':
                if observed:
                    expected_inequalities[f'capacity:{a ^ b}'][0][name] = -len(observed)
            else:
                for z in observed:
                    expected_inequalities[f'label:{a ^ b}:{z}'][0][name] = -1
            table_checks += 1
        assert pair_seen == set(product(range(len(domains[a])), range(len(domains[b]))))
        for endpoint in (a, b):
            for k in range(len(domains[endpoint])):
                coefficients = {x(endpoint, k): -1}
                for i in range(len(domains[a])):
                    for j in range(len(domains[b])):
                        if (i if endpoint == a else j) == k:
                            coefficients[y(a, b, i, j)] = 1
                expected_equalities[f'marginal:{a}:{b}:{endpoint}:{k}'] = (coefficients, 0)
    assert edges_seen == expected_edges
    assert len(model['variables']) == len(expected_variables)
    assert set(model['variables']) == expected_variables and model['all_variables_nonnegative'] is True
    for key, expected in [('equalities', expected_equalities), ('inequalities', expected_inequalities)]:
        observed = {r['name']: (clean(r['coefficients']), r['rhs']) for r in model[key]}
        assert len(observed) == len(model[key])
        assert observed == expected
    return domains, table_checks


def farkas_check(model, certificate):
    assert certificate['schema'] == 'nonnegative-farkas-certificate-v1'
    residual = defaultdict(Fraction)
    rhs = Fraction(0)
    for key, multipliers, nonnegative in [
        ('inequalities', certificate['inequality_multipliers'], True),
        ('equalities', certificate['equality_multipliers'], False),
    ]:
        rows = {r['name']: r for r in model[key]}
        assert set(multipliers) <= set(rows)
        for name, value in multipliers.items():
            multiplier = Fraction(value)
            assert not nonnegative or multiplier >= 0
            rhs += multiplier * rows[name]['rhs']
            for variable, coefficient in rows[name]['coefficients'].items():
                residual[variable] += multiplier * coefficient
    assert set(residual) <= set(model['variables'])
    assert all(c >= 0 for c in residual.values())
    assert rhs == certificate['claimed_combined_rhs'] < 0
    return dict(combined_rhs=str(rhs), nonzero_residual_coefficients=clean(dict(residual)))


def primal_check(model, values):
    assert set(values) == set(model['variables'])
    values = {v: Fraction(q) for v, q in values.items()}
    assert min(values.values()) >= 0
    for row in model['equalities']:
        assert sum(c*values[v] for v, c in row['coefficients'].items()) == row['rhs']
    for row in model['inequalities']:
        assert sum(c*values[v] for v, c in row['coefficients'].items()) <= row['rhs']


def integer_count(n, domains, ring):
    support = sorted(domains)
    count, witnesses, tested = 0, [], 0
    for choices in product(*(domains[a] for a in support)):
        fibres = dict(zip(support, choices))
        coverage = direct_coverage(n, fibres, ring)
        feasible = all(len(labels) == (1 << (n-1)) for labels in coverage.values())
        if all(len(t) == 3 for t in choices):
            missing = [next(x for x in range(4) if x not in t) for t in choices]
            total = missing[0] ^ missing[1] ^ missing[2] ^ missing[3]
            assert feasible == (ring == 'z4' and total == 3)
        tested += 1
        if feasible:
            count += 1
            if not witnesses:
                witnesses.append({str(a): list(t) for a, t in fibres.items()})
    return tested, count, witnesses


def main():
    start = time.monotonic()
    manifest = json.loads((HERE/'DEMO_MANIFEST.json').read_text())
    records = []
    hashes = {}
    for name in manifest['examples']:
        path = HERE/'demo'/(name+'.json')
        data = json.loads(path.read_text())
        model = data['model']
        domains, checked = check_semantics(model)
        row = dict(example=name, direct_ring_edge_table_entries_checked=checked,
                   variables=len(model['variables']), equalities=len(model['equalities']),
                   inequalities=len(model['inequalities']))
        if 'certificate' in data:
            result = farkas_check(model, data['certificate'])
            row.update(lp_status='INFEASIBLE_EXACT_FARKAS_CERTIFICATE', combined_rhs=result['combined_rhs'])
        else:
            primal_check(model, data['fractional_lp_witness'])
            row.update(lp_status='FEASIBLE_EXACT_RATIONAL_WITNESS')
        tested, feasible, witnesses = integer_count(model['n'], domains, model['ring'])
        assert feasible == data['expected_integer_feasible_assignments']
        row.update(integer_assignments_checked=tested, feasible_integer_assignments=feasible,
                   first_integer_witness=witnesses)
        records.append(row)
        hashes[str(path.relative_to(HERE))] = hashlib.sha256(path.read_bytes()).hexdigest()
    # A single edge's two ring tables can differ only by a translated label set.
    carry_examples = {}
    for ring in ('dual', 'z4'):
        carry_examples[ring] = list(direct_edge(2, 1, 2, (0, 3), (0, 3), ring))
    assert carry_examples == {'dual': [0], 'z4': [1]}
    theta_checks = 0
    for theta in map(Fraction, ['1/9', '1/3', '1/2', '1', '2', '3', '9']):
        a, b = theta.numerator, theta.denominator
        for p, q in product(range(10), repeat=2):
            assert a*a*p*p + b*b*q*q - 2*a*b*p*q == (a*p-b*q)**2 >= 0
            theta_checks += 1
    weighted_hub = (Fraction(1, 9)*81 + 9)/2
    assert weighted_hub == 9 and (81+1)//2 == 41
    receipt = dict(status='PASS', scope='Finite-domain architecture and n2 demonstrations; no new n5 exclusion is claimed.',
                   examples=records, direct_ring_edge_table_entries_checked=sum(r['direct_ring_edge_table_entries_checked'] for r in records),
                   exact_farkas_certificates=sum('certificate' in json.loads((HERE/'demo'/(n+'.json')).read_text()) for n in manifest['examples']),
                   ring_shift_example=carry_examples, weighted_square_checks=theta_checks,
                   hub9_against1=dict(unweighted_upper=41, weighted_upper=9, theta='1/9'),
                   files_sha256=hashes, seconds=round(time.monotonic()-start, 3))
    (HERE/'OPTIMIZATION_DEMO_VERIFICATION.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('status','scope','exact_farkas_certificates','direct_ring_edge_table_entries_checked','seconds')},indent=2))
    print(json.dumps({r['example']:r['feasible_integer_assignments'] for r in records if '3333' in r['example']},indent=2))


if __name__ == '__main__':
    main()
