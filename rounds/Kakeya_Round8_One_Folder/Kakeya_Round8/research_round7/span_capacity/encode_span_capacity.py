"""Append common-direction-space edge capacity bounds to the frozen joint CNF.

The Round6 baseline is unchanged.  A second, small family of capacity
variables carries the additional bounds, avoiding dependence on hidden
variable numbering in the baseline.  Exact CNF UNSAT still needs a separate
checked refutation.  See SPAN_CAPACITY_LEMMA.md for the one-way argument.
"""
from pathlib import Path
import importlib.util
import itertools
from collections import defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
_spec = importlib.util.spec_from_file_location(
    "round7_span_base", ROOT / "research_round6/encoder_audit/encode_maximal_cosets.py")
BASE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(BASE)

load_spectra = BASE.load_spectra
load_M = BASE.load_M
all_subspaces = BASE.all_subspaces
write_dimacs = BASE.write_dimacs


def append_span_capacity(f, S, M, SUBS, dimensions=(2, 3, 4)):
    """For H_a,H_b contained in L, cap(a,b) <= 2**(dim(L)-1).

    Only L containing the edge direction is needed.  All dimensions are
    proper nonzero binary subspaces.  Containment selectors are exact ORs
    of the already selected H choices, so no fibre type is guessed.
    """
    dimensions = tuple(sorted(set(dimensions)))
    if not dimensions or any(k not in (1, 2, 3, 4) for k in dimensions):
        raise ValueError("Use a nonempty subset of dimensions1..4")
    superspaces = [L for L in SUBS if len(L).bit_length() - 1 in dimensions]
    inside = {}
    start_n, start_cl = f.n, len(f.cl)
    for v in S:
        for L in superspaces:
            u = f.new()
            inside[v, L] = u
            options = [h for H, h in f.h_selectors[v].items() if H <= L]
            f.add([-u] + options)
            for h in options:
                f.add([-h, u])
    coverage = defaultdict(list)
    edge_bits = {}
    span_rows = 0
    for a, b in itertools.combinations(S, 2):
        d = a ^ b
        bits = [f.new() for _ in range(16)]
        edge_bits[a, b] = bits
        for j in range(15):
            f.add([-bits[j + 1], bits[j]])
        a_values = [k for k in range(17) if (a, d, k) in f.y]
        b_values = [k for k in range(17) if (b, d, k) in f.y]
        for p in a_values:
            for q in b_values:
                cap = M[p][q]
                if cap < 16:
                    f.add([-bits[cap], -f.y[a, d, p], -f.y[b, d, q]])
        for L in superspaces:
            if d in L:
                cap = len(L) // 2
                f.add([-inside[a, L], -inside[b, L], -bits[cap]])
                span_rows += 1
        coverage[d].extend(bits)
    coverage_requirements = []
    for d in range(1, 32):
        total = f.unary_sum(coverage[d])
        coverage_requirements.append(len(f.cl))
        f.add([total[15]] if len(total) >= 16 else [])
    f.span_inside = inside
    f.span_edge_bits = edge_bits
    f.span_coverage_requirements = coverage_requirements
    f.span_metadata = {
        "dimensions": list(dimensions), "containment_variables": len(inside),
        "new_variables": f.n - start_n, "new_clauses": len(f.cl) - start_cl,
        "span_capacity_rows": span_rows,
        "new_capacity_bits": sum(map(len, edge_bits.values())),
    }
    return f


def encode(T, m, SPEC, M, SUBS, outtotal=None, hub_min=2,
           strengthen=True, dimensions=(2, 3, 4)):
    f = BASE.encode(T, m, SPEC, M, SUBS, outtotal=outtotal,
                    hub_min=hub_min, strengthen=False)
    if strengthen:
        append_span_capacity(f, [0] + list(T), M, SUBS, dimensions)
    return f
