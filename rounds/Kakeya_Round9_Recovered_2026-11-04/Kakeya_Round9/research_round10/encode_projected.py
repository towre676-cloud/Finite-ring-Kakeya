"""Append redundant heavy-pattern and missing-direction capacity projections.

Frozen Round9 formulas and numbering are preserved as a prefix. No hidden
baseline auxiliary positions are read. Scope: S13, exact hub maximum12/13,
total<=93, both-ring necessary relaxation. See SOUNDNESS.md.
"""
from itertools import combinations, product
import hashlib
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'research_round8/incidence/encode_next_frontier.py'
SOURCE_SHA = 'ba6d760926997e2ab61e1403cdcc363aef39617c6b6c7f3ab59d65836494a825'
if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
    raise ValueError('Frozen next-frontier encoder changed')
spec = importlib.util.spec_from_file_location('round10_frozen_next', SOURCE)
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)


def patterns(support, maximum):
    """Exhaustive small projection; exact integer arithmetic only."""
    S = tuple(support)
    if (len(S) != 13 or len(set(S)) != 13 or S[0] != 0 or
            any(type(v) is not int or not 0 <= v < 32 for v in S) or
            type(maximum) is not int or maximum not in (12, 13)):
        raise ValueError('Expected support13, hub0, exact maximum12/13')
    P = maximum // 2
    forbidden, survivors, witnesses = [], [], []
    for k in range(4):
        for light in combinations(S[1:], k):
            L = set(light)
            H = set(S) - L
            missing = sorted(set(range(1, 32)) - {a ^ b for a, b in combinations(H, 2)})
            capacities = {}
            for d in missing:
                edges = [(a, a ^ d) for a in S if a < (a ^ d) and (a ^ d) in S]
                capacities[d] = sum(1 if a in L and b in L else P for a, b in edges)
            failures = [d for d in missing if capacities[d] < 16]
            bad = bool(failures or len(missing) > 2)
            if bad:
                if not any(set(old) <= L for old in forbidden):
                    forbidden.append(light)
                    witnesses.append({'light': list(light), 'missing': missing,
                                      'direction_capacities': capacities,
                                      'reason': 'capacity_below16' if failures else 'incidence_budget'})
            else:
                survivors.append({'light': list(light), 'missing': missing})
    return {'forbidden_minimal': witnesses, 'survivors': survivors,
            'patterns_considered': 299, 'surviving_patterns': len(survivors)}


def append_projection(formula, support, maximum, *, enabled=True, pair_projection=True):
    before = formula.n, len(formula.cl)
    if not enabled:
        return {'enabled': False, 'added_variables': 0, 'added_clauses': 0}
    meta = formula.r8_next_frontier_metadata
    if (meta['support'] != list(support) or meta['maximum_interval'] != [maximum, maximum]
            or not meta['enabled'] or meta['total_upper_bound'] != 93
            or not meta['optional_pair_propagation_requested']):
        raise ValueError('Projection requires the exact enabled recovered formula')
    data = patterns(support, maximum)
    heavy = formula.r8_incidence['heavy']
    for witness in data['forbidden_minimal']:
        formula.add([heavy[a] for a in witness['light']])
    pair_clauses = 0
    if pair_projection:
        for row in data['survivors']:
            L = row['light']
            for d in row['missing']:
                if len(L) != 3 or any(a ^ d in L or a ^ d not in support for a in L):
                    raise ValueError('Unexpected surviving missing-direction pattern')
                partners = [a ^ d for a in L]
                gate = [heavy[a] for a in L]
                # Assuming these three lights, all other residues are heavy.
                # All three light-heavy edges are active, each heavy count>=4.
                # Emit minimal forbidden partial exact pair choices: the
                # unspecified edges can supply at most P each.
                P = maximum // 2
                for k in range(1, 4):
                    for indices in combinations(range(3), k):
                        for values in product(range(4, P + 1), repeat=k):
                            if sum(values) + P * (3-k) >= 16:
                                continue
                            if any(sum(values)-v+P*(4-k) < 16 for v in values):
                                continue
                            formula.add(gate + [-formula.y[partners[i], d, p]
                                                for i, p in zip(indices, values)])
                            pair_clauses += 1
    return {'enabled': True, 'added_variables': formula.n-before[0],
            'added_clauses': len(formula.cl)-before[1],
            'pattern_clauses': len(data['forbidden_minimal']),
            'pair_projection_clauses': pair_clauses, **data}


def encode(T, maximum, spectra, table, subspaces, *, enabled=True, pair_projection=True):
    formula = N.encode(T, maximum, spectra, table, subspaces)
    formula.r10_projection = append_projection(formula, [0]+list(T), maximum,
                                               enabled=enabled, pair_projection=pair_projection)
    return formula
