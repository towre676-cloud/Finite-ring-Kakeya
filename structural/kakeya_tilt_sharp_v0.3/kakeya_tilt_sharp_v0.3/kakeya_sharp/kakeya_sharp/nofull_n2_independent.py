"""Independent re-derivation (fresh coordinate-tuple arithmetic, no shared code)
of the n = 2 no-full-fibre census in Z/4Z and F_2[e]/(e^2)."""
import json
from itertools import product

def ring_ops(R):
    if R == "Z4":
        els = [0, 1, 2, 3]
        add = lambda x, y: (x + y) % 4
        mul = lambda x, y: (x * y) % 4
        res = lambda x: x % 2
        units = [1, 3]
    else:  # dual numbers a + b e encoded as (a, b)
        els = [(a, b) for a in (0, 1) for b in (0, 1)]
        add = lambda x, y: ((x[0] + y[0]) % 2, (x[1] + y[1]) % 2)
        mul = lambda x, y: ((x[0] * y[0]) % 2, (x[0] * y[1] + x[1] * y[0]) % 2)
        res = lambda x: x[0]
        units = [(1, 0), (1, 1)]
    return els, add, mul, res, units

out = {}
for R in ("Z4", "D2"):
    els, add, mul, res, units = ring_ops(R)
    pts = list(product(els, repeat=2))
    idx = {p: i for i, p in enumerate(pts)}
    dirs, seen = [], set()
    for b in pts:
        if all(res(c) == 0 for c in b) or b in seen: continue
        cls = {tuple(mul(u, c) for c in b) for u in units}
        seen |= cls; dirs.append(b)
    lines = []
    for b in dirs:
        Ls = set()
        for x in pts:
            Ls.add(frozenset(idx[tuple(add(x[i], mul(t, b[i])) for i in range(2))] for t in els))
        lines.append([sum(1 << j for j in L) for L in Ls])
    fib = {}
    for p in pts:
        fib.setdefault(tuple(res(c) for c in p), 0)
        fib[tuple(res(c) for c in p)] |= 1 << idx[p]
    fibmasks = list(fib.values())
    best, cnt = None, 0
    for mask in range(1 << 16):
        if any(mask & f == f for f in fibmasks): continue
        if all(any(mask & L == L for L in Ls) for Ls in lines):
            k = bin(mask).count("1")
            if best is None or k < best: best, cnt = k, 1
            elif k == best: cnt += 1
    out[R] = {"directions": len(dirs), "min_nofull": best, "count_at_min": cnt}
print(json.dumps(out)); json.dump(out, open("results/nofull_n2_independent.json", "w"))
