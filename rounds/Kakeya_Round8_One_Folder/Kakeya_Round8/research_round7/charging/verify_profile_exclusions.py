#!/usr/bin/env python3
"""Independent integer replay of explicit heavy/light profile certificates.

This verifier does not import a search/optimization implementation.  It reads
the inherited spectrum and sumset tables, constructs the coefficient bounds
anew, and checks each displayed heavy subset.  The complete census and the
geometric charging lemma are mathematical dependencies, stated in the report.
"""
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import math

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = {
    "research_round6/after_round6_survivors.txt": "d96cd6794e87bede959d813c39e36aefafa42d5c243a465b19f6ec4c065cb52c",
    "research_round6/imported_claude_round4/data/spec32.csv": "a61140936f55aa278de40d1b66e537138048322d152141ccc436d42c0f8fefab",
    "research_round6/imported_claude_round4/data/Mtable.txt": "c67d586fa469e243f633d2def4f36ff605ea61290c782ffb5c717ac21c9372e9",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_inputs():
    for path, digest in PINS.items():
        require(sha(ROOT / path) == digest, "Changed inherited input: " + path)
    source_lines = (ROOT / next(iter(PINS))).read_text().splitlines()
    profiles = []
    for line in source_lines:
        support, maximum, old_energy, *weights = map(int, line.split())
        require(len(weights) == support and max(weights) == maximum, "Bad profile dimensions")
        require(13 <= support <= 17 and 12 <= maximum <= 18, "Unexpected frontier cell")
        require(all(2 <= w <= maximum for w in weights) and sum(weights) <= 93,
                "Invalid active-fibre profile")
        profiles.append(tuple(weights))
    require(len(profiles) == len(set(profiles)) == 186482, "Missing or duplicated inherited profile")

    histograms = defaultdict(set)
    for line in (ROOT / "research_round6/imported_claude_round4/data/spec32.csv").read_text().splitlines():
        row = tuple(map(int, line.split(",")))
        weight, histogram = row[0], row[1:-1]
        require(len(histogram) == 17 and all(c >= 0 for c in histogram) and sum(histogram) == 31,
                "Malformed spectrum")
        require(sum(p * count for p, count in enumerate(histogram)) == math.comb(weight, 2),
                "Spectrum violates exact pair budget")
        require(all(count == 0 for p, count in enumerate(histogram) if p > weight // 2),
                "Spectrum exceeds disjoint-pair limit")
        histograms[weight].add(histogram)
    require(all(histograms[w] for w in range(2, 19)), "Missing weight in spectrum census")

    capacity = [[0] * 17]
    capacity += [[0] + list(map(int, line.split())) for line in
                 (ROOT / "research_round6/imported_claude_round4/data/Mtable.txt").read_text().splitlines()]
    require(len(capacity) == 17 and all(len(row) == 17 for row in capacity), "Malformed capacity table")
    for p in range(17):
        for q in range(17):
            require(0 <= capacity[p][q] <= min(16, p*q) and capacity[p][q] == capacity[q][p],
                    "Capacity table sanity check failed")
    elementary = [[small_capacity(p, q) if q <= 3 else 0 for q in range(17)] for p in range(17)]
    for p in range(17):
        for q in range(4):
            require(capacity[p][q] == elementary[p][q], "Legacy small-light table differs from elementary formula")
    return source_lines, profiles, histograms, elementary


def small_capacity(p, q):
    """Proved bounds; no census of quotient sumsets is used by this verifier."""
    if q == 0:
        return 0
    if q == 1:
        return p
    if q == 2:
        return min(16, 2*p)
    if q == 3:
        return min(16, 3*p, p+8)
    raise ValueError("Unreviewed larger light pair-set")


def direction_bound(h):
    # Current accepted certificate family uses only the elementary pair bound.
    require(0 <= h <= 8, "Unreviewed heavy-cardinality refinement")
    return math.comb(h, 2)


def check(row, profiles, histograms, capacity, coefficient_cache):
    line = row["source_line"]
    require(type(line) is int and 1 <= line <= len(profiles), "Invalid source line")
    weights = profiles[line - 1]
    ell, price = row["light_ceiling"], row["price"]
    require(type(ell) is int and 2 <= ell <= 7 and type(price) is int and price >= ell // 2,
            "Invalid light ceiling or price")
    positions = row["heavy_positions"]
    require(isinstance(positions, list) and all(type(i) is int and 0 <= i < len(weights) for i in positions),
            "Invalid heavy positions")
    require(len(set(positions)) == len(positions), "Duplicated heavy endpoint")
    heavy = set(positions)
    require(all(w <= ell for i, w in enumerate(weights) if i not in heavy),
            "Light fibre exceeds specified ceiling")

    key = ell, price
    if key not in coefficient_cache:
        excess = []
        for p in range(17):
            excess.append(max(0, *(2*capacity[p][q] - price*q for q in range(1, ell//2 + 1))))
        bounds = {}
        for w, spectra in histograms.items():
            bounds[w] = max(sum(count * excess[p] for p, count in enumerate(spectrum))
                            for spectrum in spectra)
        # Check the actual finite price inequalities, independently of the maximizer.
        for p in range(17):
            for q in range(ell//2 + 1):
                require(2*capacity[p][q] <= price*q + excess[p], "Heavy/light price failed")
        for p in range(ell//2 + 1):
            for q in range(ell//2 + 1):
                require(2*capacity[p][q] <= price*(p+q), "Light/light price failed")
        coefficient_cache[key] = excess, bounds
    _, bounds = coefficient_cache[key]
    required = 32 * (31 - direction_bound(len(heavy)))
    light_pairs = sum(math.comb(w, 2) for i, w in enumerate(weights) if i not in heavy)
    available = price*light_pairs + sum(bounds[weights[i]] for i in heavy)
    require(type(row["required_capacity_twice"]) is int and required == row["required_capacity_twice"],
            "Incorrect required capacity")
    require(type(row["available_upper_bound_twice"]) is int and available == row["available_upper_bound_twice"],
            "Incorrect resource upper bound")
    require(required > available, "No strict contradiction")
    return {"source_line": line, "weights": weights, "support": len(weights), "maximum": max(weights),
            "required_twice": required, "available_twice": available, "strict_margin_twice": required-available,
            "light_pair_budget": light_pairs, "heavy_costs": [bounds[weights[i]] for i in sorted(heavy)],
            "certificate": row}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", default="research_round7/dense_encoder/OPTIONAL_HEAVY_DUAL_DIAGNOSTIC.json")
    args = parser.parse_args()
    path = ROOT / args.certificate
    report = json.loads(path.read_text())
    for relative, digest in report["source_hashes"].items():
        require(sha(ROOT / relative) == digest, "Changed certificate discovery source")
    source_lines, profiles, histograms, capacity = read_inputs()
    rows = report["certificates"]
    require(len(rows) == report["proposed_exclusions"] and len({r["source_line"] for r in rows}) == len(rows),
            "Wrong or duplicated certificate count")
    cache = {}
    verified = [check(row, profiles, histograms, capacity, cache) for row in rows]
    excluded = {row["source_line"] for row in verified}
    before, removed, after = Counter(), Counter(), Counter()
    cells = defaultdict(lambda: {"before": 0, "excluded": 0, "remaining": 0})
    remaining_lines = []
    for line, weights in enumerate(profiles, 1):
        s, m = len(weights), max(weights)
        before[s] += 1
        cells[s, m]["before"] += 1
        if line in excluded:
            removed[s] += 1
            cells[s, m]["excluded"] += 1
        else:
            after[s] += 1
            cells[s, m]["remaining"] += 1
            remaining_lines.append(source_lines[line-1])

    # These controls test rejection by this verifier, not the discovery optimizer.
    controls = []
    for label, field, value in [("wrong_upper_bound", "available_upper_bound_twice", -1),
                                 ("invalid_source_line", "source_line", 0),
                                 ("negative_price", "price", -1),
                                 ("duplicate_heavy_endpoint", "heavy_positions", [0, 0])]:
        altered = deepcopy(rows[0]); altered[field] = value
        try:
            check(altered, profiles, histograms, capacity, cache)
        except (ValueError, KeyError, TypeError):
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted certificate accepted: " + label)

    HERE.mkdir(parents=True, exist_ok=True)
    survivor_path = HERE / "after_integer_dual_survivors.txt"
    survivor_path.write_text("\n".join(remaining_lines) + "\n")
    excluded_path = HERE / "EXCLUDED_PROFILES.jsonl"
    excluded_path.write_text("".join(json.dumps(row, separators=(",", ":")) + "\n" for row in verified))
    receipt = {
        "status": "PASS_ROOT_SEPARATE_INTEGER_CERTIFICATE_REPLAY",
        "profiles_before": len(profiles), "whole_profiles_excluded": len(verified),
        "profiles_remaining": len(remaining_lines),
        "minimum_strict_margin_twice": min(row["strict_margin_twice"] for row in verified),
        "by_support": {str(s): {"before": before[s], "excluded": removed[s], "remaining": after[s]}
                       for s in sorted(before)},
        "by_support_and_maximum": [{"support": s, "maximum": m, **value}
                                   for (s, m), value in sorted(cells.items())],
        "input_pins": PINS,
        "discovery_report": str(path.relative_to(ROOT)), "discovery_report_sha256": sha(path),
        "verifier_sha256": sha(Path(__file__)),
        "survivors_file": str(survivor_path.relative_to(ROOT)), "survivors_sha256": sha(survivor_path),
        "excluded_file": str(excluded_path.relative_to(ROOT)), "excluded_sha256": sha(excluded_path),
        "negative_controls": controls,
        "example": verified[0],
        "capacity_coefficients": "Elementary formulas M(p,1)=p, M(p,2)<=min(2p,16), M(p,3)<=min(3p,p+8,16); no quotient-sumset census premise.",
        "small_light_capacity_lemma_sha256": sha(HERE / "SMALL_LIGHT_CAPACITY.md"),
        "scope": "Every placement and fibre shape of these weight profiles, in both rings, under the complete inherited spectrum census and the elementary small-light capacity bounds.",
        "dependency_boundary": [
            "The heavy/light geometric charging lemma connects these finite inequalities to Kakeya coverage.",
            "The spectrum census is an inherited finite dependency, pinned here and reproduced in the earlier checkpoint.",
            "The old quotient sumset table is checked for agreement only; every coefficient used here is recomputed from an elementary formula proved in SMALL_LIGHT_CAPACITY.md.",
            "Lean checks the abstract pricing/summation/strict-gap core; the census and Python implementation are not fully formalized.",
            "Separate model review is reproducibility, not independent human refereeing."]}
    (HERE / "PROFILE_EXCLUSIONS_REPLAY.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ["status", "profiles_before", "whole_profiles_excluded", "profiles_remaining", "by_support"]}, indent=2))


if __name__ == "__main__":
    main()
