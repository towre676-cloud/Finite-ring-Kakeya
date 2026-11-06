"""Exact finite-domain type-marginal outer relaxation for ring Kakeya coverage.

Types are actual embedded binary subsets, including their translations.
No affine-orbit list or spectrum census is imported. A domain must be complete
or explicitly declared restricted before any infeasibility claim is global.
"""
from itertools import combinations


def quotient(v, d):
    """Canonical representative of v modulo <d>, without bit compression."""
    return min(v, v ^ d)


def pair_labels(fibre, d):
    fibre = set(fibre)
    return {quotient(x, d) for x in fibre if x ^ d in fibre}


def edge_labels(n, a, b, left, right, ring):
    assert ring in ('dual', 'z4') and a != b
    d = a ^ b
    p, q = pair_labels(left, d), pair_labels(right, d)
    carry = quotient(a & d, d) if ring == 'z4' else 0
    return {x ^ y ^ carry for x in p for y in q}


def xname(a, i):
    return f'x:{a}:{i}'


def yname(a, b, i, j):
    return f'y:{a}:{b}:{i}:{j}'


def build_model(n, domains, ring, mode='labels', weight_counts=None):
    """Build nonnegative variables, equalities, and <= inequalities.

    Binary x variables plus these marginals would give the exact finite-domain
    IP in label mode. Keeping all variables continuous gives an outer LP.
    Cardinality mode discards coverage overlap and is only necessary even as IP.
    """
    assert mode in ('labels', 'capacity')
    size = 1 << n
    support = sorted(domains)
    domains = {a: [sorted(set(t)) for t in domains[a]] for a in support}
    variables, equalities, inequalities, tables = [], [], [], []
    for a in support:
        assert domains[a]
        for t in domains[a]:
            assert all(0 <= x < size for x in t)
        names = [xname(a, i) for i in range(len(domains[a]))]
        variables += names
        equalities.append(dict(name=f'node:{a}', coefficients=dict.fromkeys(names, 1), rhs=1))
    label_rows = {}
    for d in range(1, size):
        labels = sorted({quotient(v, d) for v in range(size)})
        if mode == 'labels':
            for z in labels:
                row = dict(name=f'label:{d}:{z}', coefficients={}, rhs=-1)
                label_rows[d, z] = row
                inequalities.append(row)
        else:
            row = dict(name=f'capacity:{d}', coefficients={}, rhs=-(size // 2))
            label_rows[d, None] = row
            inequalities.append(row)
    for a, b in combinations(support, 2):
        d = a ^ b
        entries = []
        for i, left in enumerate(domains[a]):
            for j, right in enumerate(domains[b]):
                name = yname(a, b, i, j)
                variables.append(name)
                labels = sorted(edge_labels(n, a, b, left, right, ring))
                entries.append(dict(left=i, right=j, labels=labels, capacity=len(labels)))
                if mode == 'labels':
                    for z in labels:
                        label_rows[d, z]['coefficients'][name] = -1
                elif labels:
                    label_rows[d, None]['coefficients'][name] = -len(labels)
        tables.append(dict(a=a, b=b, direction=d, entries=entries))
        for endpoint in (a, b):
            for k in range(len(domains[endpoint])):
                coeffs = {xname(endpoint, k): -1}
                for i in range(len(domains[a])):
                    for j in range(len(domains[b])):
                        if (i if endpoint == a else j) == k:
                            coeffs[yname(a, b, i, j)] = 1
                equalities.append(dict(name=f'marginal:{a}:{b}:{endpoint}:{k}',
                                       coefficients=coeffs, rhs=0))
    if weight_counts is not None:
        for w, count in sorted(weight_counts.items()):
            coeffs = {xname(a, i): 1 for a in support for i, t in enumerate(domains[a]) if len(t) == w}
            equalities.append(dict(name=f'weight:{w}', coefficients=coeffs, rhs=count))
    return dict(schema='finite-type-marginal-lp-v1', n=n, ring=ring, mode=mode,
                support=support, domains={str(a): ts for a, ts in domains.items()},
                variables=variables, all_variables_nonnegative=True,
                equalities=equalities, inequalities=inequalities, edge_tables=tables)


def unique_low_fibre_certificate(model, low):
    """Exact Farkas certificate for n2 support3, assigned weights(4,4,2)."""
    assert model['n'] == 2 and len(model['support']) == 3
    directions = {low ^ a for a in model['support'] if a != low}
    le = {}
    for row in model['inequalities']:
        if int(row['name'].split(':')[1]) in directions:
            le[row['name']] = 1
    eq = {f'node:{low}': 2}
    for table in model['edge_tables']:
        a, b = table['a'], table['b']
        if low not in (a, b):
            continue
        for entry in table['entries']:
            k = entry['left'] if low == a else entry['right']
            eq[f'marginal:{a}:{b}:{low}:{k}'] = entry['capacity']
    return dict(schema='nonnegative-farkas-certificate-v1',
                inequality_multipliers=le, equality_multipliers=eq,
                claimed_combined_rhs=-2,
                meaning='Nonnegative residual coefficients and negative rhs contradict nonnegative variables.')
