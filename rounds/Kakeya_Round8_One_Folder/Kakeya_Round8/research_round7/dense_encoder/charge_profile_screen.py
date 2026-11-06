#!/usr/bin/env python3
"""Diagnostic application of a general heavy/light charge to the n5 ledger.

No existing ledger is changed. Any cuts are recorded with exact scalar
witnesses and census/input hashes for independent review.
"""
from pathlib import Path
from collections import Counter, defaultdict
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = ROOT / "research_round6/after_round6_survivors.txt"
SPECTRA = ROOT / "research_round6/imported_claude_round4/data/spec32.csv"


def maximum_excess():
    values = defaultdict(lambda: [0] * 17)
    for line in SPECTRA.read_text().splitlines():
        row = list(map(int, line.split(",")))
        w, histogram = row[0], row[1:-1]
        assert len(histogram) == 17 and sum(histogram) == 31
        for r in range(17):
            values[w][r] = max(values[w][r], sum(max(p - r, 0) * count for p, count in enumerate(histogram)))
    return dict(values)


def witness(weights, excess):
    frequencies = Counter(weights)
    maximum = max(weights)
    # Suffix aggregates for all thresholds and prices.
    for ell in range(2, maximum + 1):
        light_pairs = sum(count * w * (w - 1) // 2 for w, count in frequencies.items() if w <= ell)
        heavy = [(w, count) for w, count in frequencies.items() if w > ell]
        h = sum(count for w, count in heavy)
        missing_directions = 31 - h * (h - 1) // 2
        if missing_directions <= 0:
            continue
        t = ell // 2
        lhs = 16 * missing_directions
        for r in range(max(1, t), maximum // 2 + 1):
            heavy_excess = sum(count * excess[w][r] for w, count in heavy)
            rhs = r * light_pairs + t * heavy_excess
            if lhs > rhs:
                return {"light_weight_upper_bound": ell, "light_pair_upper_bound": t,
                        "price": r, "heavy_vertices": h, "light_pair_resource": light_pairs,
                        "maximum_heavy_excess": heavy_excess, "required_capacity": lhs,
                        "available_upper_bound": rhs, "strict_margin": lhs - rhs}
    return None


def main():
    start = time.monotonic()
    excess = maximum_excess()
    rows, cuts = [], []
    all_by_support, cut_by_support = Counter(), Counter()
    for number, line in enumerate(INPUT.read_text().splitlines(), 1):
        values = list(map(int, line.split()))
        size, maximum, old_energy = values[:3]
        weights = values[3:]
        assert len(weights) == size and max(weights) == maximum and sum(weights) <= 93
        all_by_support[size] += 1
        proof = witness(weights, excess)
        if proof:
            cuts.append({"source_line": number, "profile_line": line, "weights": weights,
                         "maximum": maximum, "support_size": size, "witness": proof})
            cut_by_support[size] += 1
    report = {"status": "COMPLETED_CHARGING_DIAGNOSTIC_NO_LEDGER_MUTATION",
              "profiles_examined": sum(all_by_support.values()), "proposed_exclusions": len(cuts),
              "by_support": {str(s): {"examined": all_by_support[s], "proposed_cuts": cut_by_support[s]}
                             for s in sorted(all_by_support)},
              "maximum_excess_by_weight_and_price": {str(w): values for w, values in sorted(excess.items())},
              "cuts": cuts,
              "source_hashes": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in [INPUT, SPECTRA, Path(__file__)]},
              "scope": "Profile-only bound using |D(H)|<=C(h,2). Any exclusions need separate review before ledger credit.",
              "seconds": round(time.monotonic() - start, 6)}
    (HERE / "CHARGING_PROFILE_DIAGNOSTIC.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in ["status", "profiles_examined", "proposed_exclusions", "by_support", "seconds"]}, indent=2))


if __name__ == "__main__":
    main()
