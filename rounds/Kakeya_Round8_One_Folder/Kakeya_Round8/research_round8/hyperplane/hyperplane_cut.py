"""Append elementary hyperplane crossing-pair budgets to a spectrum CNF.

Only the public z/y interface is used.  The frozen encoder is never edited.
The auxiliary definitions are exposed solely for constructive replay tests.
"""
from itertools import combinations


def crossing_budget(weight):
    return (weight * weight) // 4


def dot(a, b):
    return (a & b).bit_count() & 1


def append_hyperplane_cuts(formula, support, spectra, enabled=True):
    before_n, before_c = formula.n, len(formula.cl)
    definitions = []
    thresholds = {}
    groups = []
    stats = {"enabled": bool(enabled), "tested_hyperplanes": 0,
             "used_hyperplanes": 0, "spectrum_implications": 0}
    if not enabled:
        stats.update(added_variables=0, added_clauses=0)
        formula.hyperplane_cut_statistics = stats
        return stats

    def new_aux(operation, operands, parameter=None):
        variable = formula.new()
        definitions.append((variable, operation, list(operands), parameter))
        return variable

    def threshold(vertex, direction, level):
        key = (vertex, direction, level)
        if key not in thresholds:
            choices = [literal for (v, d, k), literal in formula.y.items()
                       if v == vertex and d == direction and k >= level]
            variable = new_aux("or", choices)
            formula.add([-variable] + choices)
            for literal in choices:
                formula.add([-literal, variable])
            thresholds[key] = variable
        return thresholds[key]

    def count(values):
        if len(values) <= 1:
            return list(values)
        split = len(values) // 2
        left, right = count(values[:split]), count(values[split:])
        out = [new_aux("threshold", values, k + 1)
               for k in range(len(values))]
        for i in range(len(left) + 1):
            for j in range(len(right) + 1):
                if i + j:
                    formula.add(([-left[i - 1]] if i else []) +
                                ([-right[j - 1]] if j else []) +
                                [out[i + j - 1]])
                if i + j < len(out):
                    formula.add(([left[i]] if i < len(left) else []) +
                                ([right[j]] if j < len(right) else []) +
                                [-out[i + j]])
        return out

    for vertex in support:
        choices = sorted(i for v, i in formula.z if v == vertex)
        directions = sorted({d for v, d, k in formula.y if v == vertex})
        if any(not 1 <= d <= 31 for d in directions):
            raise ValueError("This implementation uses binary dimension five")
        maxima = {d: max(k for v, e, k in formula.y if v == vertex and e == d)
                  for d in directions}
        for u in range(1, 32):
            stats["tested_hyperplanes"] += 1
            outside = [d for d in directions if dot(u, d)]
            restricted = []
            for index in choices:
                weight, histogram, rank_min, rank_max = spectra[index]
                # A nonzero linear form on the affine direction space has
                # 2**(rank-1) directions on its nonzero side.  If it vanishes
                # there, the true crossing count is zero.  The rank-maximum
                # version below is an upper bound in either event.
                places = min(len(outside), 1 << max(rank_max - 1, 0))
                largest = sorted((k for k, multiplicity in enumerate(histogram)
                                  for _ in range(multiplicity)), reverse=True)
                possible = sum(largest[:places])
                if possible > crossing_budget(weight):
                    restricted.append((index, crossing_budget(weight)))
            if not restricted:
                continue
            values = [threshold(vertex, d, level)
                      for d in outside for level in range(1, maxima[d] + 1)]
            outputs = count(values)
            guards = []
            for index, budget in restricted:
                if budget < len(outputs):
                    clause = [-formula.z[vertex, index], -outputs[budget]]
                    formula.add(clause)
                    guards.append((index, budget))
                    stats["spectrum_implications"] += 1
            if guards:
                groups.append((vertex, u, outside, guards))
                stats["used_hyperplanes"] += 1
    stats.update(added_variables=formula.n - before_n,
                 added_clauses=len(formula.cl) - before_c,
                 shared_pair_thresholds=len(thresholds))
    formula.hyperplane_cut_statistics = stats
    formula.hyperplane_aux_definitions = definitions
    formula.hyperplane_groups = groups
    formula.hyperplane_clause_range = (before_c, len(formula.cl))
    return stats


def complete_assignment(formula, assignment):
    for variable, operation, operands, parameter in formula.hyperplane_aux_definitions:
        values = [assignment[abs(x)] == (x > 0) for x in operands]
        if operation == "or":
            result = any(values)
        elif operation == "threshold":
            result = sum(values) >= parameter
        else:
            raise ValueError(operation)
        assignment[variable] = result
    return assignment
