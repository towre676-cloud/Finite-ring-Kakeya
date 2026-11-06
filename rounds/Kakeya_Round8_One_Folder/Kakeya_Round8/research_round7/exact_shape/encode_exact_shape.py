"""Direct binary fibre shapes and exact quotient-sumset cardinalities.

This is a common necessary-condition relaxation for both length-two rings.
It deliberately sums edge cardinalities; it does not assert that their
label sets are disjoint or cover the quotient. The full one-way proof is
EXACT_SHAPE_METHOD.md. No spectrum census or subspace catalogue is used.
"""
from collections import defaultdict
from itertools import combinations


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []
        self.gates = []

    def new(self):
        self.n += 1
        return self.n

    def add(self, clause):
        self.cl.append(list(clause))

    def and_gate(self, left, right):
        out = self.new()
        self.add([-left, -right, out])
        self.add([left, -out])
        self.add([right, -out])
        self.gates.append(('and', out, left, right))
        return out

    def or_gate(self, literals):
        literals = list(literals)
        if len(literals) == 1:
            return literals[0]
        out = self.new()
        self.add([-out] + literals)
        for literal in literals:
            self.add([-literal, out])
        self.gates.append(('or', out, literals))
        return out

    def unary_sum(self, literals, limit=None):
        """Bidirectional balanced totalizer, truncated at an exact threshold.

        Output i means count >= i+1. Child arrays are truncated at the same
        limit. In reverse clauses with i+j below the output length, an
        omitted child literal necessarily belongs to an untruncated child;
        hence truncation preserves both directions of the usual totalizer.
        """
        literals = list(literals)
        if limit is None:
            limit = len(literals)
        if limit <= 0 or not literals:
            return []
        if len(literals) == 1:
            return literals
        middle = len(literals) // 2
        left = self.unary_sum(literals[:middle], limit)
        right = self.unary_sum(literals[middle:], limit)
        out = [self.new() for _ in range(min(len(literals), limit))]
        for i in range(len(left) + 1):
            for j in range(len(right) + 1):
                if 0 < i + j <= len(out):
                    self.add(([-left[i - 1]] if i else []) +
                             ([-right[j - 1]] if j else []) + [out[i + j - 1]])
                if i + j < len(out):
                    self.add(([left[i]] if i < len(left) else []) +
                             ([right[j]] if j < len(right) else []) + [-out[i + j]])
        self.gates.append(('sum', out, literals))
        return out


def quotient_representatives(direction, size):
    """The pivot-bit-zero hyperplane: a linear representative of V/<d>."""
    return [x for x in range(size) if x < (x ^ direction)]


def encode_support(support, maximum, hub_min=2, total=93, dimension=5,
                   normalize_fibres=True):
    size = 1 << dimension
    quotient_size = size // 2
    support = sorted(support)
    assert 0 in support and len(support) == len(set(support))
    assert all(0 <= v < size for v in support)
    assert 2 <= hub_min <= maximum <= size
    assert isinstance(total, int) and total >= 0
    formula = CNF()
    formula.points = {(v, x): formula.new() for v in support for x in range(size)}
    formula.weight_bits = {}
    formula.pairs = {}
    formula.sumset_bits = {}
    formula.sumset_witnesses = {}

    # Every fibre is pair-active. Its cardinality is represented exactly.
    for vertex in support:
        if normalize_fibres:
            formula.add([formula.points[vertex, 0]])
        bits = formula.unary_sum([formula.points[vertex, x] for x in range(size)],
                                 min(size, maximum + 1))
        for k, literal in enumerate(bits, 1):
            formula.weight_bits[vertex, k] = literal
        formula.add([bits[1]])
        if maximum < size:
            formula.add([-bits[maximum]])
    formula.add([formula.weight_bits[0, hub_min]])
    for vertex in support:
        if vertex:
            for k in range(3, maximum + 1):
                formula.add([-formula.weight_bits[vertex, k],
                             formula.weight_bits[0, k]])

    # Remove the already-required two points per fibre from the budget.
    excess_budget = total - 2 * len(support)
    excess_bits = [formula.weight_bits[v, k] for v in support
                   for k in range(3, maximum + 1)]
    if excess_budget < 0:
        formula.add([])
    elif excess_budget < len(excess_bits):
        budget = formula.unary_sum(excess_bits, excess_budget + 1)
        formula.add([-budget[excess_budget]])

    directions = {v: sorted(v ^ b for b in support if b != v) for v in support}
    for vertex in support:
        for direction in directions[vertex]:
            for x in quotient_representatives(direction, size):
                formula.pairs[vertex, direction, x] = formula.and_gate(
                    formula.points[vertex, x], formula.points[vertex, x ^ direction])

    capacities = defaultdict(list)
    edge_counts = defaultdict(int)
    for a, b in combinations(support, 2):
        direction = a ^ b
        representatives = quotient_representatives(direction, size)
        edge_counts[direction] += 1
        for label in representatives:
            witnesses = []
            for x in representatives:
                witness = formula.and_gate(formula.pairs[a, direction, x],
                                           formula.pairs[b, direction, x ^ label])
                witnesses.append(witness)
                formula.sumset_witnesses[a, b, label, x] = witness
            covered = formula.or_gate(witnesses)
            formula.sumset_bits[a, b, label] = covered
            capacities[direction].append(covered)
    for direction in range(1, size):
        bits = capacities[direction]
        if len(bits) < quotient_size:
            formula.add([])
        elif len(bits) == quotient_size:
            for bit in bits:
                formula.add([bit])
        else:
            coverage = formula.unary_sum(bits, quotient_size)
            formula.add([coverage[quotient_size - 1]])

    formula.exact_shape_metadata = {
        'encoder': 'actual_binary_fibres_and_exact_edge_sumset_cardinalities',
        'dimension': dimension,
        'support': support,
        'largest_fibre_at': 0,
        'hub_minimum': hub_min,
        'maximum_fibre': maximum,
        'total_upper_bound': total,
        'independent_fibre_zero_normalization': normalize_fibres,
        'ring_scope': 'common_necessary_relaxation_both_length_two_rings',
        'spectrum_census_used': False,
        'variables': formula.n,
        'clauses': len(formula.cl),
        'point_variables': len(formula.points),
        'pair_variables': len(formula.pairs),
        'sumset_variables': len(formula.sumset_bits),
        'sumset_witness_variables': len(formula.sumset_witnesses),
        'edge_counts_by_direction': dict(sorted(edge_counts.items())),
    }
    return formula


def encode(T, m, SPEC=None, M=None, SUBS=None, outtotal=None, hub_min=2):
    """Compatibility entry point; census arguments are deliberately unused."""
    return encode_support([0] + list(T), m, hub_min,
                          93 if outtotal is None else outtotal)


def write_dimacs(formula, path):
    with open(path, 'w') as handle:
        handle.write(f'p cnf {formula.n} {len(formula.cl)}\n')
        for clause in formula.cl:
            handle.write(' '.join(map(str, clause)) + ' 0\n')


def extend_assignment(formula, fibres):
    """Evaluate every definitional gate from actual normalized fibres.

    This does not silently normalize input fibres. Callers must provide
    the intended point assignment, so a bad normalization test is visible.
    """
    assignment = {literal: x in fibres[v] for (v, x), literal in formula.points.items()}

    def value(literal):
        result = assignment[abs(literal)]
        return result if literal > 0 else not result

    for gate in formula.gates:
        kind = gate[0]
        if kind == 'and':
            _, out, left, right = gate
            assignment[out] = value(left) and value(right)
        elif kind == 'or':
            _, out, literals = gate
            assignment[out] = any(value(literal) for literal in literals)
        else:
            assert kind == 'sum'
            _, outputs, literals = gate
            count = sum(value(literal) for literal in literals)
            for threshold, out in enumerate(outputs, 1):
                assignment[out] = count >= threshold
    assert set(assignment) == set(range(1, formula.n + 1))
    return assignment


def unsatisfied_clauses(formula, assignment):
    return [i for i, clause in enumerate(formula.cl)
            if not any(assignment[abs(literal)] == (literal > 0) for literal in clause)]
