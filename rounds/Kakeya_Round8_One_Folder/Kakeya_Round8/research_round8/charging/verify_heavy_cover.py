#!/usr/bin/env python3
"""Finite corroboration, Boolean controls, and explicit heavy-set inventory.

No SAT solver is called. No Round7 artifact is modified. Raw weight-profile
counts are illustrative budget counts, not a subtraction from a frontier.
"""
from collections import Counter
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import hashlib
import importlib.util
import json
import time

from heavy_cover_cut import add_heavy_cover_cut

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MASKS = (377850134, 411136406, 671697334, 2185856310)
BASE = ROOT / "research_round6/joint_maxima/encode_joint_maxima.py"
BASE_SHA = "776af5c5699f5e153990cdfb8b0897d690202c9895dd95134eec9b8df295feba"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def differences(points):
    return {a ^ b for a, b in combinations(points, 2)}


def support(mask):
    result = [0] + [v for v in range(1, 32) if mask >> v & 1]
    require(len(result) == 13 and differences(result) == set(range(1, 32)), "Invalid requested support")
    return result


def small_geometry():
    basis = {0, 1, 2, 4, 8, 16}
    extras = sorted(set(range(32)) - basis)
    rows = []
    for weight, maximum in ((8, 25), (9, 28)):
        histogram = Counter()
        for extra in combinations(extras, weight - 6):
            size = len(differences(basis | set(extra)))
            require(size <= maximum, "Difference bound failed")
            histogram[size] += 1
        rows.append({"weight": weight, "normalized_affine_basis_cases": sum(histogram.values()),
                     "largest_difference_set": max(histogram), "distribution": dict(sorted(histogram.items()))})
    for h in range(8):
        require(301 + 23 * h - 8 * h*h > 0, "Small-heavy contradiction failed")
    require(96 > 75 and 3*5 < 16 and 2*5 + 1 < 16, "Matching capacity arithmetic failed")
    # Every actual light fibre has at most three directions; a 3-set has
    # precisely the nonzero points of a binary plane.
    light_sets = 0
    for weight in (2, 3):
        for fibre in combinations(range(32), weight):
            directions = differences(fibre)
            require(len(directions) == (1 if weight == 2 else 3), "Light direction count failed")
            if weight == 3:
                a, b, c = sorted(directions)
                require(a ^ b ^ c == 0, "Three-point direction set is not a plane")
            light_sets += 1
    return {"normalized_difference_checks": rows, "actual_light_fibres_checked": light_sets,
            "lower_affine_rank_bound": 15, "small_heavy_integer_cases": 8}


def boolean_and_pattern_checks():
    require(sha(BASE) == BASE_SHA, "Frozen baseline changed")
    spec = importlib.util.spec_from_file_location("r8_cover_boolean_baseline", BASE)
    B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)
    spectra = [(2,), (3,), (4,), (11,)]
    rows = []
    total_assignments = 0
    controls = []
    for mask in MASKS:
        S = support(mask)
        f = B.CNF(); f.z = {}; f.r8_heavy = {}
        for v in S:
            for i in range(len(spectra)):
                f.z[v, i] = f.new()
            f.exactly_one([f.z[v, i] for i in range(len(spectra))])
            f.r8_heavy[v] = f.new()
        records = []
        original_unary = f.unary_sum
        def recorded_unary(literals):
            outputs = original_unary(literals)
            records.append((list(literals), list(outputs)))
            return outputs
        f.unary_sum = recorded_unary
        before = len(f.cl)
        metadata = add_heavy_cover_cut(f, S, spectra)
        clauses = f.cl[before:]
        histogram = Counter(); hub_histogram = Counter(); allowed = []
        first_allowed_values = None
        for index_mask in range(1 << 13):
            H = [v for i, v in enumerate(S) if index_mask >> i & 1]
            D = differences(H)
            histogram[len(H), len(D)] += 1
            if index_mask & 1:
                hub_histogram[len(H), len(D)] += 1
            expected = len(H) >= 10 and len(D) == 31
            values = [False] * (f.n + 1)
            for i, v in enumerate(S):
                heavy = bool(index_mask >> i & 1)
                values[f.r8_heavy[v]] = heavy
                selected = (2 if heavy else 0) + ((index_mask >> ((i+1) % 13)) & 1)
                values[f.z[v, selected]] = True
            for inputs, outputs in records:
                count = sum(values[x] if x > 0 else not values[-x] for x in inputs)
                for j, output in enumerate(outputs):
                    require(output > 0, "Unexpected negative counter output")
                    values[output] = count >= j + 1
            for (a, b), variable in f.r8_heavy_cover_edge_ands.items():
                values[variable] = values[f.r8_heavy[a]] and values[f.r8_heavy[b]]
            satisfied = all(any(values[x] if x > 0 else not values[-x] for x in clause) for clause in clauses)
            require(satisfied == expected, "Boolean cut differs from exact heavy-cover predicate")
            total_assignments += 1
            if expected and index_mask & 1:
                allowed.append({"heavy_index_mask": index_mask, "heavy_residue_mask": sum(1 << v for v in H),
                                "heavy_residues": H, "light_residues": [v for v in S if v not in H],
                                "heavy_count": len(H)})
                if first_allowed_values is None:
                    first_allowed_values = values
        require(first_allowed_values is not None, "No positive Boolean control available")
        for label, variable in (("wrong_heavy_edge_AND", next(iter(f.r8_heavy_cover_edge_ands.values()))),
                                ("wrong_tenth_counter_output", f.r8_heavy_cover_count_outputs[9])):
            bad = list(first_allowed_values); bad[variable] = not bad[variable]
            require(not all(any(bad[x] if x > 0 else not bad[-x] for x in clause) for clause in clauses),
                    "Corrupted auxiliary assignment accepted")
            controls.append({"support_mask": mask, "control": label, "rejected": True})
        by_h = Counter(row["heavy_count"] for row in allowed)
        expected_counts = {377850134: (4, 21, 11, 1), 411136406: (6, 31, 12, 1),
                           671697334: (1, 24, 12, 1), 2185856310: (2, 24, 12, 1)}
        require(tuple(by_h[h] for h in range(10, 14)) == expected_counts[mask], "Heavy-pattern count changed")
        rows.append({"nonzero_support_mask": mask, "support": S,
                     "hub": 0, "hub_weight_assumption_for_inventory": "exactly 11, therefore heavy",
                     "all_boolean_patterns_checked": 8192,
                     "hub_heavy_patterns_with_at_least_nine_heavy_before_cut": 794,
                     "remaining_hub_heavy_patterns": len(allowed),
                     "remaining_by_heavy_size": dict(sorted(by_h.items())),
                     "complete_all_pattern_histogram": [{"heavy_count": h, "difference_count": d, "patterns": c}
                                                        for (h, d), c in sorted(histogram.items())],
                     "complete_hub_heavy_histogram": [{"heavy_count": h, "difference_count": d, "patterns": c}
                                                       for (h, d), c in sorted(hub_histogram.items())],
                     "allowed_heavy_patterns": allowed, "encoder_metadata": metadata})
    return {"total_boolean_assignments_checked": total_assignments, "negative_controls": controls, "cases": rows}


def raw_weight_profiles():
    counts = Counter()
    for outer in combinations_with_replacement(range(2, 12), 12):
        weights = (11,) + outer
        if sum(weights) <= 93:
            counts[sum(w >= 4 for w in weights)] += 1
    require(sum(counts.values()) == 183064, "Raw profile enumeration changed")
    return {"scope": "Raw sorted weight profiles only: support13, exact maximum11, weights>=2, total<=93. Not an inherited survivor ledger.",
            "raw_profiles": sum(counts.values()), "by_heavy_count": dict(sorted(counts.items())),
            "retained_by_at_least_nine_heavy": sum(c for h, c in counts.items() if h >= 9),
            "retained_by_at_least_ten_heavy": sum(c for h, c in counts.items() if h >= 10),
            "new_whole_support_or_affine_class_exclusions_claimed": 0}


def main():
    start = time.monotonic()
    result = {"status": "RUNNING"}
    output = HERE / "HEAVY_COVER_REPLAY.json"
    output.write_text(json.dumps(result) + "\n")
    try:
        result.update(small_geometry=small_geometry(), patterns=boolean_and_pattern_checks(),
                      raw_budget_profiles=raw_weight_profiles())
        paths = [Path(__file__), HERE / "heavy_cover_cut.py", HERE / "HEAVY_DIFFERENCE_COVER_THEOREM.md", BASE,
                 ROOT / "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md"]
        result.update(status="PASS_HEAVY_DIFFERENCE_COVER_THEOREM_CONTROLS_AND_EXACT_PATTERN_INVENTORY",
                      source_hashes={str(p.relative_to(ROOT)): sha(p) for p in paths},
                      SAT_solver_called=False, new_whole_support_exclusions_claimed=0,
                      seconds=round(time.monotonic() - start, 6))
        output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"status": result["status"], "boolean_assignments": result["patterns"]["total_boolean_assignments_checked"],
                          "remaining_patterns": {row["nonzero_support_mask"]: row["remaining_hub_heavy_patterns"] for row in result["patterns"]["cases"]},
                          "seconds": result["seconds"]}, indent=2))
    except BaseException as error:
        result.update(status="FAIL", error=repr(error))
        output.write_text(json.dumps(result, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
