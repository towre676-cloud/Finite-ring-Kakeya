#!/usr/bin/env python3
"""Independently check the final one-missing leaves using actual binary subsets."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations
import json
from pathlib import Path

from audit_frontier import points, require


@cache
def normalized_spectra(weight):
    checked = 0
    spectra = set()
    for rank in range(1, 6):
        space = set(range(1 << rank))
        basis = {0, *(1 << j for j in range(rank))}
        extra_count = weight - len(basis)
        if not 0 <= extra_count <= len(space - basis):
            continue
        for extra in combinations(sorted(space - basis), extra_count):
            checked += 1
            fibre = basis | set(extra)
            pairs = [sum((a ^ d) in fibre for a in fibre) // 2 for d in range(1, 32)]
            spectra.add(tuple(sorted(pairs, reverse=True)))
    return checked, spectra


def upper(p, q):
    """Compute the plane-coset bound by integer allocation."""
    if p > q:
        p, q = q, p
    if p != 3:
        return min(16, p * q)
    scores = [0, 3] + [4] * 6
    return max(sum(scores[n] for n in (a, b, c, q - a - b - c))
               for a in range(q + 1) for b in range(q - a + 1)
               for c in range(q - a - b + 1))


def verify(path):
    leaves = json.loads(path.read_text())["one_missing_support13"]["spectrum_leaf_witnesses"]
    accepted = Counter()
    for row in leaves:
        weights = {int(k): v for k, v in row["weights"].items()}
        support = set(points(row["mask"] | 1))
        light = dict(zip(row["light"], row["light_options"]))
        heavy = support - light.keys()
        require(weights.keys() == support and len(support) == 13 and len(heavy) == 10
                and all(4 <= weights[a] <= row["maximum"] for a in heavy)
                and sum(weights.values()) <= 93 and weights[0] == row["maximum"],
                "Invalid leaf weight scope")
        missing = set(range(1, 32)) - {a ^ b for a, b in combinations(heavy, 2)}
        require(missing == {row["missing"]}, "Invalid missing direction")
        for a, (w, active) in light.items():
            require(w == weights[a] and row["missing"] in active
                    and all((a ^ d) in support for d in active), "Invalid light options")
            if w == 2:
                require(len(active) == 1, "Weight two has one pair direction")
            else:
                require(w == 3 and any(set(active) == ({row["missing"], e, e ^ row["missing"]}
                                                        & {a ^ b for b in support - {a}})
                                       for e in range(1, 32) if e != row["missing"]),
                        "Invalid projected light triangle")
        failures = [r for r in row["spectrum_deficits"] if r["weight"] in (8, 9)]
        require(failures, "Leaf lacks an independently reproducible spectrum contradiction")
        witness = failures[0]
        vertex = witness["vertex"]
        weight = weights[vertex]
        require(vertex in heavy and weight == witness["weight"], "Wrong leaf vertex")
        requirements = []
        for d in range(1, 32):
            def active(a):
                return a not in light or d in light[a][1]

            partner = vertex ^ d
            if partner not in support or not active(partner):
                continue
            other_capacity = sum(
                upper(weights[a] // 2, weights[a ^ d] // 2)
                for a in support
                if a < (a ^ d) and (a ^ d) in support and vertex not in (a, a ^ d)
                and active(a) and active(a ^ d)
            )
            if other_capacity < 16:
                requirements.append(next(p for p in range(1, weight // 2 + 1)
                                         if other_capacity + upper(p, weights[partner] // 2) >= 16))
        require([sum(q >= p for q in requirements) for p in range(1, 8)]
                == witness["tails_ge_1_to_7"], "Invalid pair demand witness")
        ordered = sorted(requirements, reverse=True)
        _, possible = normalized_spectra(weight)
        require(all(any(q > p for q, p in zip(ordered, spectrum)) for spectrum in possible),
                "A normalized actual fibre can meet the displayed requirements")
        accepted[row["maximum"]] += 1
    require(accepted == {14: 88, 15: 4}, "Missing one-missing leaves")
    return {"status": "PASS", "spectrum_leaves_checked": dict(accepted),
            "normalized_actual_fibres_checked": {
                w: normalized_spectra(w)[0] for w in (8, 9)},
            "distinct_pair_histograms": {w: len(normalized_spectra(w)[1]) for w in (8, 9)}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exclusions", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.exclusions), indent=2))


if __name__ == "__main__":
    main()
