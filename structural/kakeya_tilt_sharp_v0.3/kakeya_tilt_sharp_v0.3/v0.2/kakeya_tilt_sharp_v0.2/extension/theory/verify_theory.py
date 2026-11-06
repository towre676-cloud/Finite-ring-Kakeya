"""Exact covariogram arithmetic and heavy-fibre theorems for binary Kakeya.

Standard library only.  Run this file to regenerate theory_receipt.json and
local_types_n4.json.  The finite classification compares two independent
enumerations: all subsets, and all possible integer-square Walsh spectra.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations, product
from math import ceil, isqrt
from pathlib import Path
import hashlib
import json
import time


def walsh(values):
    out = list(values)
    step = 1
    while step < len(out):
        for start in range(0, len(out), 2 * step):
            for j in range(start, start + step):
                x, y = out[j], out[j + step]
                out[j], out[j + step] = x + y, x - y
        step *= 2
    return tuple(out)


def pair_vector(mask, N):
    members = [a for a in range(N) if mask >> a & 1]
    p = [0] * (N - 1)
    for x, y in combinations(members, 2):
        p[(x ^ y) - 1] += 1
    return len(members), tuple(p)


def actual_types(N):
    answer = {s: set() for s in range(N + 1)}
    witnesses = {}
    for mask in range(1 << N):
        s, p = pair_vector(mask, N)
        answer[s].add(p)
        witnesses.setdefault((s, p), mask)
    return answer, witnesses


def spectrum(s, p):
    return walsh((s,) + tuple(2 * x for x in p))


def is_T_local(s, p):
    N = len(p) + 1
    if any(not isinstance(x, int) or x < 0 or 2 * x > s for x in p):
        return False
    if sum(p) != s * (s - 1) // 2:
        return False
    d = (0,) + tuple(s - 2 * x for x in p)
    if max(d) > min(s, N - s):
        return False
    return all(d[v ^ w] <= d[v] + d[w]
               for v in range(N) for w in range(N))


def complete_signs(s, p, max_nonzero=20):
    """Exact sign-completion certificate, or None if exhausted without one.

    Raises rather than silently truncating a search beyond max_nonzero.
    The inverse Walsh transform need only be integral; Parseval then makes
    it a zero-one vector automatically.
    """
    W = spectrum(s, p)
    if any(z < 0 or isqrt(z) ** 2 != z for z in W) or W[0] != s * s:
        return None
    support = [j for j in range(1, len(W)) if W[j]]
    if len(support) > max_nonzero:
        raise ValueError("sign search exceeds declared nonzero-frequency cap")
    for signs in product((-1, 1), repeat=len(support)):
        b = [0] * len(W)
        b[0] = s
        for j, sign in zip(support, signs):
            b[j] = sign * isqrt(W[j])
        inverse = walsh(b)
        if all(z % len(W) == 0 for z in inverse):
            f = tuple(z // len(W) for z in inverse)
            assert set(f) <= {0, 1}
            mask = sum(bit << x for x, bit in enumerate(f))
            assert pair_vector(mask, len(W)) == (s, tuple(p))
            return {"signed_roots": b, "mask": mask}
    return None


def count_histograms(values, length, total):
    def visit(i, slots, remaining, prefix):
        if i == len(values) - 1:
            if slots * values[i] == remaining:
                yield prefix + (slots,)
            return
        for count in range(slots + 1):
            rest = remaining - count * values[i]
            if rest >= 0:
                yield from visit(i + 1, slots - count, rest, prefix + (count,))
    yield from visit(0, length, total, ())


def arrangements(values, histogram, slots, array, index=0):
    if index == len(values) - 1:
        for j in slots:
            array[j] = values[index]
        yield tuple(array)
        return
    for chosen in combinations(slots, histogram[index]):
        chosen_set = set(chosen)
        for j in chosen:
            array[j] = values[index]
        remaining = tuple(j for j in slots if j not in chosen_set)
        yield from arrangements(values, histogram, remaining, array, index + 1)


def square_candidates(N, s):
    """Every permitted spectrum is enumerated, without calling a solver."""
    root_bound = min(s, N - s)
    squares = tuple(r * r for r in range(s % 2, root_bound + 1, 2))
    for histogram in count_histograms(squares, N - 1, s * (N - s)):
        for W in arrangements(squares, histogram, tuple(range(1, N)),
                              [s * s] + [0] * (N - 1)):
            raw = walsh(W)
            if any(x % N for x in raw):
                continue
            c = tuple(x // N for x in raw)
            if c[0] != s or any(x < max(0, 2 * s - N) or x > s or x % 2
                               for x in c[1:]):
                continue
            yield tuple(x // 2 for x in c[1:]), W


def xor_all(values):
    out = 0
    for x in values:
        out ^= x
    return out


def four_frequency_obstruction(N, s, W):
    support = [xi for xi in range(1, N) if W[xi]]
    return (s == N // 2 and len(support) == 4
            and all(W[xi] == (N // 4) ** 2 for xi in support)
            and xor_all(support) != 0)


def all_subspaces(N):
    known = {frozenset({0})}
    frontier = list(known)
    while frontier:
        U = frontier.pop()
        for v in range(1, N):
            if v in U:
                continue
            larger = U | frozenset(x ^ v for x in U)
            if larger not in known:
                known.add(larger)
                frontier.append(larger)
    return sorted(known, key=lambda U: (len(U), tuple(sorted(U))))


def verify_subspace_bounds(types, N):
    checks = 0
    subspaces = all_subspaces(N)
    for s, vectors in types.items():
        for p in vectors:
            for U in subspaces:
                h = len(U)
                q, r = divmod(s, h)
                upper = q * h * (h - 1) // 2 + r * (r - 1) // 2
                cosets = N // h
                a, b = divmod(s, cosets)
                lower = (cosets - b) * a * (a - 1) // 2 + b * a * (a + 1) // 2
                actual = sum(p[v - 1] for v in U if v)
                assert lower <= actual <= upper
                checks += 1
    return {"subspaces": len(subspaces), "type_subspace_checks": checks}


def verify_heavy_allocation_n2(types):
    N = 4
    H = N // 2
    all_types = [(s, p) for s, pp in types.items() for p in pp]
    feasible = 0
    minima = {}
    for assignment in product(all_types, repeat=N):
        if any(sum(assignment[a][1][v - 1] * assignment[a ^ v][1][v - 1]
                   for a in range(N) if a < (a ^ v)) < H
               for v in range(1, N)):
            continue
        feasible += 1
        B = [a for a in range(N) if assignment[a][0] > 2]
        L = sum(s == 2 for s, _ in assignment)
        h = len(B)
        D = {a ^ b for a, b in combinations(B, 2)}
        external = [v for v in range(1, N) if v not in D]
        demands = 0
        for v in external:
            capacities = sorted((assignment[a][1][v - 1] for a in B), reverse=True)
            prefix = 0
            demand = 2 * H
            for j in range(h + 1):
                if j:
                    prefix += capacities[j - 1]
                demand = min(demand, j + 2 * max(0, H - prefix))
            demands += demand
        assert demands <= L
        total = sum(s for s, _ in assignment)
        minima[h] = min(minima.get(h, total), total)
        if h <= 2:
            assert any(s == N for s, _ in assignment)
            assert total >= 3 * N - 2
            if h == 2:
                assert total >= 3 * N - 1
        if all(s < N for s, _ in assignment):
            assert (h - 1) ** 2 >= N - 1
    return {"assignments_checked": len(all_types) ** N, "feasible": feasible,
            "minimum_by_heavy_count": minima}


def shared_period_capacity(s, p, t, q, v):
    N = len(p) + 1
    HA = {0} | {w for w in range(1, N) if 2 * p[w - 1] == s}
    HB = {0} | {w for w in range(1, N) if 2 * q[w - 1] == t}
    SA = {min(w, w ^ v) for w in HA}
    SB = {min(w, w ^ v) for w in HB}
    intersection = len(SA & SB)
    prod = p[v - 1] * q[v - 1]
    assert prod % intersection == 0
    return min(N // 2, prod // intersection)


def verify_shared_period_capacities_n3():
    N = 8
    cached = {}
    for mask in range(1 << N):
        s, p = pair_vector(mask, N)
        for v in range(1, N):
            P = {min(x, x ^ v) for x in range(N)
                 if (mask >> x & 1) and (mask >> (x ^ v) & 1)}
            cached[mask, v] = (s, p, P)
    checks = 0
    strict = 0
    for v in range(1, N):
        for ma in range(1 << N):
            s, p, A = cached[ma, v]
            for mb in range(1 << N):
                t, q, B = cached[mb, v]
                actual = len({min(x ^ y, x ^ y ^ v) for x in A for y in B})
                capacity = shared_period_capacity(s, p, t, q, v)
                assert actual <= capacity <= min(N // 2, len(A) * len(B))
                strict += capacity < min(N // 2, len(A) * len(B))
                checks += 1
    sizes = (6, 6, 4, 0, 4, 0, 4, 0)
    pairs = ((2,2,2,2,2,2,3), (2,2,2,2,3,2,2),
             (2,2,2,0,0,0,0), (0,0,0,0,0,0,0),
             (2,0,0,2,2,0,0), (0,0,0,0,0,0,0),
             (2,0,0,0,0,2,2), (0,0,0,0,0,0,0))
    types, _ = actual_types(N)
    assert all(pairs[a] in types[sizes[a]] for a in range(N))
    old = []
    new = []
    for v in range(1, N):
        old.append(sum(pairs[a][v - 1] * pairs[a ^ v][v - 1]
                       for a in range(N) if a < (a ^ v)))
        new.append(sum(shared_period_capacity(sizes[a], pairs[a],
                                             sizes[a ^ v], pairs[a ^ v], v)
                       for a in range(N) if a < (a ^ v)))
    assert min(old) >= N // 2 and new[5] == 2 < N // 2
    return {"all_subset_pair_direction_checks": checks,
            "strict_capacity_improvements": strict,
            "true_local_24_point_assignment": {
                "sizes": sizes, "pairs": pairs,
                "product_totals": old, "period_capacity_totals": new,
                "refuted_direction": 6}}


def main():
    start = time.perf_counter()
    result = {"arithmetic": "Python integers only", "solver_dependency": None,
              "definitions": {"pair_vector_order": "nonzero v in integer order 1..2^n-1",
                              "Walsh_character": "(-1)^popcount(x & xi)"}}
    types4, witnesses = actual_types(16)
    classification = []
    square_total = 0
    phase_rejections = 0
    actual_total = 0
    for s in range(9):
        squared = {}
        for p, W in square_candidates(16, s):
            assert p not in squared
            assert is_T_local(s, p)
            squared[p] = W
        repaired = {p for p, W in squared.items()
                    if not four_frequency_obstruction(16, s, W)}
        assert repaired == types4[s]
        difference = set(squared) - types4[s]
        assert all(four_frequency_obstruction(16, s, squared[p]) for p in difference)
        factor = 1 if s == 8 else 2
        square_total += factor * len(squared)
        phase_rejections += factor * len(difference)
        actual_total += factor * len(types4[s])
        classification.append({"size": s, "actual_types": len(types4[s]),
                               "square_spectral_types": len(squared),
                               "four_frequency_rejections": len(difference)})
    assert (actual_total, square_total, phase_rejections) == (3967, 5227, 1260)
    result["dimension_four"] = {"all_subsets_checked": 65536,
                                "complement_reduces_sizes_to": "0..8",
                                "rows": classification,
                                "actual_total": actual_total,
                                "square_total": square_total,
                                "phase_rejections": phase_rejections,
                                "exact_after_four_frequency_cut": True}
    types3, _ = actual_types(8)
    rows3 = []
    for s in range(9):
        metric = set()
        squares = set()
        for p in product(range(s // 2 + 1), repeat=7):
            if not is_T_local(s, p):
                continue
            metric.add(p)
            W = spectrum(s, p)
            if all(z >= 0 and isqrt(z) ** 2 == z for z in W):
                squares.add(p)
        assert squares == types3[s]
        rows3.append({"size": s, "actual": len(types3[s]), "T_local": len(metric),
                      "square": len(squares)})
    result["dimension_three"] = {"all_subsets_checked": 256, "rows": rows3,
                                  "square_condition_exact": True}
    p_fake3 = (0, 0, 2, 1, 1, 1, 1)
    assert is_T_local(4, p_fake3) and p_fake3 not in types3[4]
    result["strict_square_cut_example"] = {"n": 3, "s": 4, "p": p_fake3,
                                           "spectrum": spectrum(4, p_fake3)}
    p_fake4 = (1, 1, 2, 1, 2, 2, 3, 0, 3, 3, 2, 3, 2, 2, 1)
    assert is_T_local(8, p_fake4) and complete_signs(8, p_fake4) is None
    positive_support = (1, 2, 4, 7)
    W_positive = [64] + [0] * 15
    for xi in positive_support:
        W_positive[xi] = 16
    c = tuple(x // 16 for x in walsh(W_positive))
    positive = complete_signs(8, tuple(x // 2 for x in c[1:]))
    assert positive is not None
    result["strict_phase_cut_example"] = {"n": 4, "s": 8, "p": p_fake4,
                                          "spectrum": spectrum(8, p_fake4),
                                          "frequency_xor": 7,
                                          "all_16_sign_choices_rejected": True,
                                          "positive_control_support": positive_support,
                                          "positive_control": positive}
    family_checks = []
    for n in range(4, 9):
        N = 1 << n
        for support in [(1, 2, 4, 7), (1, 2, 4, 8), (11, 13, 14, 15)]:
            W = [N * N // 4] + [0] * (N - 1)
            for xi in support:
                W[xi] = N * N // 16
            raw = walsh(W)
            assert all(x % N == 0 for x in raw)
            c = tuple(x // N for x in raw)
            p = tuple(x // 2 for x in c[1:])
            assert all(x % 2 == 0 for x in c[1:]) and is_T_local(N // 2, p)
            answer = complete_signs(N // 2, p)
            assert (answer is not None) == (xor_all(support) == 0)
            family_checks.append({"n": n, "support": support,
                                  "realizable": answer is not None})
    result["four_frequency_family_checks"] = family_checks
    result["subspace_occupancy_bounds"] = verify_subspace_bounds(types4, 16)
    types2, _ = actual_types(4)
    result["heavy_allocation_checks"] = verify_heavy_allocation_n2(types2)
    result["shared_period_capacity_checks"] = verify_shared_period_capacities_n3()
    type_rows = [{"s": s, "p": list(p), "witness_mask": witnesses[(s, p)]}
                 for s in range(17) for p in sorted(types4[s])]
    type_text = json.dumps(type_rows, separators=(",", ":")) + "\n"
    output = Path(__file__).resolve().parent
    (output / "local_types_n4.json").write_text(type_text)
    result["local_types_n4_sha256"] = hashlib.sha256(type_text.encode()).hexdigest()
    result["seconds"] = round(time.perf_counter() - start, 3)
    (output / "theory_receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
