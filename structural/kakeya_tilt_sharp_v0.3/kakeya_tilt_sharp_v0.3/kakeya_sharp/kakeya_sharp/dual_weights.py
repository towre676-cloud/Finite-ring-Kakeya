"""Dual-weight certificate for the no-full-fibre case.

Lemma (supply).  Let H = N/2 and let f: {0..H-1} -> R_{>=0}, f(0) = 0, satisfy
    min(H, x*y) <= f(x) + f(y)     for all 0 <= x, y <= H-1.          (W)
If K is Kakeya in R^n (either ring) with no full residue fibre, then
    sum_a Phi_f(A_a) >= H (N-1),   Phi_f(A) = sum_{v != 0} f(p_A(v)).
Proof: for each v the covering identity gives
    H <= sum_{edges {a,a+v}} min(H, p_a(v) p_{a+v}(v)) <= sum_a f(p_a(v)),
since no fibre is full, every p_a(v) <= H-1; sum over v.  []

Hence if  max { sum_a Phi_f(T_a) : T_a realizable local types, |T_a| <= N-1,
sum |T_a| <= ub }  <  H (N-1),  no Kakeya set of size <= ub without a full
fibre exists.  The maximum is a knapsack over N fibres computed exactly by
dynamic programming over Phi_max(s) = max_{|T| = s} Phi_f(T).

f is found by a cutting-plane LP: minimise z subject to (W) and
sum_a Phi_f(T_a) <= z for every type multiset produced so far by the DP.
The final certificate is re-verified in exact rational arithmetic.
"""
import sys, json
from fractions import Fraction
from ortools.linear_solver import pywraplp
from .exact_local4 import local_types


def knapsack(Phimax, N, ub, smax):
    # best[k][b] = max total Phi using k fibres with total size b
    NEG = None
    best = [[NEG] * (ub + 1) for _ in range(N + 1)]
    arg = [[None] * (ub + 1) for _ in range(N + 1)]
    best[0][0] = 0
    for k in range(N):
        for b in range(ub + 1):
            if best[k][b] is None:
                continue
            for s in range(0, smax + 1):
                if b + s > ub:
                    break
                val = best[k][b] + Phimax[s][0]
                if best[k + 1][b + s] is None or val > best[k + 1][b + s]:
                    best[k + 1][b + s] = val
                    arg[k + 1][b + s] = (b, s)
    bb = max(range(ub + 1), key=lambda b: best[N][b] if best[N][b] is not None else -1)
    sizes, b = [], bb
    for k in range(N, 0, -1):
        pb, s = arg[k][b]
        sizes.append(s); b = pb
    return best[N][bb], sizes


def certify(n, ub, rounds=200, verbose=True):
    N = 1 << n; H = N >> 1; smax = N - 1
    T = [(k[0], k[1:]) for k in local_types(n) if k[0] <= smax]
    bysize = {}
    for s, p in T:
        bysize.setdefault(s, []).append(p)
    lp = pywraplp.Solver.CreateSolver("GLOP")
    f = [lp.NumVar(0, lp.infinity(), f"f{x}") for x in range(H)]
    lp.Add(f[0] == 0)
    for x in range(H):
        for y in range(x, H):
            lp.Add(f[x] + f[y] >= min(H, x * y))
    z = lp.NumVar(0, lp.infinity(), "z")
    lp.Minimize(z)
    cuts = []
    target = H * (N - 1)
    hist = []
    for it in range(rounds):
        lp.Solve()
        fv = [f[x].solution_value() for x in range(H)]
        Phimax = {}
        for s in range(smax + 1):
            best = max(((sum(fv[q] for q in p), p) for p in bysize.get(s, [])), default=(None, None))
            Phimax[s] = best
        avail = {s: v for s, v in Phimax.items() if v[0] is not None}
        PM = [avail.get(s, (-1e9, None)) for s in range(smax + 1)]
        val, sizes = knapsack(PM, N, ub, smax)
        hist.append((round(z.solution_value(), 4), round(val, 4)))
        if verbose:
            print(f"round {it}: lp z = {z.solution_value():.4f}  knapsack max = {val:.4f}  sizes = {sorted(sizes, reverse=True)}", flush=True)
        if val <= z.solution_value() + 1e-7:
            break
        # add cut for this multiset of types: count of each pair value
        cnt = [0] * H
        for s in sizes:
            for q in PM[s][1]:
                cnt[q] += 1
        lp.Add(sum(cnt[q] * f[q] for q in range(H)) <= z)
    return fv, val, target, hist, bysize


def exact_check(fv, n, ub, bysize, denom=1000):
    """Round f up to rationals, re-verify (W) and the knapsack bound exactly."""
    N = 1 << n; H = N >> 1; smax = N - 1
    fq = [Fraction(0)] + [Fraction(int(-(-x * denom // 1)) if False else round(x * denom + 0.5), denom) for x in fv[1:]]
    okW = all(fq[x] + fq[y] >= min(H, x * y) for x in range(H) for y in range(H))
    Phimax = []
    for s in range(smax + 1):
        if s in bysize:
            Phimax.append((max(sum(fq[q] for q in p) for p in bysize[s]), None))
        else:
            Phimax.append((Fraction(-10 ** 9), None))
    val, sizes = knapsack(Phimax, N, ub, smax)
    return {"f": [str(x) for x in fq], "W_holds": okW, "knapsack_max": str(val),
            "knapsack_max_float": float(val), "target": H * (N - 1),
            "certified": okW and val < H * (N - 1), "extremal_sizes": sorted(sizes, reverse=True)}


if __name__ == "__main__":
    n, ub = int(sys.argv[1]), int(sys.argv[2])
    fv, val, target, hist, bysize = certify(n, ub)
    ex = exact_check(fv, n, ub, bysize)
    ex.update({"n": n, "ub": ub, "lp_rounds": len(hist)})
    print(json.dumps(ex))
    json.dump(ex, open(f"results/dual_weights_n{n}_ub{ub}.json", "w"))
