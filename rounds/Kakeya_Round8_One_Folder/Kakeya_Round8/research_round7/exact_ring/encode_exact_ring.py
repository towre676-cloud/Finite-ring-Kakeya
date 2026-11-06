"""Exact actual-membership Kakeya CNF over Z/4 or F2[epsilon]/epsilon^2.

No spectrum census, sumset-capacity table or independent fibre translations
are used.  Exact lifted-direction coverage is enforced.  Optional symmetry
normalization uses one common tangent affine shear on an affine residue basis.
See EXACT_RING_SOUNDNESS.md for both implications and the symmetry proof.
"""
import itertools

RINGS = ("z4", "dual")


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []
        self.definitions = []

    def new(self):
        self.n += 1
        return self.n

    def add(self, clause):
        self.cl.append(list(clause))

    def and_literal(self, a, b):
        c = self.new()
        self.add([-c, a]); self.add([-c, b]); self.add([-a, -b, c])
        self.definitions.append((c, "and", [a, b], None))
        return c

    def unary_sum(self, values, limit=None):
        """Exact thresholds count>=1,...,limit; full bidirectional totalizer.

        Thresholds above limit are omitted.  Forward and backward clauses
        for every retained threshold are unchanged from the full totalizer.
        """
        values = list(values)
        if limit is None:
            limit = len(values)
        limit = min(limit, len(values))
        if limit <= 0:
            return []
        if len(values) == 1:
            return values
        split = len(values) // 2
        A = self.unary_sum(values[:split], limit)
        B = self.unary_sum(values[split:], limit)
        O = [self.new() for _ in range(limit)]
        self.definitions.extend((o, "threshold", values, k + 1) for k, o in enumerate(O))
        for i in range(len(A) + 1):
            for j in range(len(B) + 1):
                if 0 < i + j <= len(O):
                    self.add(([-A[i - 1]] if i else []) +
                             ([-B[j - 1]] if j else []) + [O[i + j - 1]])
                if i + j < len(O):
                    self.add(([A[i]] if i < len(A) else []) +
                             ([B[j]] if j < len(B) else []) + [-O[i + j]])
        return O

    def fill_auxiliaries(self, assignment):
        for variable, operation, operands, threshold in self.definitions:
            values = [assignment[abs(x)] == (x > 0) for x in operands]
            if operation == "and":
                assignment[variable] = all(values)
            elif operation == "threshold":
                assignment[variable] = sum(values) >= threshold
            else:
                raise ValueError(operation)


def quotient(x, d):
    """Linear quotient projection clearing the highest set bit of nonzero d."""
    if d <= 0:
        raise ValueError("A quotient direction must be nonzero")
    return min(x, x ^ d)


def quotient_representatives(dimension, d):
    return [x for x in range(1 << dimension) if x < (x ^ d)]


def carry(a, d, ring):
    if ring == "dual":
        return 0
    if ring == "z4":
        return a & d
    raise ValueError("Unknown ring")


def choose_anchors(support, dimension):
    """Zero and a deterministic basis of the support's residue span."""
    if 0 not in support:
        raise ValueError("The distinguished largest fibre must be at zero")
    anchors, span = [0], {0}
    for a in sorted(support):
        if a not in span:
            anchors.append(a)
            span |= {x ^ a for x in list(span)}
    if len(anchors) > dimension + 1:
        raise AssertionError("Residue rank exceeds dimension")
    return anchors


def encode_support(support, maximum, hub_min=2, total=93, dimension=5,
                   ring="z4", normalize=True):
    if ring not in RINGS or not 1 <= dimension <= 5:
        raise ValueError("Unsupported ring or dimension")
    N = 1 << dimension
    S = sorted(support)
    if len(S) != len(set(S)) or 0 not in S or any(not 0 <= a < N for a in S):
        raise ValueError("Invalid pair-active support")
    if not 2 <= hub_min <= maximum <= N or total < 0:
        raise ValueError("Invalid weight/budget domain")
    f = CNF()
    f.support = S
    f.dimension, f.ring = dimension, ring
    f.maximum, f.hub_min, f.total = maximum, hub_min, total
    f.members = {(a, x): f.new() for a in S for x in range(N)}
    f.weight_thresholds = {}
    for a in S:
        counts = f.unary_sum([f.members[a, x] for x in range(N)], maximum + 1)
        f.weight_thresholds[a] = counts
        f.add([counts[1]])
        if maximum < N:
            f.add([-counts[maximum]])
    f.add([f.weight_thresholds[0][hub_min - 1]])
    # The chosen hub is largest, with ties allowed.
    for a in S:
        if a:
            for j in range(3, maximum + 1):
                f.add([-f.weight_thresholds[a][j - 1], f.weight_thresholds[0][j - 1]])
    # Every fibre has >=2 points.  Reuse its exact remaining weight bits.
    excess = [f.weight_thresholds[a][j - 1] for a in S for j in range(3, maximum + 1)]
    allowance = total - 2 * len(S)
    if allowance < 0:
        f.add([])
    elif allowance < len(excess):
        counts = f.unary_sum(excess, allowance + 1)
        f.add([-counts[allowance]])
    f.pairs = {}
    for a in S:
        for b in S:
            if a == b:
                continue
            d = a ^ b
            for x in quotient_representatives(dimension, d):
                f.pairs[a, d, x] = f.and_literal(f.members[a, x], f.members[a, x ^ d])
    f.coverage = {(d, u): [] for d in range(1, N)
                  for u in quotient_representatives(dimension, d)}
    f.witnesses = {}
    for a, b in itertools.combinations(S, 2):
        d = a ^ b
        representatives = quotient_representatives(dimension, d)
        c = carry(a, d, ring)
        for x in representatives:
            for y in representatives:
                witness = f.and_literal(f.pairs[a, d, x], f.pairs[b, d, y])
                f.witnesses[a, b, x, y] = witness
                u = quotient(x ^ y ^ c, d)
                f.coverage[d, u].append(witness)
    for literals in f.coverage.values():
        f.add(literals)
    f.anchors = choose_anchors(S, dimension) if normalize else []
    for a in f.anchors:
        f.add([f.members[a, 0]])
    f.normalized = bool(normalize)
    return f


def encode(T, m, SPEC=None, M=None, SUBS=None, outtotal=None, hub_min=2,
           ring="z4", normalize=True, dimension=5):
    """Compatibility wrapper. Census/capacity arguments are intentionally unused."""
    return encode_support([0] + list(T), m, hub_min, 93 if outtotal is None else outtotal,
                          dimension, ring, normalize)


def write_dimacs(f, path):
    with open(path, "w") as out:
        out.write(f"p cnf {f.n} {len(f.cl)}\n")
        for clause in f.cl:
            out.write(" ".join(map(str, clause)) + " 0\n")


def actual_assignment(f, fibres):
    """Canonical full assignment from a dictionary of actual tangent subsets."""
    if set(fibres) != set(f.support):
        raise ValueError("Actual fibres must match the encoded support exactly")
    a = [False] * (f.n + 1)
    for (v, x), literal in f.members.items():
        a[literal] = x in fibres[v]
    f.fill_auxiliaries(a)
    return a


def first_failed_clauses(f, assignment, limit=10):
    bad = []
    for i, clause in enumerate(f.cl):
        if not any(assignment[abs(x)] == (x > 0) for x in clause):
            bad.append(i)
            if len(bad) >= limit:
                break
    return bad


def normalize_fibres(fibres, dimension):
    """Apply ONE common affine tangent map that puts zero in each anchor.

    Returns the translated fibres, t and columns of L.  This is the ring
    affine map z -> (I+pi*L)z + pi*t, not independent fibre translations.
    """
    anchors = choose_anchors(fibres, dimension)
    t = min(fibres[0])
    basis = anchors[1:]
    image = {0: 0}
    for a in basis:
        value = min(fibres[a]) ^ t
        image.update({x ^ a: y ^ value for x, y in list(image.items())})
    # Extend a lower-rank residue basis to the ambient space with arbitrary
    # zero images. A Kakeya support spans the full space, but this keeps the
    # normalization lemma and local tests correct for arbitrary supports.
    for bit in range(dimension):
        a = 1 << bit
        if a not in image:
            image.update({x ^ a: y for x, y in list(image.items())})
    columns = [image[1 << bit] for bit in range(dimension)]
    changed = {a: frozenset(x ^ t ^ image[a] for x in A) for a, A in fibres.items()}
    assert all(0 in changed[a] for a in anchors)
    return changed, {"t": t, "L_columns": columns, "anchors": anchors}
