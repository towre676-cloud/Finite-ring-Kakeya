#!/usr/bin/env python3
"""Explicit integer duals for heavy/light n5 profile exclusions.

The sweep uses NumPy only for speed. Certificate verification below is pure
Python and recomputes every dual value from the pinned spectrum/capacity data.
No inherited ledger is mutated.
"""
from pathlib import Path
from collections import defaultdict
import argparse
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research_round6/after_round6_survivors.txt"
SPEC = ROOT / "research_round6/imported_claude_round4/data/spec32.csv"
MTAB = ROOT / "research_round6/imported_claude_round4/data/Mtable.txt"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data():
    spectra = defaultdict(set)
    for line in SPEC.read_text().splitlines():
        row = list(map(int, line.split(",")))
        w, histogram = row[0], tuple(row[1:-1])
        assert len(histogram) == 17 and sum(histogram) == 31
        spectra[w].add(histogram)
    M = [[0] * 17] + [[0] + list(map(int, line.split())) for line in MTAB.read_text().splitlines()]
    assert len(M) == 17 and all(len(row) == 17 for row in M)
    profiles = []
    for line in INPUT.read_text().splitlines():
        values = list(map(int, line.split()))
        s, maximum = values[:2]
        weights = values[3:]
        assert len(weights) == s and max(weights) == maximum and sum(weights) <= 93
        profiles.append(weights)
    return spectra, M, profiles


def dual(ell, u, spectra, M):
    t = ell // 2
    assert 2 <= ell <= 17 and t <= u <= 18
    g = [max([0] + [2 * M[p][q] - u * q for q in range(1, t + 1)]) for p in range(17)]
    G = {w: max(sum(h[p] * g[p] for p in range(17)) for h in histograms)
         for w, histograms in spectra.items()}
    return g, G


def check_certificate(certificate, profiles, spectra, M, cache):
    weights = profiles[certificate["source_line"] - 1]
    ell, u = certificate["light_ceiling"], certificate["price"]
    key = ell, u
    if key not in cache:
        cache[key] = dual(ell, u, spectra, M)
    g, G = cache[key]
    heavy = certificate["heavy_positions"]
    assert len(set(heavy)) == len(heavy) and all(0 <= p < len(weights) for p in heavy)
    heavy = set(heavy)
    assert all(w <= ell for i, w in enumerate(weights) if i not in heavy)
    h = len(heavy)
    assert h <= 8
    lhs = 32 * (31 - h * (h - 1) // 2)
    light_pairs = sum(w * (w - 1) // 2 for i, w in enumerate(weights) if i not in heavy)
    rhs = u * light_pairs + sum(G[weights[i]] for i in heavy)
    assert lhs == certificate["required_capacity_twice"] and rhs == certificate["available_upper_bound_twice"]
    assert lhs > rhs
    return lhs - rhs


def sweep(optional=False):
    import numpy as np
    started = time.monotonic()
    spectra, M, profiles = data()
    N = len(profiles)
    counts = np.zeros((N, 19), dtype=np.int32)
    padded = np.zeros((N, 17), dtype=np.int32)
    lengths = np.array([len(w) for w in profiles], dtype=np.int32)
    for i, weights in enumerate(profiles):
        for w in weights:
            counts[i, w] += 1
        padded[i, :len(weights)] = weights
    chosen = np.full(N, -1, dtype=np.int32)
    certificates = []
    parameters = []
    for ell in range(2, 18):
        t = ell // 2
        mandatory_count = counts[:, ell + 1:].sum(axis=1)
        for u in range(t, 19):
            g, G = dual(ell, u, spectra, M)
            coefficients = np.array([u * w * (w - 1) // 2 if w <= ell else G[w] for w in range(19)], dtype=np.int32)
            # w=0 and1 are absent from profiles; G is needed only aboveell.
            costs = counts @ coefficients
            lhs = 32 * (31 - mandatory_count * (mandatory_count - 1) // 2)
            passing = (chosen < 0) & (mandatory_count <= 8) & (lhs > costs)
            for i in np.flatnonzero(passing):
                i = int(i)
                heavy = [j for j, w in enumerate(profiles[i]) if w > ell]
                certificate = {"source_line": i + 1, "light_ceiling": ell, "price": u,
                               "heavy_positions": heavy, "required_capacity_twice": int(lhs[i]),
                               "available_upper_bound_twice": int(costs[i]), "method": "mandatory_heavy"}
                certificates.append(certificate); chosen[i] = len(certificates) - 1
            if optional:
                # Promote eligible light vertices in increasing marginal cost.
                # Padded entries and mandatory-heavy entries receive infinity.
                delta_by_weight = np.array([G.get(w, 0) - u * w * (w - 1) // 2 for w in range(19)], dtype=np.int32)
                deltas = delta_by_weight[padded]
                eligible = (padded >= 2) & (padded <= ell)
                deltas = np.where(eligible, deltas, 1000000)
                order = np.argsort(deltas, axis=1, kind="stable")
                sorted_deltas = np.take_along_axis(deltas, order, axis=1)
                running = costs.copy()
                for promoted in range(1, 9):
                    running = running + sorted_deltas[:, promoted - 1]
                    h = mandatory_count + promoted
                    need = 32 * (31 - h * (h - 1) // 2)
                    passing = (chosen < 0) & (h <= 8) & (sorted_deltas[:, promoted - 1] < 1000000) & (need > running)
                    for i in np.flatnonzero(passing):
                        i = int(i)
                        heavy = [j for j, w in enumerate(profiles[i]) if w > ell]
                        heavy += [int(j) for j in order[i, :promoted]]
                        heavy.sort()
                        certificate = {"source_line": i + 1, "light_ceiling": ell, "price": u,
                                       "heavy_positions": heavy, "required_capacity_twice": int(need[i]),
                                       "available_upper_bound_twice": int(running[i]), "method": "optional_heavy_promotion"}
                        certificates.append(certificate); chosen[i] = len(certificates) - 1
            parameters.append({"light_ceiling": ell, "price": u, "g": g,
                               "G_by_weight": {str(w): value for w, value in sorted(G.items())}})
    certificates.sort(key=lambda c: c["source_line"])
    cache = {}
    margins = [check_certificate(c, profiles, spectra, M, cache) for c in certificates]
    by_support = defaultdict(lambda: {"examined": 0, "proposed_cuts": 0})
    for weights in profiles:
        by_support[len(weights)]["examined"] += 1
    for certificate in certificates:
        by_support[len(profiles[certificate["source_line"] - 1])]["proposed_cuts"] += 1
    report = {"status": "PASS_EXPLICIT_DUAL_CERTIFICATES_NO_LEDGER_MUTATION",
              "optional_heavy_promotion": optional, "profiles_examined": N,
              "proposed_exclusions": len(certificates), "minimum_strict_margin_twice": min(margins, default=None),
              "by_support": {str(s): row for s, row in sorted(by_support.items())},
              "dual_parameters": parameters, "certificates": certificates,
              "source_hashes": {str(path.relative_to(ROOT)): sha(path) for path in [INPUT, SPEC, MTAB, Path(__file__)]},
              "all_certificates_rechecked_with_python_integers": True,
              "ledger_updated": False, "seconds": round(time.monotonic() - started, 6)}
    path = HERE / ("OPTIONAL_HEAVY_DUAL_DIAGNOSTIC.json" if optional else "MANDATORY_HEAVY_DUAL_DIAGNOSTIC.json")
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["status", "optional_heavy_promotion", "profiles_examined", "proposed_exclusions", "by_support", "seconds"]}, indent=2))


def verify(path):
    report = json.loads(Path(path).read_text())
    for relative, digest in report["source_hashes"].items():
        assert sha(ROOT / relative) == digest
    spectra, M, profiles = data()
    cache = {}
    rows = report["certificates"]
    assert len(rows) == report["proposed_exclusions"]
    assert len({r["source_line"] for r in rows}) == len(rows)
    margins = [check_certificate(row, profiles, spectra, M, cache) for row in rows]
    print(json.dumps({"status": "PASS_ALL_RECORDED_INTEGER_DUAL_CERTIFICATES",
                      "certificates": len(rows), "minimum_margin_twice": min(margins, default=None)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--optional", action="store_true")
    parser.add_argument("--verify")
    arguments = parser.parse_args()
    verify(arguments.verify) if arguments.verify else sweep(arguments.optional)
