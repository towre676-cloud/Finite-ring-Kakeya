"""Exhaustive: minimum size of a Kakeya set in R^2 with no full residue fibre."""
import json
from .rings import RINGS, is_kakeya, fibres
out = {}
for R in RINGS:
    best, cnt = None, 0
    for mask in range(1 << 16):
        K = [x for x in range(16) if mask >> x & 1]
        if best is not None and len(K) > best:
            continue
        if any(len(A) == 4 for A in fibres(K, 2).values()):
            continue
        if is_kakeya(R, K, 2):
            if best is None or len(K) < best:
                best, cnt = len(K), 1
            elif len(K) == best:
                cnt += 1
    out[R] = {"min_nofull": best, "count_at_min": cnt}
print(json.dumps(out)); json.dump(out, open("results/nofull_n2.json", "w"))
