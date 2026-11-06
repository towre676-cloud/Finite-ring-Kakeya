"""Exact three-direction restrictions from the eight cosets of a binary plane.

This wrapper only appends clauses. It never changes the frozen joint encoder.
The semantic justification is PLANE_PAIR_COMPATIBILITY.md. No claim of a
global Kakeya exclusion is made by this module alone.
"""
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product


# Tuple entries are weight, p(1), p(2), p(3). The last entry is a realizing
# four-point-coset mask; bit i represents the point i in F_2^2.
PATTERNS = (
    ((0, 0, 0, 0), 0),
    ((1, 0, 0, 0), 1),
    ((2, 1, 0, 0), 3),
    ((2, 0, 1, 0), 5),
    ((2, 0, 0, 1), 9),
    ((3, 1, 1, 1), 7),
    ((4, 2, 2, 2), 15),
)


@lru_cache(None)
def attainable(cosets=8):
    """Return all exact tuples and one explicit subset mask for each."""
    states = {(0, 0, 0, 0): 0}
    for i in range(cosets):
        nxt = {}
        for state, mask in sorted(states.items()):
            for increment, small_mask in PATTERNS:
                key = tuple(x + y for x, y in zip(state, increment))
                if key not in nxt:
                    nxt[key] = mask | (small_mask << (4 * i))
        states = nxt
    return states


def closed_form_feasible(weight, p, q, r, cosets=8):
    """Independent exact integer criterion proved in the accompanying note."""
    if min(weight, p, q, r) < 0:
        return False
    minimum = min(p, q, r)
    total = p + q + r
    for full in range(min(cosets, minimum // 2) + 1):
        for triple in range(min(cosets - full, minimum - 2 * full) + 1):
            singles = weight - 2 * total + 8 * full + 3 * triple
            empty = cosets - weight + total - 3 * full - triple
            if singles >= 0 and empty >= 0:
                return True
    return False


@lru_cache(None)
def weight_intervals():
    """Each interval is checked against the complete eight-coset relation.

    The interval property is a tiny finite optimization, not an assumed
    general theorem about arbitrary ambient dimensions.
    """
    by_counts = defaultdict(set)
    for weight, p, q, r in attainable():
        by_counts[p, q, r].add(weight)
    result = {}
    for counts, weights in by_counts.items():
        lo, hi = min(weights), max(weights)
        assert weights == set(range(lo, hi + 1)), (counts, weights)
        result[counts] = (lo, hi)
    return result


def incident_planes(directions):
    present = set(directions)
    return sorted({tuple(sorted((d, e, d ^ e)))
                   for d, e in combinations(present, 2) if d ^ e in present})


def _cut_plan(spectra, maximum_pair_count):
    """Omit only quadruples already impossible by the census histogram.

    Each plan item is (p,q,r,lower_bound,upper_bound,forbidden). Bounds set
    to None need no new clause; every plan is exact relative to the supplied
    spectrum choices and the baseline sub-multiset condition.
    """
    intervals = weight_intervals()
    plan = []
    for counts in product(range(maximum_pair_count + 1), repeat=3):
        demand = Counter(counts)
        weights = {sp[0] for sp in spectra
                   if all(sp[1][k] >= count for k, count in demand.items())}
        if not weights:
            continue
        bounds = intervals.get(counts)
        if bounds is None or not any(bounds[0] <= w <= bounds[1] for w in weights):
            plan.append((*counts, None, None, True))
            continue
        lo, hi = bounds
        lower = lo if min(weights) < lo else None
        upper = hi if max(weights) > hi else None
        if lower is not None or upper is not None:
            plan.append((*counts, lower, upper, False))
    return plan


def add_plane_cuts(formula, support, spectra):
    """Append exact local-plane restrictions to an existing joint formula.

    Required interface: new(), add(clause), z[(vertex,spectrum_index)],
    y[(vertex,direction,pair_count)]. This is provided by the frozen Round6
    joint encoder. No hidden subspace selector or edge numbering is used.

    All weight-threshold auxiliaries are defined in both directions. There
    is no new independent choice of weight or fibre type. Distinct vertices
    may have different domains (e.g. a restricted distinguished hub).
    """
    stats = {'local_planes': 0, 'forbidden_triples': 0,
             'lower_weight_cuts': 0, 'upper_weight_cuts': 0,
             'weight_thresholds': 0}
    before_variables, before_clauses = formula.n, len(formula.cl)
    threshold_variables = {}
    plan_cache = {}
    for vertex in support:
        indices = tuple(sorted(i for vv, i in formula.z if vv == vertex))
        local_spectra = [spectra[i] for i in indices]
        directions = sorted({d for vv, d, k in formula.y if vv == vertex})
        planes = incident_planes(directions)
        if not planes:
            continue
        count_sets = {d: sorted(k for vv, dd, k in formula.y
                                if vv == vertex and dd == d)
                      for d in directions}
        maximum = max(k for values in count_sets.values() for k in values)
        key = (indices, maximum)
        if key not in plan_cache:
            plan_cache[key] = _cut_plan(local_spectra, maximum)
        plan = plan_cache[key]

        def weight_at_least(bound):
            key = (vertex, bound)
            if key not in threshold_variables:
                literal = formula.new()
                threshold_variables[key] = literal
                choices = [formula.z[vertex, i] for i in indices
                           if spectra[i][0] >= bound]
                formula.add([-literal] + choices)
                for choice in choices:
                    formula.add([-choice, literal])
                stats['weight_thresholds'] += 1
            return threshold_variables[key]

        for d, e, f in planes:
            stats['local_planes'] += 1
            for p, q, r, lower, upper, forbidden in plan:
                keys = ((vertex, d, p), (vertex, e, q), (vertex, f, r))
                if not all(key in formula.y for key in keys):
                    continue
                prefix = [-formula.y[key] for key in keys]
                if forbidden:
                    formula.add(prefix)
                    stats['forbidden_triples'] += 1
                    continue
                if lower is not None:
                    formula.add(prefix + [weight_at_least(lower)])
                    stats['lower_weight_cuts'] += 1
                if upper is not None:
                    formula.add(prefix + [-weight_at_least(upper + 1)])
                    stats['upper_weight_cuts'] += 1
    stats['added_variables'] = formula.n - before_variables
    stats['added_clauses'] = len(formula.cl) - before_clauses
    formula.plane_weight_thresholds = threshold_variables
    formula.plane_cut_statistics = stats
    return stats


def encode(T, m, SPEC, M, SUBS, outtotal=None, hub_min=2):
    """Convenience wrapper with the same public arguments as joint.encode."""
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[2] / 'research_round6/joint_maxima/encode_joint_maxima.py'
    spec = importlib.util.spec_from_file_location('round6_plane_base', path)
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    result = base.encode(T, m, SPEC, M, SUBS, outtotal, hub_min)
    add_plane_cuts(result, [0] + list(T), SPEC)
    return result
