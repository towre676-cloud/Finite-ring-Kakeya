#!/usr/bin/env python3
"""Exact Teichmuller fibre traces, with a separate direct-arithmetic checker.

Standard library only.  No imports from the uploaded packages.

    python3 trace_law.py --profile standard --receipt trace_receipt.json
    python3 trace_law.py --profile quick --receipt quick_receipt.json

The theorem and the precise finite verification scope are in TRACE_THEOREMS.md.
The direct oracle constructs Teichmuller representatives by root lifting; the
formula engine constructs them by modular exponentiation.  The direct oracle
uses integer arithmetic or truncated polynomial multiplication, not the carry
recurrence being checked.
"""

from __future__ import annotations

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
from itertools import product
import json
from math import comb, isqrt
from pathlib import Path
import platform
import random
import re
import time


def prime(p: int) -> bool:
    return isinstance(p, int) and not isinstance(p, bool) and p >= 2 and all(
        p % d for d in range(2, isqrt(p) + 1))


def valid_length(length: int) -> bool:
    return isinstance(length, int) and not isinstance(length, bool) and length >= 1


@lru_cache(maxsize=None)
def teich_table(p: int, length: int) -> tuple[int, ...]:
    """Canonical representatives in Z/p^length, by the power formula."""
    if not prime(p) or not valid_length(length):
        raise ValueError("p must be prime and length must be a positive integer")
    modulus = p ** length
    return tuple(pow(a, p ** (length - 1), modulus) for a in range(p))


def gamma(p: int, a: int, b: int, flat: bool = False) -> int:
    """The first Teichmuller addition carry; arguments are field elements."""
    if flat:
        return 0
    a, b = a % p, b % p
    return ((a ** p + b ** p - (a + b) ** p) // p) % p


def eta(p: int, a: int, b: int, flat: bool = False) -> int:
    """Second carry, evaluated by the integral ghost-coordinate expression.

    The power and division are integer operations before final reduction.
    Replacing the integer pth power by its residue-field value is invalid.
    """
    if flat:
        return 0
    a, b = a % p, b % p
    big_g = (a ** p + b ** p - (a + b) ** p) // p
    numerator = a ** (p * p) + b ** (p * p) - (a + b) ** (p * p) - p * big_g ** p
    assert numerator % (p * p) == 0
    return (numerator // (p * p)) % p


@lru_cache(maxsize=None)
def carry_tables(p: int, flat: bool) -> tuple[tuple[tuple[int, ...], ...], tuple[tuple[int, ...], ...]]:
    return (
        tuple(tuple(gamma(p, a, b, flat) for b in range(p)) for a in range(p)),
        tuple(tuple(eta(p, a, b, flat) for b in range(p)) for a in range(p)),
    )


class TraceEngine:
    """The proved diagonal-carry recurrence, in scalar Teichmuller digits."""

    def __init__(self, p: int, length: int, flat: bool = False):
        if not prime(p) or not valid_length(length):
            raise ValueError("p must be prime and length must be a positive integer")
        self.p, self.length, self.flat = p, length, flat
        self.tau = teich_table(p, length)
        self.g, self.e = carry_tables(p, flat)

    @classmethod
    def from_code(cls, code: str) -> "TraceEngine":
        """Parse only the documented Wp^length and Tp^length canonical forms."""
        matched = re.fullmatch(r"([WT])([1-9][0-9]*)\^([1-9][0-9]*)", code) if isinstance(code, str) else None
        if matched is None:
            raise ValueError("ring code must have canonical form Wp^length or Tp^length")
        kind, p, length = matched.groups()
        return cls(int(p), int(length), flat=kind == "T")

    def affine(self, x: tuple[int, ...], v: tuple[int, ...], s: tuple[int, ...]) -> tuple[int, ...]:
        """Digits of x+s*v; all three inputs have exactly self.length digits."""
        p, length = self.p, self.length
        if len(x) != length or len(v) != length or len(s) != length:
            raise ValueError("wrong digit length")
        if self.flat:
            return tuple((x[k] + sum(s[i] * v[k - i] for i in range(k + 1))) % p
                         for k in range(length))
        carry = 0
        result = []
        tau = self.tau
        for k in range(length):
            column = carry + tau[x[k]]
            for i in range(k + 1):
                column += tau[(s[i] * v[k - i]) % p]
            digit = column % p
            result.append(digit)
            carry = (column - tau[digit]) // p
        return tuple(result)

    def affine3(self, x: tuple[int, ...], v: tuple[int, ...], s: tuple[int, ...]) -> tuple[int, ...]:
        """The closed length-three formula, independently of affine()."""
        if self.length != 3:
            raise ValueError("affine3 requires length 3")
        p, g, e = self.p, self.g, self.e
        a, b, c = x
        al, be, de = v
        sg, r, u = s
        q0 = (sg * al) % p
        base_carry = g[a][q0]
        product_first = (sg * be + r * al) % p
        product_carry = g[(sg * be) % p][(r * al) % p]
        first = (b + product_first + base_carry) % p
        second = (
            c + sg * de + r * be + u * al + e[a][q0] + product_carry
            + g[b][product_first] + g[(b + product_first) % p][base_carry]
        ) % p
        return ((a + q0) % p, first, second)

    def affine3_compact(self, x: tuple[int, ...], v: tuple[int, ...], s: tuple[int, ...]) -> tuple[int, ...]:
        """Equivalent compact formula isolating gamma(B_sigma, r*alpha)."""
        if self.length != 3:
            raise ValueError("affine3_compact requires length 3")
        p, g, e = self.p, self.g, self.e
        a, b, c = x
        al, be, de = v
        sg, r, u = s
        sg_al, sg_be = (sg * al) % p, (sg * be) % p
        base_carry = g[a][sg_al]
        middle_offset = (b + sg_be + base_carry) % p
        top_offset = (c + sg * de + e[a][sg_al] + g[b][sg_be]
                      + g[(b + sg_be) % p][base_carry]) % p
        return ((a + sg_al) % p, (middle_offset + r * al) % p,
                (top_offset + r * be + u * al + g[middle_offset][(r * al) % p]) % p)

    def vector_affine(self, x: tuple[tuple[int, ...], ...],
                      v: tuple[tuple[int, ...], ...],
                      s: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
        """Inputs and output are coordinate-major digit tuples."""
        if len(x) != len(v):
            raise ValueError("vector dimensions differ")
        return tuple(self.affine(xi, vi, s) for xi, vi in zip(x, v))

    def fibre_trace(self, x: tuple[tuple[int, ...], ...],
                    v: tuple[tuple[int, ...], ...], sigma: int) -> frozenset[tuple[int, ...]]:
        """Higher digits over a+sigma*alpha, flattened by layer then coordinate."""
        if not any(vi[0] for vi in v):
            raise ValueError("direction must be primitive")
        traces = set()
        for tail in product(range(self.p), repeat=self.length - 1):
            y = self.vector_affine(x, v, (sigma % self.p,) + tail)
            traces.add(tuple(yi[k] for k in range(1, self.length) for yi in y))
        return frozenset(traces)


class DirectRing:
    """Independent oracle: actual integers or truncated polynomial arithmetic."""

    def __init__(self, p: int, length: int, flat: bool):
        if not prime(p) or not valid_length(length):
            raise ValueError("p must be prime and length must be a positive integer")
        self.p, self.length, self.flat = p, length, flat
        self.q = p ** length
        self.code = f"{'T' if flat else 'W'}{p}^{length}"
        if flat:
            self.tau = tuple(range(p))
        else:
            roots = []
            for a in range(p):
                root = a
                place = p
                for _ in range(1, length):
                    modulus = place * p
                    candidates = [root + c * place for c in range(p)
                                  if pow(root + c * place, p, modulus) == (root + c * place) % modulus]
                    assert len(candidates) == 1
                    root = candidates[0]
                    place = modulus
                roots.append(root)
            self.tau = tuple(roots)
        self.raw_digits = [tuple((a // p ** k) % p for k in range(length)) for a in range(self.q)]
        self.digits = [None] * self.q
        for ds in product(range(p), repeat=length):
            z = sum((p ** k) * self.tau[d] for k, d in enumerate(ds)) % self.q
            assert self.digits[z] is None
            self.digits[z] = ds
        assert all(ds is not None for ds in self.digits)

    def add(self, a: int, b: int) -> int:
        if not self.flat:
            return (a + b) % self.q
        return sum(((x + y) % self.p) * self.p ** k
                   for k, (x, y) in enumerate(zip(self.raw_digits[a], self.raw_digits[b])))

    def mul(self, a: int, b: int) -> int:
        if not self.flat:
            return (a * b) % self.q
        da, db = self.raw_digits[a], self.raw_digits[b]
        return sum((sum(da[i] * db[k - i] for i in range(k + 1)) % self.p) * self.p ** k
                   for k in range(self.length))

    def encode(self, ds: tuple[int, ...]) -> int:
        return sum(self.p ** k * self.tau[d % self.p] for k, d in enumerate(ds)) % self.q


def rank_mod(rows: list[tuple[int, ...]], p: int) -> int:
    if not rows:
        return 0
    basis: dict[int, list[int]] = {}
    for row in rows:
        row = [a % p for a in row]
        for col in sorted(basis):
            if row[col]:
                factor = row[col]
                row = [(x - factor * y) % p for x, y in zip(row, basis[col])]
        pivot = next((j for j, a in enumerate(row) if a), None)
        if pivot is not None:
            inv = pow(row[pivot], -1, p)
            basis[pivot] = [(a * inv) % p for a in row]
    return len(basis)


def affine_dimension(points: frozenset[tuple[int, ...]], p: int) -> int | None:
    """Return affine dimension, or None if the point set is not an affine space."""
    if not points:
        return None
    origin = next(iter(points))
    dim = rank_mod([tuple((a - b) % p for a, b in zip(z, origin)) for z in points], p)
    return dim if len(points) == p ** dim else None


def affine_incidence_counts(p: int, n: int) -> dict[str, int]:
    """Proved length-three mixed-characteristic census at odd prime p.

    Counts incidences (a distinct affine line, one of its residue points),
    not distinct subsets that happen to occur as traces.
    """
    if not prime(p) or p == 2 or not valid_length(n):
        raise ValueError("an odd prime p and a positive integer n are required")
    total = p ** (5 * n - 4) * ((p ** n - 1) // (p - 1))
    affine = p ** (4 * n - 3) * (((2 * p - 1) ** n - p ** n) // (p - 1))
    support_sum = sum(comb(n, m) * (p - 1) ** (m - 1) * p ** (5 * n - 3 - m)
                      for m in range(1, n + 1))
    assert affine == support_sum
    return {"total": total, "affine": affine, "nonaffine": total - affine}


def direct_trace(ring: DirectRing, x: tuple[int, ...], v: tuple[int, ...], sigma: int) -> frozenset[tuple[int, ...]]:
    points = set()
    for s in range(sigma, ring.q, ring.p):
        y = [ring.digits[ring.add(xi, ring.mul(s, vi))] for xi, vi in zip(x, v)]
        points.add(tuple(yi[k] for k in range(1, ring.length) for yi in y))
    return frozenset(points)


def carry_check() -> dict:
    out = {}
    for p in (2, 3, 5, 7):
        for flat in (False, True):
            ring = DirectRing(p, 3, flat)
            checked = 0
            eta_nonzero = 0
            for a, b in product(range(p), repeat=2):
                actual = ring.digits[ring.add(ring.tau[a], ring.tau[b])]
                predicted = ((a + b) % p, gamma(p, a, b, flat), eta(p, a, b, flat))
                assert actual == predicted, (ring.code, a, b, actual, predicted)
                eta_nonzero += predicted[2] != 0
                checked += 1
            out[ring.code] = {"all_digit_pairs": checked, "second_carry_nonzero_pairs": eta_nonzero,
                              "mismatches": 0}
    return out


def boundary_and_coordinate_checks() -> dict:
    boundary = {}
    conversion = {}
    for p in (2, 3, 5, 7):
        for flat in (False, True):
            for length in (1, 2):
                ring = DirectRing(p, length, flat)
                engine = TraceEngine(p, length, flat)
                count = 0
                for x, v, s in product(range(ring.q), repeat=3):
                    actual = ring.digits[ring.add(x, ring.mul(s, v))]
                    predicted = engine.affine(ring.digits[x], ring.digits[v], ring.digits[s])
                    assert actual == predicted
                    count += 1
                if length == 1:
                    assert engine.fibre_trace(((0,), (0,)), ((1,), (0,)), sigma=0) == frozenset({()})
                boundary[ring.code] = {"all_scalar_triples": count, "mismatches": 0}
            ring = DirectRing(p, 3, flat)
            count = 0
            for a, delta, epsilon in product(range(p), repeat=3):
                _, e1, e2 = ring.digits[a]
                z = ring.add(a, ring.add(ring.mul(p, ring.tau[delta]), ring.mul(p * p, ring.tau[epsilon])))
                predicted = (a, (e1 + delta) % p, (e2 + epsilon + gamma(p, e1, delta, flat)) % p)
                assert ring.digits[z] == predicted
                count += 1
            conversion[ring.code] = {"all_coordinate_conversion_triples": count, "mismatches": 0}
    invalid_codes = ["", "W2", "W2^", "W2^0", "W2^-1", "W4^2", "T1^3", "X2^3",
                     "w2^3", "W02^3", "W2^03", "W2^3junk", None, 7]
    invalid_parameters = [(1, 3), (4, 3), (2, 0), (2, -1), (2, 2.5), (2.5, 3), (True, 3), (2, True)]
    for code in invalid_codes:
        try:
            TraceEngine.from_code(code)
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid code accepted", code))
    for p, length in invalid_parameters:
        try:
            TraceEngine(p, length)
        except ValueError:
            pass
        else:
            raise AssertionError(("invalid parameters accepted", p, length))
    for code in ("W2^1", "T2^1", "W3^4", "T7^4"):
        TraceEngine.from_code(code)
    return {"length1_and_length2": boundary, "length3_slope_conversion": conversion,
            "invalid_codes_rejected": len(invalid_codes), "invalid_parameter_pairs_rejected": len(invalid_parameters)}


def scalar_checks(profile: str, rng: random.Random) -> dict:
    out = {}
    for p in (2, 3, 5, 7):
        for length in (3, 4):
            for flat in (False, True):
                ring = DirectRing(p, length, flat)
                engine = TraceEngine(p, length, flat)
                assert flat or ring.tau == engine.tau
                q, ds = ring.q, ring.digits
                exhaustive = (p <= 3) or (profile == "standard" and p == 5 and length == 3)
                if profile == "quick":
                    exhaustive = p == 2
                if exhaustive:
                    triples = ((x, v, s) for v in range(q) for s in range(q) for x in range(q))
                    scope = "all scalar triples (x,v,s), including nonunits"
                    total = q ** 3
                else:
                    # Deterministic coverage of each element in each role, all
                    # v,s pairs at zero intercept, then independent general triples.
                    sample_n = 20000 if profile == "standard" else 2000
                    include_all_products = profile == "standard" and q <= 625
                    def chosen():
                        for z in range(q):
                            yield (z, q - 1, q - 1)
                            yield (q - 1, z, q - 1)
                            yield (q - 1, q - 1, z)
                        if include_all_products:
                            for v in range(q):
                                for s in range(q):
                                    yield (0, v, s)
                        for _ in range(sample_n):
                            yield tuple(rng.randrange(q) for _ in range(3))
                    triples = chosen()
                    scope = ("each scalar element in each role; "
                             + ("all scalar products at x=0; " if include_all_products else "")
                             + "seeded general scalar triples")
                    total = 3 * q + (q * q if include_all_products else 0) + sample_n
                count = closed_count = 0
                # Cache direct products to keep the exhaustive oracle cheap.
                multiplication = [[ring.mul(s, v) for s in range(q)] for v in range(q)] if q <= 343 else None
                addition = [[ring.add(x, z) for x in range(q)] for z in range(q)] if q <= 343 else None
                for x, v, s in triples:
                    prod = multiplication[v][s] if multiplication is not None else ring.mul(s, v)
                    actual = ds[addition[prod][x] if addition is not None else ring.add(x, prod)]
                    predicted = engine.affine(ds[x], ds[v], ds[s])
                    assert actual == predicted, (ring.code, x, v, s, actual, predicted)
                    if length == 3:
                        closed = engine.affine3(ds[x], ds[v], ds[s])
                        assert actual == closed, (ring.code, x, v, s, actual, closed)
                        compact = engine.affine3_compact(ds[x], ds[v], ds[s])
                        assert actual == compact, (ring.code, x, v, s, actual, compact)
                        closed_count += 1
                    count += 1
                assert count == total
                out[ring.code] = {"scope": scope, "exhaustive_scalar_triples": exhaustive,
                                  "scalar_cases": count, "closed_length3_cases": closed_count,
                                  "mismatches": 0}
                print(f"scalar {ring.code}: {count} cases", flush=True)
    return out


def vector_checks(profile: str, rng: random.Random) -> dict:
    out = {}
    cases_per_dimension = 48 if profile == "standard" else 8
    for p in (2, 3, 5, 7):
        for length in (3, 4):
            for flat in (False, True):
                ring = DirectRing(p, length, flat)
                engine = TraceEngine(p, length, flat)
                count = points = 0
                for n in (2, 3):
                    for _ in range(cases_per_dimension):
                        x = tuple(rng.randrange(ring.q) for _ in range(n))
                        while True:
                            v = tuple(rng.randrange(ring.q) for _ in range(n))
                            if any(vi % p for vi in v):
                                break
                        xd, vd = tuple(ring.digits[z] for z in x), tuple(ring.digits[z] for z in v)
                        for sigma in range(p):
                            actual = direct_trace(ring, x, v, sigma)
                            predicted = engine.fibre_trace(xd, vd, sigma)
                            assert actual == predicted, (ring.code, n, x, v, sigma)
                            assert len(actual) == p ** (length - 1)
                            for depth in range(1, length):
                                prefixes = Counter(z[:depth * n] for z in actual)
                                assert len(prefixes) == p ** depth
                                assert set(prefixes.values()) == {p ** (length - 1 - depth)}
                            if flat or (p == 2 and length == 3):
                                assert affine_dimension(actual, p) == length - 1
                            if not flat and p > 2 and length == 3:
                                middle = [ring.digits[ring.add(xi, ring.mul(ring.tau[sigma], vi))][1]
                                          for xi, vi in zip(x, v)]
                                ratios = {(bi * pow(vi % p, -1, p)) % p
                                          for bi, vi in zip(middle, v) if vi % p}
                                predicted_dim = 2 if len(ratios) == 1 else None
                                assert affine_dimension(actual, p) == predicted_dim
                            points += len(actual)
                            count += 1
                out[ring.code] = {"scope": "seeded primitive lines in dimensions 2 and 3; all residue fibres",
                                  "lines_per_dimension": cases_per_dimension, "fibre_sets": count,
                                  "point_incidences": points, "prefix_balance_checked": True,
                                  "odd_prime_affine_criterion_checked": not flat and p > 2 and length == 3,
                                  "mismatches": 0}
                print(f"vector {ring.code}: {count} full fibre sets", flush=True)
    return out


def census(p: int, length: int, flat: bool) -> dict:
    """Every distinct affine line in the two-dimensional direct ring.

    Directions (1,m), m arbitrary, and (m,1), m in the maximal ideal,
    with transversal intercepts (0,b), respectively (b,0).
    """
    ring = DirectRing(p, length, flat)
    q = ring.q
    dims = Counter()
    first_nonaffine = None
    lines = 0
    for vertical in (False, True):
        for m in (range(0, q, p) if vertical else range(q)):
            v = (m, 1) if vertical else (1, m)
            for b in range(q):
                x = (b, 0) if vertical else (0, b)
                lines += 1
                for sigma in range(p):
                    trace = direct_trace(ring, x, v, sigma)
                    dim = affine_dimension(trace, p)
                    dims["nonaffine" if dim is None else str(dim)] += 1
                    if dim is None and first_nonaffine is None:
                        first_nonaffine = {"x": list(x), "v": list(v), "sigma": sigma,
                                           "higher_digit_trace": [list(z) for z in sorted(trace)]}
    expected_lines = (q + q // p) * q
    assert lines == expected_lines
    assert sum(dims.values()) == lines * p
    if flat or (p == 2 and length <= 3):
        assert dims == {str(length - 1): lines * p}
    else:
        assert dims["nonaffine"] > 0
    formula_counts = None
    if not flat and p > 2 and length == 3:
        formula_counts = affine_incidence_counts(p, 2)
        assert dims == {"2": formula_counts["affine"], "nonaffine": formula_counts["nonaffine"]}
    return {"scope": "all distinct affine lines in R^2, all residue fibres",
            "directions": q + q // p, "lines": lines,
            "line_fibre_incidences": lines * p,
            "affine_dimensions_or_nonaffine": dict(sorted(dims.items())),
            "proved_formula_agrees": True if formula_counts is not None else None,
            "proved_formula_counts": formula_counts,
            "first_nonaffine": first_nonaffine}


def obstruction_checks() -> dict:
    odd = {}
    for p in (3, 5, 7):
        ring = DirectRing(p, 3, False)
        trace = direct_trace(ring, (0, 0), (1, 1 + p), 1)
        assert affine_dimension(trace, p) is None
        values = [gamma(p, 1, r) for r in range(p)]
        assert values[0] == values[-1] == 0 and any(values)
        odd[str(p)] = {"ring": ring.code, "x": [0, 0], "v": [1, 1 + p], "sigma": 1,
                       "gamma(1,r)": values, "trace_nonaffine": True}
    ring = DirectRing(2, 4, False)
    points = {(s, (3 * s) % 16) for s in range(0, 16, 2)}
    assert (2, 6) in points and (4, 12) in points and (6, 10) not in points
    assert affine_dimension(direct_trace(ring, (0, 0), (1, 3), 0), 2) is None
    flat = DirectRing(2, 4, True)
    assert affine_dimension(direct_trace(flat, (0, 0), (1, 3), 0), 2) == 3
    # Isolate the multiplication carry that would be lost by coefficientwise
    # convolution of Teichmuller digits in mixed characteristic.
    mixed3 = DirectRing(2, 3, False)
    assert mixed3.digits[mixed3.mul(3, 3)] == (1, 0, 0)
    naive_convolution = TraceEngine(2, 3, True).affine((0, 0, 0), (1, 1, 0), (1, 1, 0))
    assert naive_convolution == (1, 0, 1)
    return {"odd_prime_length3": odd,
            "binary_length4": {"ring": "W2^4", "x": [0, 0], "v": [1, 3], "sigma": 0,
                               "present_points": [[2, 6], [4, 12]],
                               "missing_digitwise_sum": [6, 10], "mixed_nonaffine": True,
                               "flat_affine_dimension": 3},
            "multiplication_carry_witness": {"ring": "W2^3", "s": 3, "v": 3,
                                             "actual_product_digits": [1, 0, 0],
                                             "incorrect_carryless_digits": [1, 0, 1]}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("quick", "standard"), default="standard")
    parser.add_argument("--receipt", type=Path, default=Path(__file__).with_name("trace_receipt.json"))
    parser.add_argument("--seed", type=int, default=20261101)
    args = parser.parse_args()
    started = time.perf_counter()
    rng = random.Random(args.seed)
    receipt = {
        "schema": "kakeya-teichmuller-trace/1.0",
        "status": "running",
        "profile": args.profile,
        "seed": args.seed,
        "python": platform.python_version(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "proof_file": "TRACE_THEOREMS.md",
        "proof_status": "general theorems have symbolic proofs; finite checks validate the implementation",
        "oracle": "integer arithmetic / truncated polynomials; Teichmuller roots lifted independently",
    }
    receipt["carry_identities"] = carry_check()
    receipt["boundary_and_coordinate_checks"] = boundary_and_coordinate_checks()
    receipt["scalar_affine_checks"] = scalar_checks(args.profile, rng)
    receipt["vector_fibre_checks"] = vector_checks(args.profile, rng)
    census_cases = ((2, 3), (2, 4), (3, 3), (3, 4), (5, 3)) if args.profile == "standard" else ((2, 3), (2, 4))
    receipt["complete_plane_line_censuses"] = {}
    for p, length in census_cases:
        for flat in (False, True):
            key = f"{'T' if flat else 'W'}{p}^{length}"
            receipt["complete_plane_line_censuses"][key] = census(p, length, flat)
            print(f"census {key}: complete", flush=True)
    receipt["explicit_obstructions"] = obstruction_checks()
    receipt["totals"] = {
        "scalar_cases": sum(x["scalar_cases"] for x in receipt["scalar_affine_checks"].values()),
        "closed_length3_cases": sum(x["closed_length3_cases"] for x in receipt["scalar_affine_checks"].values()),
        "vector_fibre_sets": sum(x["fibre_sets"] for x in receipt["vector_fibre_checks"].values()),
        "vector_point_incidences": sum(x["point_incidences"] for x in receipt["vector_fibre_checks"].values()),
        "census_line_fibre_incidences": sum(x["line_fibre_incidences"] for x in receipt["complete_plane_line_censuses"].values()),
        "mismatches": 0,
    }
    receipt["wall_seconds"] = round(time.perf_counter() - started, 3)
    receipt["status"] = "passed"
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"receipt": str(args.receipt), "status": receipt["status"],
                      "totals": receipt["totals"], "wall_seconds": receipt["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
