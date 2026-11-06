"""Exact offset-completion CNF for fixed binary fibre shapes.

The shape A_x may be translated independently by an unknown t_x in F_2^n.
No independent rotations are allowed.  This solves only that finite fixed-
shape problem, not the unrestricted Kakeya problem.  No solver is required
to build or check a decoded witness.  PySAT is used only by solve().
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def quotient(v: int, d: int) -> int:
    pivot = d.bit_length() - 1
    if (v >> pivot) & 1:
        v ^= d
    return (v & ((1 << pivot) - 1)) | ((v >> (pivot + 1)) << pivot)


def parity(v: int) -> int:
    return v.bit_count() & 1


def affine_basis(points):
    points = sorted(points)
    if not points:
        return []
    out, rows = [points[0]], {}
    for point in points[1:]:
        v = point ^ points[0]
        while v:
            pivot = v.bit_length() - 1
            if pivot in rows:
                v ^= rows[pivot]
            else:
                rows[pivot] = v
                out.append(point)
                break
    return out


def pair_quotient(A, d):
    return {quotient(u, d) for u in A if (u ^ d) in A}


def sumset(A, B):
    return {a ^ b for a in A for b in B}


def tree_union_upper_bound(sets, quotient_size):
    """Exact-arithmetic union upper bound for arbitrary independent shifts.

    Every tree yields |union S_i| <= sum |S_i| - sum_tree |S_i intersect S_j|.
    Minimize each intersection over relative shifts, then maximize the tree
    weight.  The returned finite certificate can be checked without SAT.
    """
    if not sets:
        return {'upper_bound': 0, 'capacity_sum': 0, 'tree_weight': 0, 'tree_edges': [],
                'minimum_intersections': []}
    L = len(sets)
    minimum = [[0]*L for _ in sets]
    for i in range(L):
        for j in range(i+1, L):
            value = min(len(sets[i] & {x ^ shift for x in sets[j]})
                        for shift in range(quotient_size))
            minimum[i][j] = minimum[j][i] = value
    seen, tree = {0}, []
    while len(seen) < L:
        value, i, j = max((minimum[i][j], i, j) for i in seen for j in range(L) if j not in seen)
        tree.append([i,j,value])
        seen.add(j)
    weight = sum(v for _, _, v in tree)
    total = sum(map(len, sets))
    return {'upper_bound': total-weight, 'capacity_sum': total, 'tree_weight': weight,
            'tree_edges': tree, 'minimum_intersections': minimum}


def translated_shapes(shapes, offsets):
    return {x: {a ^ offsets.get(x, 0) for a in A} for x, A in shapes.items()}


def coverage_counts(n, shapes, ring):
    """Exact quotient coverage and individual edge sumset cardinalities."""
    N, Q = 1 << n, 1 << (n - 1)
    rows = []
    for d in range(1, N):
        covered, total, edges = set(), 0, []
        for x in sorted(shapes):
            y = x ^ d
            if x < y and y in shapes:
                P = pair_quotient(shapes[x], d)
                R = pair_quotient(shapes[y], d)
                S = sumset(P, R)
                carry = quotient(x & d, d) if ring == "z4" else 0
                covered.update(s ^ carry for s in S)
                total += len(S)
                edges.append({"x": x, "y": y, "pair_counts": [len(P), len(R)],
                              "sumset_size": len(S), "sumset": sorted(S)})
        rows.append({"d": d, "capacity_sum": total,
                     "covered": sorted(covered), "missing": sorted(set(range(Q)) - covered),
                     "edges": edges})
    return rows


def ring_add(u, v, ring):
    a, b = u
    c, d = v
    return (a ^ c, b ^ d ^ ((a & c) if ring == "z4" else 0))


def scalar_mul(s, v, ring):
    a, b = v
    low, high = s & 1, (s >> 1) & 1
    return (a if low else 0, (b if low else 0) ^ (a if high else 0))


def direct_ring_verify(n, shapes, ring, residue_directions=None):
    """Independent arithmetic check, including every primitive vector."""
    N = 1 << n
    directions = list(range(1, N)) if residue_directions is None else sorted(set(residue_directions))
    K = {(x, a) for x, A in shapes.items() for a in A}
    missing = []
    for a in directions:
        for b in range(N):
            v = (a, b)
            if not any(all(ring_add(p, scalar_mul(t, v, ring), ring) in K
                           for t in range(4)) for p in K):
                missing.append([a, b])
    return {"all_required_directions_covered": not missing,
            "full_kakeya": not missing and len(directions) == N - 1,
            "primitive_vectors_checked": N * len(directions),
            "projective_directions_checked": N * len(directions) // 2,
            "missing_primitive_vectors": missing}


class CompletionCNF:
    def __init__(self, n, shapes, ring, fix_affine_gauge=True, residue_directions=None):
        if ring not in ("dual", "z4"):
            raise ValueError(ring)
        self.n, self.N, self.Q = n, 1 << n, 1 << (n - 1)
        self.shapes = {int(x): set(A) for x, A in shapes.items() if A}
        assert all(0 <= x < self.N and all(0 <= a < self.N for a in A)
                   for x, A in self.shapes.items())
        self.ring, self.clauses, self.vars = ring, [], {}
        self.directions = list(range(1, self.N)) if residue_directions is None else sorted(set(residue_directions))
        assert all(1 <= d < self.N for d in self.directions)
        self.basis = affine_basis(self.shapes) if fix_affine_gauge else []
        for x in self.shapes:
            for j in range(n):
                self.var(("t", x, j))
        for x in self.basis:
            for j in range(n):
                self.clauses.append([-self.var(("t", x, j))])
        self.local_failures, self.edge_data, self.tree_prechecks = [], [], []
        self._build()

    def var(self, key):
        if key not in self.vars:
            self.vars[key] = len(self.vars) + 1
        return self.vars[key]

    def xor(self, out, inputs):
        # Truth-table equivalence is small: at most four input bits.
        for bits in itertools.product((0, 1), repeat=len(inputs)):
            clause = [-v if b else v for v, b in zip(inputs, bits)]
            clause.append(out if sum(bits) % 2 else -out)
            self.clauses.append(clause)

    def _build(self):
        for d in self.directions:
            cover = [[] for _ in range(self.Q)]
            universally_covered = False
            capacity = 0
            tree_sets, tree_base_edges = [], []
            pivot = d.bit_length() - 1
            for x in sorted(self.shapes):
                y = x ^ d
                if x >= y or y not in self.shapes:
                    continue
                P, R = pair_quotient(self.shapes[x], d), pair_quotient(self.shapes[y], d)
                S = sumset(P, R)
                capacity += len(S)
                if not S:
                    continue
                tree_sets.append(S)
                tree_base_edges.append([x,y])
                if len(S) == self.Q:
                    universally_covered = True
                    continue
                carry = quotient(x & d, d) if self.ring == "z4" else 0
                S = {v ^ carry for v in S}
                bits = []
                for j in range(self.n):
                    if j == pivot:
                        continue
                    out = self.var(("quotient_difference", x, y, j))
                    inputs = [self.var(("t", x, j)), self.var(("t", y, j))]
                    if (d >> j) & 1:
                        inputs += [self.var(("t", x, pivot)), self.var(("t", y, pivot))]
                    self.xor(out, inputs)
                    bits.append(out)
                shift_vars = []
                for shift in range(self.Q):
                    indicator = self.var(("shift", x, y, shift))
                    match_literals = [v if (shift >> j) & 1 else -v for j, v in enumerate(bits)]
                    # indicator <=> all quotient bits match shift.
                    for literal in match_literals:
                        self.clauses.append([-indicator, literal])
                    self.clauses.append([indicator] + [-v for v in match_literals])
                    shift_vars.append(indicator)
                    for covered in S:
                        cover[covered ^ shift].append(indicator)
                self.edge_data.append({"d": d, "x": x, "y": y, "sumset": sorted(S),
                                       "shift_variables": shift_vars})
            if capacity < self.Q:
                self.local_failures.append({"d": d, "capacity": capacity, "required": self.Q})
            tree_bound = tree_union_upper_bound(tree_sets, self.Q)
            self.tree_prechecks.append({'d': d, 'base_edges': tree_base_edges,
                                        'canonical_sumsets': [sorted(S) for S in tree_sets],
                                        'required': self.Q, **tree_bound})
            if not universally_covered:
                self.clauses.extend(cover)

    def write(self, path):
        path = Path(path)
        with path.open("w") as out:
            out.write(f"p cnf {len(self.vars)} {len(self.clauses)}\n")
            for clause in self.clauses:
                out.write(" ".join(map(str, clause)) + (" " if clause else "") + "0\n")

    def decode(self, model):
        true = {v for v in model if v > 0}
        return {x: sum(1 << j for j in range(self.n)
                       if self.var(("t", x, j)) in true) for x in self.shapes}

    def solve(self, outdir, name="g4", seconds=30):
        from pysat.solvers import Solver
        import threading
        import time
        outdir = Path(outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        cnf = outdir / "input.cnf"
        self.write(cnf)
        start = time.monotonic()
        with Solver(name=name, bootstrap_with=self.clauses, with_proof=True) as solver:
            timer = threading.Timer(seconds, solver.interrupt)
            timer.start()
            try:
                answer = solver.solve_limited(expect_interrupt=True)
            finally:
                timer.cancel()
            result = {"status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                      "n": self.n, "ring": self.ring,
                      "weight": sum(map(len, self.shapes.values())), "support": sorted(self.shapes),
                      "variables": len(self.vars), "clauses": len(self.clauses),
                      "affine_gauge_basis": self.basis, "seconds": time.monotonic() - start,
                      "required_residue_directions": self.directions,
                      "local_sumset_failures": self.local_failures,
                      "tree_overlap_failures": [r for r in self.tree_prechecks if r['upper_bound'] < self.Q],
                      "cnf_sha256": hashlib.sha256(cnf.read_bytes()).hexdigest(),
                      "fixed_shapes": {str(x): sorted(A) for x, A in self.shapes.items()},
                      "scope": "Independent translations of these fixed labelled fibre shapes, covering only the listed residue directions."}
            if answer is True:
                offsets = self.decode(solver.get_model())
                translated = translated_shapes(self.shapes, offsets)
                rows = coverage_counts(self.n, translated, self.ring)
                assert all(not row["missing"] for row in rows if row['d'] in self.directions)
                direct = direct_ring_verify(self.n, translated, self.ring, self.directions)
                assert direct["all_required_directions_covered"]
                result.update({"offsets": offsets, "direct_ring_verification": direct,
                               "witness_fibres": {str(x): sorted(A) for x, A in translated.items()}})
            elif answer is False:
                proof = outdir / "proof.drat"
                proof_lines = solver.get_proof()
                # Some solvers return no trace if bootstrap unit propagation
                # already found the conflict.  An explicit terminal empty
                # clause is still independently checkable against the CNF.
                if not any(line.strip() == '0' for line in proof_lines):
                    proof_lines.append('0')
                proof.write_text("\n".join(proof_lines) + "\n")
                result.update({"proof_sha256": hashlib.sha256(proof.read_bytes()).hexdigest(),
                               "proof_file": "proof.drat",
                               "proof_check": "Pending independent RUP/DRAT check; n2 enumeration also available."})
        (outdir / "result.json").write_text(json.dumps(result, indent=2) + "\n")
        return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="JSON with n, ring, fibres dictionary")
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--seconds", type=float, default=30)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    model = CompletionCNF(data["n"], data["fibres"], data["ring"],
                          residue_directions=data.get('required_residue_directions'))
    print(json.dumps(model.solve(args.outdir, seconds=args.seconds), indent=2))


if __name__ == "__main__":
    main()
