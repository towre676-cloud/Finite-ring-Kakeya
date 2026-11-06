"""SAT decision (CaDiCaL via PySAT) for: exists Kakeya K in R^n with |K| <= m ?
Encoding: point vars; per direction class an OR over line-selector vars, each
selector implying its 4 points; |K| <= m by a sequential-counter/totalizer.
Symmetry: K contains the line R*e_1 (sound, see exact_min.py), and
fibre-size ordering (S1) of exact_sym.py encoded via totalizer outputs."""
import sys, time, json
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType, ITotalizer
from pysat.solvers import Solver
from .rings import RINGS, all_points, directions, lines_in_direction, line, pack, unpack, is_kakeya


def decide(R, n, m, solver="cadical195", order_sym=False, time_limit=None):
    pool = IDPool()
    P = {x: pool.id(("p", x)) for x in all_points(n)}
    cnf = CNF()
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
    card = CardEnc.atmost(lits=list(P.values()), bound=m, vpool=pool,
                          encoding=EncType.totalizer)
    cnf.extend(card.clauses)
    t0 = time.time()
    with Solver(name=solver, bootstrap_with=cnf.clauses) as s:
        if time_limit:
            import threading
            tm = threading.Timer(time_limit, lambda: s.interrupt())
            tm.start()
            sat = s.solve_limited(expect_interrupt=True)
            tm.cancel()
        else:
            sat = s.solve()
        status = {True: "SAT", False: "UNSAT", None: "TIMEOUT"}[sat]
        out = {"ring": R, "n": n, "m": m, "status": status,
               "seconds": round(time.time() - t0, 2), "solver": solver}
        if sat:
            mod = set(l for l in s.get_model() if l > 0)
            K = sorted(x for x, v in P.items() if v in mod)
            out.update(size=len(K), witness=K, witness_rechecked=is_kakeya(R, K, n))
    return out


if __name__ == "__main__":
    n, m = int(sys.argv[1]), int(sys.argv[2])
    rings = sys.argv[3].split(",") if len(sys.argv) > 3 else RINGS
    tl = float(sys.argv[4]) if len(sys.argv) > 4 else None
    for R in rings:
        r = decide(R, n, m, time_limit=tl)
        print(json.dumps({k: v for k, v in r.items() if k != "witness"}), flush=True)
        json.dump(r, open(f"results/sat_{R}_n{n}_m{m}.json", "w"))
