"""Exhaustive sanity check of Theorem A's inequality chain at n = 2, 3 over
the exact local-type model with a full fibre at 0:  for every assignment of
local types to residues 1..N-1 that satisfies the counting cover condition,
with U = {v : p_v(v) = 0},  W = sum_{b not in U}(s_b - 2) + sum_{b in U} s_b
satisfies W^2 >= N |U|, and W >= 2|U| whenever |U| <= N/4.  (n = 3 is run on a
random sample of 200,000 assignments since 46^7 is too large to exhaust.)"""
import random, json, itertools
from .exact_local4 import local_types


def check(n, samples=None, seed=1):
    N = 1 << n; H = N >> 1
    T = [(k[0], k[1:]) for k in local_types(n)]
    full = [t for t in T if t[0] == N][0]
    it = itertools.product(range(len(T)), repeat=N - 1) if samples is None else \
        (tuple(random.Random(seed + i).randrange(len(T)) for _ in range(N - 1)) for i in range(samples))
    tested = feasible = viol_sq = viol_A = 0
    for combo in it:
        fib = [full] + [T[i] for i in combo]
        ok = True
        for v in range(1, N):
            tot = sum(min(H, fib[a][1][v - 1] * fib[a ^ v][1][v - 1]) for a in range(N) if a < (a ^ v))
            if tot < H:
                ok = False; break
        tested += 1
        if not ok:
            continue
        feasible += 1
        U = [v for v in range(1, N) if fib[v][1][v - 1] == 0]
        W = sum(fib[b][0] - 2 for b in range(1, N) if b not in U) + sum(fib[b][0] for b in U)
        if W * W < N * len(U): viol_sq += 1
        if 4 * len(U) <= N and W < 2 * len(U): viol_A += 1
    return {"n": n, "tested": tested, "cover_feasible": feasible, "violations_W2": viol_sq, "violations_thmA": viol_A}


if __name__ == "__main__":
    out = [check(2), check(3, samples=200000)]
    print(json.dumps(out))
    json.dump(out, open("results/theorem_A_check.json", "w"))
