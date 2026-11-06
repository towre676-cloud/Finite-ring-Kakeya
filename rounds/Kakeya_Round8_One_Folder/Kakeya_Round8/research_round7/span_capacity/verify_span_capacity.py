#!/usr/bin/env python3
"""Construct actual assignments for the new rows; replay finite geometry checks."""
from pathlib import Path
import gc
import hashlib
import importlib.util
import itertools
import json
import random
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


E = module("span_encoder_test", HERE / "encode_span_capacity.py")
B = module("span_original_baseline", ROOT / "research_round6/joint_maxima/encode_joint_maxima.py")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(f):
    h = hashlib.sha256(f"p cnf {f.n} {len(f.cl)}\n".encode())
    for cl in f.cl:
        h.update((" ".join(map(str, cl)) + " 0\n").encode())
    return h.hexdigest()


def direction_space(A):
    t = min(A)
    H = {0}
    for a in sorted(A):
        H |= {x ^ a ^ t for x in H}
    return frozenset(H)


def quotient(x, d):
    return min(x, x ^ d)


def pairs(A, d):
    return {quotient(a, d) for a in A if a ^ d in A}


def pair_sum(P, Q, d):
    return {quotient(p ^ q, d) for p in P for q in Q}


def geometry(subspaces):
    rng = random.Random(2026102807)
    shapes = [frozenset(H) for H in subspaces if len(H) >= 2]
    shapes += [frozenset(rng.sample(range(32), rng.randrange(2, 33))) for _ in range(400)]
    checks = 0
    sharp = set()
    for index in range(3000):
        A, C = rng.choice(shapes), rng.choice(shapes)
        H, J = direction_space(A), direction_space(C)
        for d in range(1, 32):
            P, Q = pairs(A, d), pairs(C, d)
            n = len(pair_sum(P, Q, d))
            if P and Q:
                if d not in H or d not in J:
                    raise AssertionError("Positive pair direction outside hull")
                bound = len({h ^ j for h in H for j in J}) // 2
                if n > bound:
                    raise AssertionError(("Sumset escaped span", A, C, d, n, bound))
                if n == bound:
                    sharp.add(bound)
            elif n != 0:
                raise AssertionError("Empty summand gave nonempty sumset")
            checks += 1
    return {"ordered_set_pair_samples": 3000, "direction_checks": checks,
            "observed_sharp_bounds": sorted(sharp), "seed": 2026102807}


class TrackedCNF(E.BASE.CNF):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def unary_sum(self, lits):
        result = super().unary_sum(lits)
        self.nodes.append((list(lits), list(result)))
        return result


def concrete_extension(fibres, subspaces, M, require_coverage=False):
    S = sorted(fibres)
    f = TrackedCNF()
    f.y = {(v, v ^ b, k): f.new() for v in S for b in S if b != v for k in range(17)}
    f.h_selectors = {v: {H: f.new() for H in subspaces} for v in S}
    E.append_span_capacity(f, S, M, subspaces)
    assignment = {}
    actual_H = {v: direction_space(fibres[v]) for v in S}
    actual_P = {(v, v ^ b): pairs(fibres[v], v ^ b) for v in S for b in S if b != v}
    for (v, d, k), lit in f.y.items():
        assignment[lit] = len(actual_P[v, d]) == k
    for v, selectors in f.h_selectors.items():
        for H, lit in selectors.items():
            assignment[lit] = H == actual_H[v]
    for (v, L), lit in f.span_inside.items():
        assignment[lit] = actual_H[v] <= L
    for (a, b), bits in f.span_edge_bits.items():
        d = a ^ b
        cap = len(pair_sum(actual_P[a, d], actual_P[b, d], d))
        for j, lit in enumerate(bits):
            assignment[lit] = cap >= j + 1
    for inputs, outputs in f.nodes:
        total = sum(assignment[lit] for lit in inputs)
        for j, lit in enumerate(outputs):
            value = total >= j + 1
            if lit in assignment and assignment[lit] != value:
                raise AssertionError("Conflicting totalizer assignment")
            assignment[lit] = value
    if len(assignment) != f.n:
        raise AssertionError("Missing auxiliary assignment")
    excluded = set() if require_coverage else set(f.span_coverage_requirements)
    bad = [i for i, clause in enumerate(f.cl) if i not in excluded
           and not any(assignment[abs(lit)] == (lit > 0) for lit in clause)]
    if bad:
        raise AssertionError(("Real fibres rejected by new rows", S, bad[:5]))
    return f, assignment


def assignment_checks(subspaces, M):
    rng = random.Random(2026102808)
    checked = 0
    for trial in range(40):
        residues = sorted(rng.sample(range(32), 2 + trial % 3))
        fibres = {v: set(rng.sample(range(32), rng.randrange(2, 33))) for v in residues}
        concrete_extension(fibres, subspaces, M)
        checked += 1
    # The explicit 94-point star is a genuine positive control in both rings.
    star = {0: set(range(32))}
    star.update({v: {0, v} for v in range(1, 32)})
    f, a = concrete_extension(star, subspaces, M, require_coverage=True)
    star_size = sum(map(len, star.values()))
    if star_size != 94:
        raise AssertionError("Wrong star")
    del f, a
    gc.collect()
    # Four-pair cube endpoints with sum dimension4 cannot have capacity9.
    A = set(range(8))
    C = {0, 1, 2, 3, 8, 9, 10, 11}
    f, assignment = concrete_extension({0: A, 1: C}, subspaces, M)
    changed = dict(assignment)
    changed[f.span_edge_bits[0, 1][8]] = True
    failing = [clause for clause in f.cl
               if not any(changed[abs(lit)] == (lit > 0) for lit in clause)]
    if not any(len(clause) == 3 and -f.span_edge_bits[0, 1][8] in clause
               for clause in failing):
        raise AssertionError("Impossible ninth lifted label was not rejected")
    L = frozenset(range(16))
    changed = dict(assignment)
    changed[f.span_inside[0, L]] = False
    if not any(not any(changed[abs(lit)] == (lit > 0) for lit in clause) for clause in f.cl):
        raise AssertionError("False containment flag not rejected")
    return {"arbitrary_concrete_fibre_collections": checked,
            "all_auxiliaries_assigned": True, "genuine_star_size": star_size,
            "star_all31_coverage_requirements_passed": True,
            "negative_controls_rejected": 2}


def baseline_identity(subspaces, SPEC, M):
    T = [1, 2, 4, 7, 8, 11, 12, 15, 16, 17, 18, 19]
    b = B.encode(T, 18, SPEC, M, subspaces, hub_min=2)
    old = digest(b)
    old_n, old_cl = b.n, len(b.cl)
    del b
    gc.collect()
    f = E.encode(T, 18, SPEC, M, subspaces, hub_min=2, strengthen=False)
    if digest(f) != old:
        raise AssertionError("Disabled wrapper changed frozen baseline")
    E.append_span_capacity(f, [0] + T, M, subspaces)
    result = {"support_mask": sum(1 << v for v in T), "baseline_sha256": old,
              "baseline_variables": old_n, "baseline_clauses": old_cl,
              "strengthened_sha256": digest(f), "variables": f.n,
              "clauses": len(f.cl), "extension": f.span_metadata}
    return result


def main():
    started = time.monotonic()
    target = HERE / "SPAN_CAPACITY_REPLAY.json"
    target.write_text(json.dumps({"status": "RUNNING"}) + "\n")
    try:
        subspaces = E.all_subspaces()
        data = ROOT / "research_round6/imported_claude_round4/data"
        SPEC, M = E.load_spectra(data / "spec32.csv"), E.load_M(data / "Mtable.txt")
        result = {"status": "PASS_CONSTRUCTIVE_SPAN_CAPACITY_CHECKS",
                  "scope": "Finite corroboration of the written proof; no support exclusion claimed.",
                  "geometry": geometry(subspaces),
                  "assignments": assignment_checks(subspaces, M),
                  "baseline_identity": baseline_identity(subspaces, SPEC, M),
                  "source_hashes": {str(p.relative_to(ROOT)): sha(p) for p in [
                      HERE / "encode_span_capacity.py", Path(__file__),
                      ROOT / "research_round6/encoder_audit/encode_maximal_cosets.py",
                      ROOT / "research_round6/joint_maxima/encode_joint_maxima.py",
                      data / "spec32.csv", data / "Mtable.txt"]},
                  "seconds": round(time.monotonic() - started, 6)}
    except Exception as error:
        result = {"status": "FAIL", "error": repr(error)}
        target.write_text(json.dumps(result, indent=2) + "\n")
        raise
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
