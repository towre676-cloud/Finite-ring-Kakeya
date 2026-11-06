"""Exact minimum Kakeya size k(R,n) by CP-SAT, with an independent re-check of
every returned witness by brute-force line enumeration (rings.is_kakeya).

Symmetry reduction (sound): GL_n(R) is transitive on primitive directions and
translations are transitive on points, so WLOG K contains the line R*e_1."""
import sys, time, json
from ortools.sat.python import cp_model
from .rings import (RINGS, all_points, directions, lines_in_direction, is_kakeya,
                    pack, line, scal, K_star)


def build(R, n, ub=None, forbid_sizes_above=None):
    m = cp_model.CpModel()
    P = {x: m.NewBoolVar(f"p{x}") for x in all_points(n)}
    for x in line(R, 0, pack(1, 0, n), n):
        m.Add(P[x] == 1)
    for b in directions(n):
        ls = []
        for L in lines_in_direction(R, b, n):
            y = m.NewBoolVar("")
            for x in L:
                m.AddImplication(y, P[x])
            ls.append(y)
        m.AddBoolOr(ls)
    obj = sum(P.values())
    if ub is not None:
        m.Add(obj <= ub)
    m.Minimize(obj)
    return m, P


def solve(R, n, time_limit=600.0, workers=2, ub=None, hint=True):
    m, P = build(R, n, ub=ub)
    if hint:
        S = K_star(n)
        for x, v in P.items():
            m.AddHint(v, 1 if x in S else 0)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = time_limit
    s.parameters.num_workers = workers
    t0 = time.time()
    st = s.Solve(m)
    res = {"ring": R, "n": n, "status": s.StatusName(st),
           "best": None, "lower_bound": s.BestObjectiveBound(),
           "seconds": round(time.time() - t0, 2), "conjecture": 3 * 2 ** n - 2}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        K = sorted(x for x, v in P.items() if s.Value(v))
        res["best"] = len(K)
        res["witness"] = K
        res["witness_rechecked"] = is_kakeya(R, K, n)
    return res


if __name__ == "__main__":
    n = int(sys.argv[1]); tl = float(sys.argv[2]) if len(sys.argv) > 2 else 600
    for R in RINGS:
        r = solve(R, n, tl)
        print(json.dumps({k: v for k, v in r.items() if k != "witness"}), flush=True)
        with open(f"results/exact_{R}_n{n}.json", "w") as f:
            json.dump(r, f)
