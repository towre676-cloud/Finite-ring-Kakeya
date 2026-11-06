"""Append exact labelled models for two rank-four fibre types.

The frozen Round 6 baseline is called with its optional maximal-coset rows
disabled.  Every appended clause is gated by one specific spectrum selector.
No restrictions on the two auxiliary models survive when their type is off.
See DENSE_ENCODER_SOUNDNESS.md for the one-way interpretation proof.
"""
from pathlib import Path
import importlib.util
import itertools

ROOT = Path(__file__).resolve().parents[2]
BASE_PATH = ROOT / "research_round6/encoder_audit/encode_maximal_cosets.py"
spec = importlib.util.spec_from_file_location("round7_dense_frozen_base", BASE_PATH)
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)

CNF = BASE.CNF
load_spectra = BASE.load_spectra
load_M = BASE.load_M
all_subspaces = BASE.all_subspaces
write_dimacs = BASE.write_dimacs


class Gated:
    """CNF primitives with a compulsory leading negative type literal.

    ``definitions`` records a canonical assignment to internal auxiliaries;
    it is used for independent clause-by-clause constructive validation.
    It has no role in SAT search or proof checking.
    """

    def __init__(self, f, gate):
        self.f, self.gate = f, gate
        self.definitions = []
        self.primary = []

    def new(self):
        v = self.f.new()
        self.primary.append(v)
        return v

    def aux(self, operation, operands, parameter=None):
        v = self.f.new()
        self.definitions.append((v, operation, list(operands), parameter))
        return v

    def add(self, clause):
        self.f.add([-self.gate] + list(clause))

    def exactly_one(self, values):
        self.add(values)
        if len(values) <= 6:
            for a, b in itertools.combinations(values, 2):
                self.add([-a, -b])
            return
        previous = None
        for x in values:
            operands = [x] if previous is None else [previous, x]
            p = self.aux("or", operands)
            self.add([-x, p])
            if previous is not None:
                self.add([-previous, p])
                self.add([-x, -previous])
            previous = p

    def unary_sum(self, values):
        if not values:
            return []
        if len(values) == 1:
            return list(values)
        split = len(values) // 2
        A = self.unary_sum(values[:split])
        B = self.unary_sum(values[split:])
        O = [self.aux("threshold", values, k + 1) for k in range(len(values))]
        for i in range(len(A) + 1):
            for j in range(len(B) + 1):
                if i + j:
                    self.add(([-A[i - 1]] if i else []) +
                             ([-B[j - 1]] if j else []) + [O[i + j - 1]])
                if i + j < len(O):
                    self.add(([A[i]] if i < len(A) else []) +
                             ([B[j]] if j < len(B) else []) + [-O[i + j]])
        return O

    def or_literal(self, values):
        u = self.aux("or", values)
        self.add([-u] + list(values))
        for x in values:
            self.add([-x, u])
        return u

    def parity_zero(self, values):
        if not values:
            return
        a = values[0]
        for b in values[1:]:
            z = self.aux("xor", [a, b])
            self.add([-a, -b, -z])
            self.add([a, b, -z])
            self.add([a, -b, z])
            self.add([-a, b, z])
            a = z
        self.add([-a])

    def complete_assignment(self, assignment):
        """Fill auxiliaries after the caller assigns selectors and primaries."""
        for variable, operation, operands, parameter in self.definitions:
            bits = [assignment[abs(x)] == (x > 0) for x in operands]
            if operation == "or":
                value = any(bits)
            elif operation == "threshold":
                value = sum(bits) >= parameter
            elif operation == "xor":
                value = bool(sum(bits) % 2)
            else:
                raise ValueError(operation)
            assignment[variable] = value


def type_indices(SPEC):
    h11 = [16, 0, 0, 5, 10] + [0] * 12
    h12 = [16, 0, 0, 0, 9, 6] + [0] * 11
    indices = {}
    for name, signature in [("w11_q205", (11, h11, 4, 4)),
                            ("w12_q294", (12, h12, 4, 4))]:
        choices = [i for i, entry in enumerate(SPEC) if tuple(entry) == signature]
        if len(choices) != 1:
            raise ValueError("Expected exactly one audited spectrum: " + name)
        indices[name] = choices[0]
    return indices


def append_dense_constraints(f, S, D, SPEC, SUBS, z, y, h_selectors):
    """Extend in place; returned structures are only introspection/witness data."""
    indices = type_indices(SPEC)
    threes = [H for H in SUBS if len(H) == 8]
    models = {}
    first_clause = len(f.cl)
    first_variable = f.n
    for v in S:
        hs = h_selectors[v]
        for name in ["w11_q205", "w12_q294"]:
            if (v, indices[name]) not in z:
                continue
            gate = z[v, indices[name]]
            g = Gated(f, gate)
            begin = len(f.cl)
            model = {"gate": gate, "builder": g, "type": name, "vertex": v}
            g.add([hs[H] for H in SUBS if len(H) == 16])
            if name == "w11_q205":
                # A five-element set of nonzero vectors with sum zero is
                # automatically a binary five-circuit.  Indicator variables
                # enforce distinctness without introducing ordering symmetry.
                circuit = {d: g.new() for d in range(1, 32)}
                model["circuit"] = circuit
                counts = g.unary_sum(list(circuit.values()))
                g.add([counts[4]])
                g.add([-counts[5]])
                for bit in range(5):
                    g.parity_zero([circuit[d] for d in range(1, 32) if d >> bit & 1])
                h_mem = {
                    d: g.or_literal([hs[H] for H in SUBS if d in H])
                    for d in range(1, 32)
                }
                for d in range(1, 32):
                    g.add([-circuit[d], h_mem[d]])
                for d in D[v]:
                    c, h = circuit[d], h_mem[d]
                    p0, p3, p4 = [y[v, d, k] for k in [0, 3, 4]]
                    g.add([-p3, c]); g.add([-c, p3])
                    g.add([-p4, h]); g.add([-p4, -c])
                    g.add([-h, c, p4])
                    g.add([-p0, -h]); g.add([h, p0])
                    for k in range(17):
                        if (v, d, k) in y and k not in [0, 3, 4]:
                            g.add([-y[v, d, k]])
                model["h_mem"] = h_mem
            else:
                js = {J: g.new() for J in threes}
                us = {u: g.new() for u in range(1, 32)}
                model.update(j_selectors=js, u_selectors=us)
                g.exactly_one(list(js.values()))
                g.exactly_one(list(us.values()))
                # The selected J is a three-space in the already-selected H.
                for J, j in js.items():
                    g.add([-j] + [hs[H] for H in SUBS if len(H) == 16 and J <= H])
                for u, choice in us.items():
                    g.add([-choice] + [js[J] for J in threes if u in J])
                h_mem, j_mem = {}, {}
                for d in D[v]:
                    h = h_mem[d] = g.or_literal([hs[H] for H in SUBS if d in H])
                    j = j_mem[d] = g.or_literal([js[J] for J in threes if d in J])
                    u = us[d]
                    p0, p4, p5 = [y[v, d, k] for k in [0, 4, 5]]
                    # p5 <-> (d in J and d != u).
                    g.add([-p5, j]); g.add([-p5, -u])
                    g.add([-j, u, p5])
                    # p4 <-> (d in H and (d outside J or d=u)).
                    g.add([-p4, h]); g.add([-p4, -j, u])
                    g.add([-h, j, p4]); g.add([-h, -u, p4])
                    g.add([-p0, -h]); g.add([h, p0])
                    for k in range(17):
                        if (v, d, k) in y and k not in [0, 4, 5]:
                            g.add([-y[v, d, k]])
                model.update(h_mem=h_mem, j_mem=j_mem)
            model["clause_range"] = (begin, len(f.cl))
            # This is a construction invariant, also checked by the replay.
            if not all(-gate in c for c in f.cl[begin:]):
                raise AssertionError("An auxiliary clause escaped its type gate")
            models[v, name] = model
    f.dense_extra_variables = f.n - first_variable
    f.dense_extra_clauses = len(f.cl) - first_clause
    return models


def encode(T, m, SPEC, M, SUBS, outtotal=None, hub_min=2, strengthen=True):
    f = BASE.encode(T, m, SPEC, M, SUBS, outtotal=outtotal,
                    hub_min=hub_min, strengthen=False)
    f.dense_models = {}
    f.dense_extra_variables = f.dense_extra_clauses = 0
    if strengthen:
        S = [0] + list(T)
        D = {v: [v ^ b for b in S if b != v] for v in S}
        f.dense_models = append_dense_constraints(
            f, S, D, SPEC, SUBS, f.z, f.y, f.h_selectors)
    return f
