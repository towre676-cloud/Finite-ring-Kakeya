"""Exact carry-transfer certificates over the two four-element local rings.

No numerical dependencies.  A certificate checks equality of each base edge's
contribution to a direction class, after fibre translations and a common
reindexing of the lifted directions.  Failure of this sufficient transfer test
does not rule out a more general transfer or a Kakeya set in the other ring.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import random
import time


def parity(x):
    return x.bit_count() & 1


def independent(vectors):
    pivots = {}
    for value in vectors:
        x = value
        while x:
            k = x.bit_length() - 1
            if k in pivots:
                x ^= pivots[k]
            else:
                pivots[k] = x
                break
    return list(pivots.values())


def contribution(A, B, v):
    """Full inverse image in V of P_v(A)+P_v(B) in V/<v>."""
    left = [u for u in A if (u ^ v) in A]
    right = [u for u in B if (u ^ v) in B]
    return {u ^ w for u in left for w in right}


def periods(S, N):
    if not S:
        return list(range(N))
    return [h for h in range(N) if {x ^ h for x in S} == S]


def solve_binary(rows, variable_count, track=False):
    pivots = {}
    for index, (mask, rhs) in enumerate(rows):
        witness = (1 << index) if track else 0
        while mask:
            p = mask.bit_length() - 1
            if p in pivots:
                m, r, w = pivots[p]
                mask ^= m
                rhs ^= r
                witness ^= w
            else:
                pivots[p] = (mask, rhs, witness)
                break
        if not mask and rhs:
            terms = [i for i in range(len(rows)) if (witness >> i) & 1] if track else []
            if track:
                cm = cr = 0
                for i in terms:
                    cm ^= rows[i][0]
                    cr ^= rows[i][1]
                assert cm == 0 and cr == 1
            return {"consistent": False, "rank_before_conflict": len(pivots),
                    "contradiction_rows": terms, "variables": variable_count,
                    "equations": len(rows)}
    solution = 0
    for p in sorted(pivots):
        mask, rhs, _ = pivots[p]
        if rhs ^ parity(mask & solution):
            solution |= 1 << p
    assert all(parity(mask & solution) == rhs for mask, rhs in rows)
    return {"consistent": True, "rank": len(pivots),
            "solution_hex": hex(solution), "variables": variable_count,
            "equations": len(rows)}


def transfer_system(fibres, n, universal=False):
    N = 1 << n
    rows, labels = [], []
    for v in range(1, N):
        for a in range(N):
            b = a ^ v
            if a > b:
                continue
            if universal:
                H = [0, v]
            else:
                H = periods(contribution(fibres[a], fibres[b], v), N)
            annihilator = independent(c for c in range(1, N)
                                      if all(parity(c & h) == 0 for h in H))
            for c in annihilator:
                mask = 0
                for j in range(n):
                    if (c >> j) & 1:
                        mask ^= 1 << (a*n + j)
                        mask ^= 1 << (b*n + j)
                        mask ^= 1 << ((N + v-1)*n + j)
                rows.append((mask, parity(c & a & v)))
                labels.append({"a": a, "b": b, "v": v, "character": c})
    return rows, labels, n*(2*N-1)


def transfer_certificate(fibres, n):
    rows, labels, variables = transfer_system(fibres, n)
    result = solve_binary(rows, variables, track=True)
    if not result["consistent"]:
        result["contradiction_equations"] = [labels[i] for i in result["contradiction_rows"]]
        return result
    N = 1 << n
    solution = int(result["solution_hex"], 16)
    f = [(solution >> (n*a)) & (N-1) for a in range(N)]
    t = {v: (solution >> (n*(N+v-1))) & (N-1) for v in range(1, N)}
    translated = [{u ^ f[a] for u in fibres[a]} for a in range(N)]
    # Independent set equality verifies every equation's intended semantics.
    for v in range(1, N):
        for a in range(N):
            b = a ^ v
            if a > b:
                continue
            source = contribution(fibres[a], fibres[b], v)
            target = {u ^ (a & v) for u in contribution(translated[a], translated[b], v)}
            assert target == {u ^ t[v] for u in source}
    result["fibre_translations"] = f
    result["direction_reindexing"] = t
    result["edgewise_set_equalities_checked"] = N*(N-1)//2
    return result


def direction_line_masks(n, mixed):
    N = 1 << n
    families = []
    for v in range(1, N):
        for w in range(N):
            if w > (w ^ v):
                continue
            seen, lines = set(), []
            for a in range(N):
                for u in range(N):
                    x = a + N*u
                    if x in seen:
                        continue
                    c = (a & v) if mixed else 0
                    L = [a + N*u, a + N*(u ^ v),
                         (a ^ v) + N*(u ^ w ^ c),
                         (a ^ v) + N*(u ^ w ^ c ^ v)]
                    seen.update(L)
                    lines.append(sum(1 << y for y in L))
            families.append(lines)
    return families


def is_kakeya_mask(mask, families):
    return all(any(mask & line == line for line in lines) for lines in families)


def fibres_from_mask(mask, n):
    N = 1 << n
    return [{u for u in range(N) if (mask >> (a+N*u)) & 1} for a in range(N)]


def mask_from_fibres(fibres, n):
    N = 1 << n
    return sum(1 << (a+N*u) for a, A in enumerate(fibres) for u in A)


def run_checks():
    start = time.perf_counter()
    report = {"theorems": ["G1 unlabelled incidence identity for every n",
                            "G2 no global fibre-translation gauge for n >= 2",
                            "G3 linear carry-transfer criterion for prescribed fibres"]}
    report["universal_gauge_checks"] = []
    for n in range(1, 7):
        rows, labels, variables = transfer_system(None, n, universal=True)
        result = solve_binary(rows, variables, track=(n <= 3))
        assert result["consistent"] == (n == 1)
        result["n"] = n
        if n <= 3 and not result["consistent"]:
            result["contradiction_equations"] = [labels[i] for i in result["contradiction_rows"]]
        report["universal_gauge_checks"].append(result)
    report["unlabelled_incidence_checks"] = []
    for n in range(1, 5):
        flat = direction_line_masks(n, False)
        mixed = direction_line_masks(n, True)
        lf = {line for family in flat for line in family}
        lm = {line for family in mixed for line in family}
        assert lf == lm
        report["unlabelled_incidence_checks"].append({"n": n, "directions": len(flat),
                                                     "unlabelled_lines": len(lf), "equal": True})
    flat = direction_line_masks(2, False)
    mixed = direction_line_masks(2, True)
    census = {"subsets": 1 << 16, "flat_kakeya": 0, "mixed_kakeya": 0,
              "flat_only": 0, "mixed_only": 0, "flat_transferable": 0,
              "flat_transfer_undecided": 0, "by_size": {}}
    example = None
    exceptional_missing_sums = set()
    for mask in range(1 << 16):
        kf, km = is_kakeya_mask(mask, flat), is_kakeya_mask(mask, mixed)
        census["flat_kakeya"] += kf
        census["mixed_kakeya"] += km
        census["flat_only"] += kf and not km
        census["mixed_only"] += km and not kf
        if km and not kf:
            A0 = fibres_from_mask(mask, 2)
            assert [len(x) for x in A0] == [3, 3, 3, 3]
            missing = [next(u for u in range(4) if u not in A) for A in A0]
            z = 0
            for u in missing:
                z ^= u
            exceptional_missing_sums.add(z)
            assert z == 3
        if not kf and not km:
            continue
        count = str(mask.bit_count())
        item = census["by_size"].setdefault(count, {"flat": 0, "mixed": 0, "flat_only": 0, "mixed_only": 0})
        item["flat"] += kf
        item["mixed"] += km
        item["flat_only"] += kf and not km
        item["mixed_only"] += km and not kf
        if not kf:
            continue
        A = fibres_from_mask(mask, 2)
        result = transfer_certificate(A, 2)
        if result["consistent"]:
            census["flat_transferable"] += 1
            f = result["fibre_translations"]
            translated = [{u ^ f[a] for u in A[a]} for a in range(4)]
            target = mask_from_fibres(translated, 2)
            assert target.bit_count() == mask.bit_count()
            assert is_kakeya_mask(target, mixed)
            if not km and example is None:
                example = {"source_mask_hex": hex(mask), "target_mask_hex": hex(target),
                           "size": mask.bit_count(), "source_fibres": [sorted(x) for x in A],
                           "target_fibres": [sorted(x) for x in translated], "certificate": result}
        else:
            census["flat_transfer_undecided"] += 1
    report["complete_n2_census"] = census
    report["n2_mixed_only_characterization"] = {
        "profile": [3, 3, 3, 3], "missing_point_xor": sorted(exceptional_missing_sums),
        "count": 64, "all_checked": True}
    # A fixed nontrivial example: flat Kakeya, not mixed in the same digits;
    # translate only fibre 7 by 2 to make a mixed Kakeya set of the same size.
    source_mask = int("505656d650c6d2d2", 16)
    source = fibres_from_mask(source_mask, 3)
    cert = transfer_certificate(source, 3)
    assert cert["consistent"]
    f = cert["fibre_translations"]
    target = [{u ^ f[a] for u in source[a]} for a in range(8)]
    target_mask = mask_from_fibres(target, 3)
    flat3, mixed3 = direction_line_masks(3, False), direction_line_masks(3, True)
    assert is_kakeya_mask(source_mask, flat3)
    assert not is_kakeya_mask(source_mask, mixed3)
    assert is_kakeya_mask(target_mask, mixed3)
    assert target_mask.bit_count() == source_mask.bit_count() == 29
    report["nontrivial_transfer_example"] = {
        "n": 3, "size": 29, "source_mask_hex": hex(source_mask),
        "target_mask_hex": hex(target_mask), "source_fibres": [sorted(A) for A in source],
        "target_fibres": [sorted(A) for A in target], "certificate": cert,
        "independent_direct_line_checks": True}
    rng = random.Random(20261101)
    random_checks = {"families": 0, "consistent": 0, "inconsistent": 0}
    for n in (2, 3, 4):
        N = 1 << n
        for _ in range(200):
            A = [{u for u in range(N) if rng.randrange(4) == 0} for a in range(N)]
            cert = transfer_certificate(A, n)
            random_checks["families"] += 1
            random_checks["consistent" if cert["consistent"] else "inconsistent"] += 1
    report["random_exact_edge_checks"] = random_checks
    report["elapsed_seconds"] = round(time.perf_counter()-start, 4)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(Path(__file__).with_name("carry_transfer_receipt.json")))
    args = parser.parse_args()
    report = run_checks()
    Path(args.output).write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
