"""Case-split SAT on the exact line encoding (CaDiCaL via PySAT), with optional
DRAT proof emission.  Cases are expressed as extra clauses:

  nofull       : no residue fibre is full (every fibre misses a point)
  full0        : fibre 0 is full (WLOG for the full-fibre case, by translation)
  heavy_max=k  : at most k fibres have >= 3 points  (not used by default)

Symmetry: in case 'nofull' we fix the line R*e_1 (sound, because the case is
invariant under every affine automorphism of R^n).  In case 'full0' no line is
fixed: a line of direction e_1 may live over any residue pair {a, a+e_1}, and
moving it to {0, e_1} would move the full fibre."""
import sys, time, json, os
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver
from .rings import RINGS, all_points, directions, lines_in_direction, line, pack, unpack, is_kakeya


def build(R, n, m, case):
    N = 1 << n
    pool = IDPool()
    P = {x: pool.id(("p", x)) for x in all_points(n)}
    cnf = CNF()
    if case != "full0":
        # sound only for affine-invariant cases; see module docstring
        for x in line(R, 0, pack(1, 0, n), n):
            cnf.append([P[x]])
    for b in directions(n):
        ys = []
        for L in lines_in_direction(R, b, n):
            y = pool.id(("l", b, L))
            for x in L:
                cnf.append([-y, P[x]])
            ys.append(y)
        cnf.append(ys)
    if case == "nofull":
        for a in range(N):
            cnf.append([-P[pack(a, u, n)] for u in range(N)])
    elif case == "full0":
        for u in range(N):
            cnf.append([P[pack(0, u, n)]])
    card = CardEnc.atmost(lits=list(P.values()), bound=m, vpool=pool, encoding=EncType.seqcounter)
    cnf.extend(card.clauses)
    return cnf, P


def decide(R, n, m, case, proof=None, solver="cadical153"):
    cnf, P = build(R, n, m, case)
    t0 = time.time()
    out = {"ring": R, "n": n, "m": m, "case": case, "vars": cnf.nv, "clauses": len(cnf.clauses)}
    with Solver(name=solver, bootstrap_with=cnf.clauses, with_proof=bool(proof)) as s:
        sat = s.solve()
        out["status"] = "SAT" if sat else "UNSAT"
        out["seconds"] = round(time.time() - t0, 2)
        out["solver"] = solver
        if sat:
            mod = set(l for l in s.get_model() if l > 0)
            K = sorted(x for x, v in P.items() if v in mod)
            out.update(size=len(K), witness=K, witness_rechecked=is_kakeya(R, K, n))
        elif proof:
            cnf.to_file(proof + ".cnf")
            with open(proof + ".drat", "w") as f:
                for line_ in s.get_proof():
                    f.write(line_ + "\n")
            out["proof"] = os.path.basename(proof)
    return out


if __name__ == "__main__":
    n, m, case = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    rings = sys.argv[4].split(",") if len(sys.argv) > 4 else RINGS
    proofdir = sys.argv[5] if len(sys.argv) > 5 else None
    for R in rings:
        pf = os.path.join(proofdir, f"{case}_{R}_n{n}_m{m}") if proofdir else None
        r = decide(R, n, m, case, pf)
        print(json.dumps({k: v for k, v in r.items() if k != "witness"}), flush=True)
        json.dump(r, open(f"results/sat_{case}_{R}_n{n}_m{m}.json", "w"))
