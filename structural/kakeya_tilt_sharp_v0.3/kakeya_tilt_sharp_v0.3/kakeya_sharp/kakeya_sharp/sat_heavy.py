"""Exact point-level SAT for one heavy-support case of the no-full-fibre
problem: residues in B carry 3..N-1 points, all other residues at most 2,
total <= ub, every direction has a line.  Ring-specific (Z4 or D2).

Kernel normalisation (sound): x -> (I + pi M) x + pi c shifts fibre a by
c + M a and fixes every residue, hence B.  For an affine basis b_0..b_n of
span(B) inside B the shifts c + M b_i are arbitrary, so WLOG 0 in A_{b_i}.

Usage: python -m kakeya_sharp.sat_heavy n ub ring caseindex [seconds]
(case index into results/heavy_orbits_n{n}_ub{ub}.json)."""
import sys, json, time, os, signal
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from .rings import all_points, directions, lines_in_direction, pack, is_kakeya


def affine_basis(B):
    base = B[0]
    vecs, basis = [], [base]
    span = {0}
    for b in B[1:]:
        d = b ^ base
        if d not in span:
            span |= {s ^ d for s in span}
            basis.append(b)
    return basis


def build(R, n, ub, B):
    N = 1 << n
    Bs = set(B)
    pool = IDPool()
    P = {x: pool.id(("p", x)) for x in all_points(n)}
    cnf = CNF()
    for b in affine_basis(B):
        cnf.append([P[pack(b, 0, n)]])
    for a in range(N):
        fib = [P[pack(a, u, n)] for u in range(N)]
        if a in Bs:
            cnf.extend(CardEnc.atleast(fib, 3, vpool=pool, encoding=EncType.seqcounter).clauses)
            cnf.append([-x for x in fib])                     # no full fibre
        else:
            cnf.extend(CardEnc.atmost(fib, 2, vpool=pool, encoding=EncType.seqcounter).clauses)
    for b in directions(n):
        ys = []
        for L in lines_in_direction(R, b, n):
            y = pool.id(("l", b, L))
            for x in L:
                cnf.append([-y, P[x]])
            ys.append(y)
        cnf.append(ys)
    cnf.extend(CardEnc.atmost(list(P.values()), ub, vpool=pool, encoding=EncType.seqcounter).clauses)
    return cnf, P


if __name__ == "__main__":
    n, ub, R, idx = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], int(sys.argv[4])
    case = json.load(open(f"results/heavy_orbits_n{n}_ub{ub}.json"))[idx]
    cnf, P = build(R, n, ub, case["B"])
    t0 = time.time()
    with Solver(name="cadical153", bootstrap_with=cnf.clauses) as s:
        sat = s.solve()
        out = {"ring": R, "n": n, "ub": ub, "case": idx, "B": case["B"], "h": case["h"],
               "status": "SAT" if sat else "UNSAT", "seconds": round(time.time() - t0, 2),
               "vars": cnf.nv, "clauses": len(cnf.clauses)}
        if sat:
            mod = set(l for l in s.get_model() if l > 0)
            K = sorted(x for x, v in P.items() if v in mod)
            out.update(size=len(K), witness=K, witness_rechecked=is_kakeya(R, K, n))
    print(json.dumps({k: v for k, v in out.items() if k != "witness"}), flush=True)
    json.dump(out, open(f"results/satheavy_{R}_n{n}_ub{ub}_c{idx}.json", "w"))
