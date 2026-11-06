"""Standard-library exhaustive proof (no solver) for the n = 3 statements:

  (a) ub = 21, any profile          -> no point      (k(R,3) >= 22)
  (b) ub = 23, every fibre size <= 7 -> no point     (no-full-fibre case >= 24)

The search ranges over exact local types (pair vectors of actual subsets of
F_2^3; 46 types including the empty set) for the 8 residue fibres, subject to
the affine size ordering (S1) and the shared-period capacity of v0.2
Theorem 14, and requires for every v != 0
    sum over edges {a, a+v} of min(4, p_a(v) p_b(v) / |J|) >= 4.
Pruning is by an optimistic capacity bound for unassigned fibres, so a
NO-POINT verdict is a complete proof for the relaxation, hence for both rings.
"""
import sys, json, time
from itertools import combinations

n, N, H = 3, 8, 4


def types():
    seen = {}
    for mask in range(1 << N):
        A = [u for u in range(N) if mask >> u & 1]
        S = set(A)
        p = tuple(sum(1 for u in A if (u ^ v) in S) // 2 for v in range(1, N))
        seen.setdefault((len(A), p), mask)
    return sorted(seen, key=lambda t: -t[0])


def stab(t):
    s, p = t
    return {0} | ({v for v in range(1, N) if 2 * p[v - 1] == s} if s else set())


def jsize(sa, sb, v):
    qa = {min(h, h ^ v) for h in sa}
    qb = {min(h, h ^ v) for h in sb}
    return len(qa & qb)


def run(ub, smax):
    T = [t for t in types() if t[0] <= smax and t[0] != 1]   # singletons have p = 0: dominated by empty
    ST = [stab(t) for t in T]
    order = [0, 1, 2, 4, 3, 5, 6, 7]
    span1 = {0, 1}; span2 = {0, 1, 2, 3}
    def cap_rule(a, s):  # size cap for residue a given assigned sizes (S1)
        c = s.get(0, smax)
        if a != 0: c = min(c, s.get(1, smax))
        if a not in span1: c = min(c, s.get(2, smax))
        if a not in span2: c = min(c, s.get(4, smax))
        return c
    nodes = 0
    assign = {}
    def feasible_bound(used):
        rem = ub - used
        for v in range(1, N):
            tot = 0
            for a in range(N):
                b = a ^ v
                if a > b: continue
                if a in assign and b in assign:
                    ta, tb = T[assign[a]], T[assign[b]]
                    pa, pb = ta[1][v - 1], tb[1][v - 1]
                    if pa and pb:
                        tot += min(H, pa * pb // jsize(ST[assign[a]], ST[assign[b]], v))
                else:
                    def pm(x):
                        if x in assign: return T[assign[x]][1][v - 1]
                        return min(H, min(rem, cap_rule(x, {k: T[i][0] for k, i in assign.items()})) // 2)
                    tot += min(H, pm(a) * pm(b))
                if tot >= H: break
            if tot < H:
                return False
        return True
    def dfs(i, used):
        nonlocal nodes
        nodes += 1
        if not feasible_bound(used):
            return None
        if i == N:
            return dict(assign)
        a = order[i]
        c = cap_rule(a, {k: T[j][0] for k, j in assign.items()})
        for j, t in enumerate(T):
            if t[0] > c or used + t[0] > ub:
                continue
            assign[a] = j
            r = dfs(i + 1, used + t[0])
            del assign[a]
            if r: return r
        return None
    t0 = time.time()
    w = dfs(0, 0)
    return {"n": 3, "ub": ub, "smax": smax, "local_types_used": len(T), "nodes": nodes,
            "status": "POINT_FOUND" if w else "NO_POINT", "seconds": round(time.time() - t0, 2),
            "witness_sizes": [T[w[a]][0] for a in range(N)] if w else None}


if __name__ == "__main__":
    ub, smax = int(sys.argv[1]), int(sys.argv[2])
    r = run(ub, smax)
    print(json.dumps(r))
    if len(sys.argv) > 3:
        json.dump(r, open(sys.argv[3], "w"))
