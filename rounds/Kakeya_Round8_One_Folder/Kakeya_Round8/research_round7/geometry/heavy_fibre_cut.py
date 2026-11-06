"""The census-free support13 heavy-fibre cut; no standalone UNSAT claim.

Soundness is proved in SUPPORT13_HEAVY_FIBRES.md. The only required CNF
interface is new(), add(), unary_sum(), and z[(vertex,spectrum_index)].
Existing spectrum choices must be exactly one at each vertex.
"""


def add_heavy_fibre_cut(formula, support, spectra):
    support = list(support)
    if len(support) != 13 or len(set(support)) != 13:
        raise ValueError('The theorem requires thirteen distinct support vertices')
    domains = {v: sorted(i for vv, i in formula.z if vv == v) for v in support}
    if any(not domain for domain in domains.values()):
        raise ValueError('Every support vertex needs a nonempty spectrum domain')
    if any(not 2 <= spectra[i][0] <= 18 for domain in domains.values() for i in domain):
        raise ValueError('The theorem requires all fibre weights in [2,18]')
    before = formula.n, len(formula.cl)
    heavy = []
    for vertex in support:
        indicator = formula.new()
        choices = [formula.z[vertex, i] for i in domains[vertex] if spectra[i][0] >= 4]
        formula.add([-indicator] + choices)
        for choice in choices:
            formula.add([-choice, indicator])
        heavy.append(indicator)
    outputs = formula.unary_sum(heavy)
    formula.add([outputs[7]])
    return {'statement': 'SUPPORT13_REQUIRES_AT_LEAST_EIGHT_WEIGHT_GE4_FIBRES',
            'support_size': 13, 'maximum_allowed_weight': 18,
            'heavy_threshold': 4, 'required_heavy_vertices': 8,
            'added_variables': formula.n - before[0],
            'added_clauses': len(formula.cl) - before[1]}
