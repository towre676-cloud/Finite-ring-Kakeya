"""Optional exact pair-space caps for the rank4 weight11/energy211 type."""
from itertools import combinations


def q211_type(spectrum):
    weight, histogram, low, high = spectrum
    return (weight == 11 and low == high == 4
            and sum(p * p * count for p, count in enumerate(histogram)) == 211)


def append_q211_pair_space_cuts(formula, support, spectra, subspaces,
                                dimensions=(3, 4), enabled=True):
    before = formula.n, len(formula.cl)
    metadata = {'enabled': bool(enabled), 'dimensions': list(dimensions),
                'ordinary_or_effective_space_cap_rows': 0,
                'three_by_three_cap7_rows': 0}
    formula.q211_pair_aux_definitions = []
    if not enabled:
        metadata.update(added_variables=0, added_clauses=0)
        formula.q211_pair_space_metadata = metadata
        return metadata
    support = sorted(support)
    if len(support) != len(set(support)) or any(not 0 <= x < 32 for x in support):
        raise ValueError('Expected distinct binary5 support residues')
    dimensions = tuple(sorted(set(dimensions)))
    if not dimensions or any(value not in (3, 4) for value in dimensions):
        raise ValueError('This wrapper supports ambient pair spaces of dimension3 or4')
    for name in ('z', 'y', 'h_selectors', 'k_selectors', 'r8_edge_capacity'):
        if not hasattr(formula, name):
            raise ValueError('Missing explicit formula map: ' + name)
    spaces = [space for space in subspaces if len(space).bit_length() - 1 in dimensions]
    definitions = formula.q211_pair_aux_definitions

    def auxiliary(operation, inputs):
        variable = formula.new()
        definitions.append((variable, operation, list(inputs)))
        return variable

    def exact_or(inputs):
        inputs = list(inputs)
        if len(inputs) == 1:
            return inputs[0]
        out = auxiliary('or', inputs)
        formula.add([-out] + inputs)
        for value in inputs:
            formula.add([-value, out])
        return out

    def exact_and(a, b):
        out = auxiliary('and', (a, b))
        formula.add([-out, a])
        formula.add([-out, b])
        formula.add([-a, -b, out])
        return out

    eligible = [i for i, spectrum in enumerate(spectra) if q211_type(spectrum)]
    type_flags = {v: exact_or(formula.z[v, i] for i in eligible if (v, i) in formula.z)
                  for v in support}
    h_inside, k_inside, qualified, effective = {}, {}, {}, {}
    for vertex in support:
        for space in spaces:
            h_inside[vertex, space] = exact_or(
                literal for H, literal in formula.h_selectors[vertex].items() if H <= space)
            k_inside[vertex, space] = exact_or(
                literal for K, literal in formula.k_selectors[vertex].items()
                if len(K) == 4 and K <= space)
        directions = sorted({d for v, d, p in formula.y if v == vertex})
        for direction in directions:
            allowed_count = exact_or(formula.y[vertex, direction, p]
                                     for p in (3, 4) if (vertex, direction, p) in formula.y)
            qualified[vertex, direction] = exact_and(type_flags[vertex], allowed_count)
            for space in spaces:
                if direction not in space:
                    continue
                h, k, q = h_inside[vertex, space], k_inside[vertex, space], qualified[vertex, direction]
                out = auxiliary('or_and', (h, q, k))
                # out iff h OR (q AND k).
                formula.add([-h, out])
                formula.add([-q, -k, out])
                formula.add([-out, h, q])
                formula.add([-out, h, k])
                effective[vertex, direction, space] = out
    for a, b in combinations(support, 2):
        direction = a ^ b
        bits = formula.r8_edge_capacity.get((a, b))
        if bits is None or len(bits) != 16:
            raise ValueError('Missing explicit sixteen-bit edge capacity')
        for space in spaces:
            if direction not in space:
                continue
            left, right = effective[a, direction, space], effective[b, direction, space]
            cap = len(space) // 2
            formula.add([-left, -right, -bits[cap]])
            metadata['ordinary_or_effective_space_cap_rows'] += 1
            if len(space) == 16 and (a, direction, 3) in formula.y and (b, direction, 3) in formula.y:
                formula.add([-left, -right, -formula.y[a, direction, 3],
                             -formula.y[b, direction, 3], -bits[7]])
                metadata['three_by_three_cap7_rows'] += 1
    metadata.update(dimensions=list(dimensions), eligible_spectrum_indices=eligible,
                    effective_containment_flags=len(effective),
                    added_variables=formula.n - before[0], added_clauses=len(formula.cl) - before[1])
    formula.q211_pair_space_metadata = metadata
    return metadata


def complete_assignment(formula, assignment):
    for variable, operation, inputs in formula.q211_pair_aux_definitions:
        values = [assignment[abs(value)] == (value > 0) for value in inputs]
        if operation == 'or':
            value = any(values)
        elif operation == 'and':
            value = all(values)
        elif operation == 'or_and':
            value = values[0] or (values[1] and values[2])
        else:
            raise ValueError(operation)
        assignment[variable] = value
