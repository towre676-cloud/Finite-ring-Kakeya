"""Support-aware dual-weight certificate (sharpening of dual_weights.py).

Lemma.  Let f satisfy (W) of dual_weights.py and let S be the set of residues
whose fibre has at least 2 points, sigma = |S|.  If K is Kakeya with no full
fibre then
    H (N-1) <= sum_{a in S} top_{sigma-1}( f(p_a(v)) : v != 0 ),
where top_k sums the k largest values.  Proof: in direction v only edges with
both ends in S contribute, and min(H, xy) <= f(x)[y>=1] + f(y)[x>=1]; fibre a
meets the edges {a, a+v} with a+v in S for exactly sigma-1 values of v.  []

For each sigma the right side is maximised by a knapsack over sigma fibres of
size >= 2 with total size <= ub.  f is optimised by cutting planes; the final
certificate is checked in exact rational arithmetic for every sigma."""
import sys, json
from fractions import Fraction
from ortools.linear_solver import pywraplp
from .exact_local4 import local_types


def topk(vals, k):
    return sum(sorted(vals, reverse=True)[:k]) if k > 0 else 0


def knap(PM, sigma, ub, smax):
    # exactly sigma fibres, sizes in [2, smax], total <= ub; maximise sum PM[s]
    best = [[None] * (ub + 1) for _ in range(sigma + 1)]
    arg = [[None] * (ub + 1) for _ in range(sigma + 1)]
    best[0][0] = 0
    for k in range(sigma):
        for b in range(ub + 1):
            if best[k][b] is None:
                continue
            for s in range(2, smax + 1):
                if b + s > ub:
                    break
                if PM[s] is None:
                    continue
                val = best[k][b] + PM[s]
                if best[k + 1][b + s] is None or val > best[k + 1][b + s]:
                    best[k + 1][b + s] = val
                    arg[k + 1][b + s] = (b, s)
    cand = [b for b in range(ub + 1) if best[sigma][b] is not None]
    if not cand:
        return None, None
    bb = max(cand, key=lambda b: best[sigma][b])
    sizes, b = [], bb
    for k in range(sigma, 0, -1):
        pb, s = arg[k][b]
        sizes.append(s); b = pb
    return best[sigma][bb], sizes


def evaluate(fv, bysize, N, ub, smax):
    worst = (None, None, None, None)
    for sigma in range(2, N + 1):
        PM, PT = [None] * (smax + 1), [None] * (smax + 1)
        for s in range(2, smax + 1):
            if s in bysize:
                v, p = max(((topk([fv[q] for q in p], sigma - 1), p) for p in bysize[s]))
                PM[s], PT[s] = v, p
        val, sizes = knap(PM, sigma, ub, smax)
        if val is not None and (worst[0] is None or val > worst[0]):
            worst = (val, sigma, sizes, [PT[s] for s in sizes])
    return worst


def certify(n, ub, rounds=300, verbose=True):
    N = 1 << n; H = N >> 1; smax = N - 1
    bysize = {}
    for k in local_types(n):
        if k[0] <= smax:
            bysize.setdefault(k[0], []).append(k[1:])
    lp = pywraplp.Solver.CreateSolver("GLOP")
    f = [lp.NumVar(0, lp.infinity(), f"f{x}") for x in range(H)]
    lp.Add(f[0] == 0)
    for x in range(H):
        for y in range(x, H):
            lp.Add(f[x] + f[y] >= min(H, x * y))
    z = lp.NumVar(0, lp.infinity(), "z")
    lp.Minimize(z)
    for it in range(rounds):
        lp.Solve()
        fv = [f[x].solution_value() for x in range(H)]
        val, sigma, sizes, ptypes = evaluate(fv, bysize, N, ub, smax)
        if verbose:
            print(f"round {it}: z = {z.solution_value():.4f}  worst = {val:.4f}  sigma = {sigma}  sizes = {sorted(sizes, reverse=True)}", flush=True)
        if val <= z.solution_value() + 1e-7:
            break
        cnt = [0] * H
        for p in ptypes:
            for q in sorted(p, key=lambda q: -fv[q])[:sigma - 1]:
                cnt[q] += 1
        lp.Add(sum(cnt[q] * f[q] for q in range(H)) <= z)
    return fv, bysize


def exact(fv, n, ub, bysize, denom=10 ** 6):
    N = 1 << n; H = N >> 1; smax = N - 1
    fq = [Fraction(0)] + [Fraction(-(-int(x * denom * 10) // 10) + 1, denom) for x in fv[1:]]
    okW = all(fq[x] + fq[y] >= min(H, x * y) for x in range(H) for y in range(H))
    val, sigma, sizes, _ = evaluate(fq, bysize, N, ub, smax)
    return {"n": n, "ub": ub, "f": [str(x) for x in fq], "W_holds": okW,
            "max_supply": str(val), "max_supply_float": float(val), "worst_sigma": sigma,
            "worst_sizes": sorted(sizes, reverse=True), "target": H * (N - 1),
            "certified": bool(okW and val < H * (N - 1))}


if __name__ == "__main__":
    n, ub = int(sys.argv[1]), int(sys.argv[2])
    fv, bysize = certify(n, ub)
    r = exact(fv, n, ub, bysize)
    print(json.dumps(r))
    json.dump(r, open(f"results/dual_support_n{n}_ub{ub}.json", "w"))
