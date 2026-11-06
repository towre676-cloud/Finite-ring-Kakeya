"""Exhaustive small controls for the three-minimum-images theorem.

This checks every normalized exact tiling A x B -> R^2 with |A|=|B|=4,
for both rings. It is a diagnostic, not a substitute for the analytic proof.
"""
from collections import Counter
from itertools import combinations
import json
from pathlib import Path


def operations(n, ring):
    mask = (1 << n) - 1
    if ring == "dual":
        add = lambda a, b: a ^ b
        neg = lambda a: a
    elif ring == "z4":
        def add(a, b):
            x, y = a & mask, b & mask
            return (x ^ y) | (((a >> n) ^ (b >> n) ^ (x & y)) << n)
        neg = lambda a: a ^ ((a & mask) << n)
    else:
        raise ValueError(ring)
    pi = lambda a: (a & mask) << n
    unit = lambda a: a ^ pi(a)
    sub = lambda a, b: add(a, neg(b))
    return add, sub, pi, unit


def check_tilings(ring):
    n, N = 2, 4
    add, sub, pi, unit = operations(n, ring)
    sets = [frozenset((0,) + rest) for rest in combinations(range(1, N*N), N-1)]
    difference_masks = []
    for A in sets:
        mask = 0
        for a in A:
            for b in A:
                mask |= 1 << sub(a, b)
        difference_masks.append(mask & ~1)
    counts = Counter()
    triple_count = 0
    strict_count = 0
    total = 0
    minimum_union = N*N
    minimum_strict_triple = N*N
    strict_example = None
    for i, A in enumerate(sets):
        for j, B in enumerate(sets):
            if difference_masks[i] & difference_masks[j]:
                continue
            total += 1
            pairs = {(sub(b, a)): (a, b) for a in A for b in B}
            assert len(pairs) == N*N
            C = {add(unit(a), pi(b)) for a in A for b in B}
            D = {add(unit(b), pi(a)) for a in A for b in B}
            # Direct f-image reconstruction checks the sumset formula.
            f = {v: pair[0] for v, pair in pairs.items()}
            direct = [set(f.values()), {add(f[v], v) for v in f},
                      {add(f[v], pi(v)) for v in f},
                      {add(f[v], unit(v)) for v in f}]
            assert direct == [set(A), set(B), C, D]
            U = A | B | C | D
            sizes = (len(A), len(B), len(C), len(D))
            counts[tuple(sizes)] += 1
            minimum_union = min(minimum_union, len(U))
            if sum(s == N for s in sizes) >= 3:
                triple_count += 1
                assert len(U) >= 3*N-2
                if max(sizes) > N:
                    strict_count += 1
                    minimum_strict_triple = min(minimum_strict_triple, len(U))
                    assert len(U) >= 7*N//2-3
                    if strict_example is None:
                        strict_example = {"A": sorted(A), "B": sorted(B),
                                          "images": [sorted(s) for s in direct],
                                          "sizes": sizes, "union_size": len(U),
                                          "f": [f[v] for v in range(N*N)]}
    return {"ring": ring, "normalized_balanced_pair_tilings": total,
            "minimum_union_all_tilings": minimum_union,
            "three_minimum_images_count": triple_count,
            "strict_three_minimum_count": strict_count,
            "minimum_union_strict_three": minimum_strict_triple,
            "size_histogram": [{"sizes": list(k), "count": v} for k,v in sorted(counts.items())],
            "strict_example": strict_example}


def check_stated_example(ring):
    add, sub, pi, unit = operations(2, ring)
    # e1=1, e2=2; point encoding x + 4*y.
    A = {0, 8, 1, 13}
    B = {0, 4, 2, 6}
    pairs = {sub(b, a): a for a in A for b in B}
    assert len(pairs) == 16
    images = [A, B,
              {add(pairs[v], pi(v)) for v in pairs},
              {add(pairs[v], unit(v)) for v in pairs}]
    assert [len(x) for x in images] == [4,4,6,4]
    assert len(set.union(*images)) == 11
    return {"ring": ring, "images": [sorted(x) for x in images],
            "sizes": [len(x) for x in images], "union_size": 11}


if __name__ == "__main__":
    report = {"scope": "Exhaustive R^2 normalized |S0|=|S1|=4 tilings; not an all-dimension proof",
              "tiling_checks": [check_tilings(ring) for ring in ["dual", "z4"]],
              "stated_examples": [check_stated_example(ring) for ring in ["dual", "z4"]]}
    dest = Path(__file__).with_name("THREE_IMAGES_SMALL_CHECKS.json")
    dest.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"report": str(dest), "summary": [
        {k:v for k,v in r.items() if k not in ["size_histogram", "strict_example"]}
        for r in report["tiling_checks"]]}, indent=2))
