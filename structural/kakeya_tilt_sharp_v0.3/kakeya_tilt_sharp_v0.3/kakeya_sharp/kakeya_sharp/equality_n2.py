"""Exhaustive census of all Kakeya sets of size <= 10 in R^2 (C(16,10) subsets)."""
from itertools import combinations
import json
from .rings import RINGS, all_points, is_kakeya, fibres
out = {}
for R in RINGS:
    pts = list(all_points(2))
    small = [K for k in range(4, 10) for K in combinations(pts, k) if is_kakeya(R, K, 2)]
    eq = [K for K in combinations(pts, 10) if is_kakeya(R, K, 2)]
    profs = sorted({tuple(sorted((len(v) for v in fibres(K, 2).values()), reverse=True)) for K in eq})
    out[R] = {"kakeya_sets_below_10": len(small), "equality_sets": len(eq), "equality_profiles": profs,
              "predicted_2^n*2^((n-1)(2^n-1))": 4 * 2 ** 3}
print(json.dumps(out))
json.dump(out, open("results/equality_census_n2.json", "w"))
