"""Symmetry-reduced exact decision procedure: is there a Kakeya set in R^n of
size <= m?  Reductions used (all sound, proved in the monograph, Sec. 3):

(S1) AGL_n(F_2) lifts to affine automorphisms of R^n, and these permute the
     residue fibres; AGL_n(F_2) is 3-transitive and the pointwise stabiliser of
     {0, e_1, ..., e_{k-1}} is transitive off span(e_1..e_{k-1}).  Hence WLOG
     s_0 >= s_a (all a), s_{e_1} >= s_a (a != 0) and, for k >= 2,
     s_{e_k} >= s_a for every a outside span(e_1, ..., e_{k-1}).
(S2) The kernel of reduction acts by x -> (I + pi M)x + pi c, shifting fibre a
     by c + M a.  Hence WLOG 0 in A_0 and 0 in A_{e_i} whenever A_{e_i} != {}.
"""
import sys, time, json
from ortools.sat.python import cp_model
from .rings import RINGS, directions, lines_in_direction, unpack, pack, is_kakeya


def span(vecs):
    S = {0}
    for v in vecs:
        S |= {s ^ v for s in S}
    return S


def decide(R, n, m, time_limit=3600, workers=2, extra_cuts=True):
    md = cp_model.CpModel()
    N = 1 << n
    X = {(a, u): md.NewBoolVar(f"x{a}_{u}") for a in range(N) for u in range(N)}
    pv = lambda x: X[unpack(x, n)]
    s = {a: sum(X[a, u] for u in range(N)) for a in range(N)}
    md.Add(sum(s.values()) <= m)
    # (S1)
    for a in range(N):
        md.Add(s[0] >= s[a])
        if a != 0 and n >= 1:
            md.Add(s[1] >= s[a])
    for k in range(2, n + 1):
        sp = span([1 << i for i in range(k - 1)])
        ek = 1 << (k - 1)
        for a in range(N):
            if a not in sp:
                md.Add(s[ek] >= s[a])
    # (S2)
    md.Add(X[0, 0] == 1)
    for i in range(n):
        for u in range(N):
            md.AddImplication(X[1 << i, u], X[1 << i, 0])
    # covering
    for b in directions(n):
        ys = []
        for L in lines_in_direction(R, b, n):
            y = md.NewBoolVar("")
            for x in L:
                md.AddImplication(y, pv(x))
            ys.append(y)
        md.AddBoolOr(ys)
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_limit
    sv.parameters.num_workers = workers
    t0 = time.time()
    st = sv.Solve(md)
    out = {"ring": R, "n": n, "m": m, "status": sv.StatusName(st),
           "seconds": round(time.time() - t0, 2)}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        K = sorted(pack(a, u, n) for (a, u), v in X.items() if sv.Value(v))
        out["witness"] = K
        out["size"] = len(K)
        out["witness_rechecked"] = is_kakeya(R, K, n)
    return out


if __name__ == "__main__":
    n, m = int(sys.argv[1]), int(sys.argv[2])
    tl = float(sys.argv[3]) if len(sys.argv) > 3 else 3600
    rings = sys.argv[4].split(",") if len(sys.argv) > 4 else RINGS
    for R in rings:
        r = decide(R, n, m, tl)
        print(json.dumps({k: v for k, v in r.items() if k != "witness"}), flush=True)
        json.dump(r, open(f"results/decide_{R}_n{n}_m{m}.json", "w"))
