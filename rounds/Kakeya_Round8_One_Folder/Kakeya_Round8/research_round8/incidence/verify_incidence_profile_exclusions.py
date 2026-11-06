#!/usr/bin/env python3
"""Replay 16 whole-profile exclusions and byte-preserving frontier coverage.

The geometric premise is the analytic missing-direction incidence theorem:
for nine heavy fibres of weight >=4, |D(H)| <=28 leaves at least three
missing directions, each requiring three active light incidences when the
maximum is 12 or 13. Four light fibres supply at most eight incidences.
No spectrum census, sumset table, SAT formula or solver is read here.

Run --write once to create the explicit certificate and reduced frontier;
ordinary replay only verifies them and updates its procedural receipt.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research_round7/charging/after_integer_dual_survivors.txt"
SOURCE_SHA256 = "1c493598b5586dec62b736df01c10df441751a222e0926691a20c330853c2df5"
PROOF_PINS = {
    "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md":
        "4d52fcdb7b60b09cc52934ab3fab575d07b4320789879de664592c3a129c9034",
    "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md":
        "cb5671d36c1b857023aee9481491881d56cf9aef27734b104208b6fbbb6b5ba8",
}
CERTIFICATE = HERE / "INCIDENCE_PROFILE_EXCLUSIONS.json"
SURVIVORS = HERE / "after_incidence_survivors.txt"
RECEIPT = HERE / "INCIDENCE_PROFILE_EXCLUSIONS_REPLAY.json"
EXPECTED_LINES = [162466, 164715, 164996, 165380, 165455, 165520,
                  173686, 173712, 173882, 174087, 174165, 174266,
                  174475, 174540, 174673, 174700]
EXPECTED_BEFORE_SUPPORT = {13: 85340, 14: 74373, 15: 19514, 16: 3853, 17: 396}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, indent=2) + "\n").encode("utf-8")


def atomic_write(path, data):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def read_inputs():
    source_bytes = (ROOT / SOURCE).read_bytes()
    require(digest(source_bytes) == SOURCE_SHA256, "Changed inherited frontier input")
    for path, expected in PROOF_PINS.items():
        require(digest((ROOT / path).read_bytes()) == expected, "Changed analytic proof: " + path)
    raw_lines = source_bytes.splitlines(keepends=True)
    require(len(raw_lines) == 183476, "Unexpected inherited profile count")
    profiles = []
    for number, raw_line in enumerate(raw_lines, 1):
        require(raw_line.endswith(b"\n"), "Unterminated inherited source line")
        values = list(map(int, raw_line.split()))
        require(len(values) >= 4, "Malformed inherited source line")
        s, m, old_energy, *weights = values
        require(len(weights) == s and 13 <= s <= 17 and 12 <= m <= 18,
                "Unexpected inherited profile dimensions at line " + str(number))
        require(weights == sorted(weights, reverse=True) and max(weights) == m,
                "Malformed sorted maximum at line " + str(number))
        require(all(2 <= w <= m for w in weights) and sum(weights) <= 93,
                "Invalid inherited active-fibre weights")
        profiles.append((s, m, old_energy, tuple(weights)))
    require(len({p[3] for p in profiles}) == len(profiles), "Duplicated inherited weight profile")
    return raw_lines, profiles


def is_excluded(profile):
    s, maximum, _, weights = profile
    return s == 13 and maximum in (12, 13) and sum(w >= 4 for w in weights) == 9


def make_row(number, raw_line, profile):
    require(is_excluded(profile), "Profile is outside the certified exclusion predicate")
    s, maximum, old_energy, weights = profile
    heavy_positions = [i for i, w in enumerate(weights) if w >= 4]
    n2, n3 = weights.count(2), weights.count(3)
    P = maximum // 2
    r = (16 + P - 1) // P
    missing_lower = 31 - 28
    required = r * missing_lower
    available = n2 + 2*n3
    require(P == 6 and len(heavy_positions) == 9 and n2 == 0 and n3 == 4,
            "Unexpected incidence-certificate parameters")
    require(required == 9 > available == 8, "No strict missing-incidence contradiction")
    return {
        "source_line": number,
        "source_line_sha256": digest(raw_line),
        "source_line_ascii": raw_line.decode("ascii"),
        "support_size": s,
        "maximum": maximum,
        "inherited_energy_metadata_not_used": old_energy,
        "weights": list(weights),
        "total_weight": sum(weights),
        "heavy_positions_zero_based": heavy_positions,
        "heavy_count": len(heavy_positions),
        "light_weight2_count": n2,
        "light_weight3_count": n3,
        "maximum_pair_count": P,
        "minimum_active_light_incidences_per_missing_direction": r,
        "heavy_difference_upper_bound": 28,
        "missing_direction_lower_bound": missing_lower,
        "required_light_incidences_lower_bound": required,
        "available_light_incidences_upper_bound": available,
        "strict_gap": required - available,
        "reason": "Nine heavy fibres leave at least three missing directions; 9 required light incidences exceed the available 8.",
    }


def check_row(row, raw_lines, profiles):
    require(isinstance(row, dict), "Certificate row must be an object")
    number = row.get("source_line")
    require(type(number) is int and 1 <= number <= len(profiles), "Invalid certificate source line")
    expected = make_row(number, raw_lines[number-1], profiles[number-1])
    # Canonical JSON equality also distinguishes booleans from integer fields.
    require(json_bytes(row) == json_bytes(expected), "Certificate row differs from its exact source-line derivation")
    return number


def build_expected(raw_lines, profiles):
    before_support = Counter(p[0] for p in profiles)
    require(dict(before_support) == EXPECTED_BEFORE_SUPPORT, "Inherited support counts differ")
    rows = [make_row(i, raw, profile)
            for i, (raw, profile) in enumerate(zip(raw_lines, profiles), 1)
            if is_excluded(profile)]
    excluded = {row["source_line"] for row in rows}
    require([row["source_line"] for row in rows] == EXPECTED_LINES, "Excluded source-line inventory differs")
    require(Counter(row["maximum"] for row in rows) == {12: 10, 13: 6}, "Per-maximum exclusion counts differ")
    require(all(sum(w >= 4 for w in weights) >= 9 for s, m, _, weights in profiles
                if s == 13 and m in (12, 13)), "Unexpected lower-heavy profile in this inherited cell")
    surviving_lines = [raw for i, raw in enumerate(raw_lines, 1) if i not in excluded]
    survivor_bytes = b"".join(surviving_lines)
    require(len(surviving_lines) == 183460, "Reduced profile count differs")
    before_cell = Counter((p[0], p[1]) for p in profiles)
    removed_cell = Counter((r["support_size"], r["maximum"]) for r in rows)
    after_cell = before_cell - removed_cell
    by_support = {str(s): {"before": before_support[s],
                          "excluded": sum(n for (cell_s, _), n in removed_cell.items() if cell_s == s),
                          "remaining": sum(n for (cell_s, _), n in after_cell.items() if cell_s == s)}
                  for s in sorted(before_support)}
    by_maximum = {str(m): {"before": sum(n for (_, cell_m), n in before_cell.items() if cell_m == m),
                          "excluded": sum(n for (_, cell_m), n in removed_cell.items() if cell_m == m),
                          "remaining": sum(n for (_, cell_m), n in after_cell.items() if cell_m == m)}
                  for m in sorted({p[1] for p in profiles})}
    certificate = {
        "format": "kakeya-round8-incidence-whole-profile-exclusions-v1",
        "input_file": SOURCE,
        "input_sha256": SOURCE_SHA256,
        "input_profiles": len(raw_lines),
        "producer_verifier": str(Path(__file__).resolve().relative_to(ROOT)),
        "producer_verifier_sha256": digest(Path(__file__).read_bytes()),
        "analytic_proof_pins": PROOF_PINS,
        "scope": "All support placements and fibre shapes of these profiles, for both Z/4Z and F2[epsilon]/(epsilon^2).",
        "mathematical_dependencies": [
            "Every nine-point subset of F2^5 has at most 28 nonzero pair differences, as proved in the pinned analytic nine-point note.",
            "For at least nine heavy fibres, the missing-direction set contains no complete binary two-space minus zero.",
            "Every missing direction needs at least ceil(16/floor(maximum/2)) active light incidences; weight2/3 fibres supply at most 1/2 over all missing directions.",
            "No complete fibre-spectrum census, quotient-sumset table, SAT encoding or solver is a premise of these new 16 exclusions."
        ],
        "excluded_profiles": len(rows),
        "remaining_profiles": len(surviving_lines),
        "survivor_file": str(SURVIVORS.relative_to(ROOT)),
        "survivor_sha256": digest(survivor_bytes),
        "by_support": by_support,
        "by_maximum": by_maximum,
        "by_support_and_maximum": [
            {"support_size": s, "maximum": m, "before": before_cell[s, m],
             "excluded": removed_cell[s, m], "remaining": after_cell[s, m]}
            for s, m in sorted(before_cell)],
        "certificates": rows,
    }
    return certificate, survivor_bytes


def negative_controls(rows, raw_lines, profiles, survivor_bytes):
    altered = []
    for label, field, value in [
        ("invalid_source_line", "source_line", 0),
        ("uncertified_source_line", "source_line", 1),
        ("wrong_source_hash", "source_line_sha256", "0"*64),
        ("wrong_heavy_count", "heavy_count", 10),
        ("wrong_required_incidence", "required_light_incidences_lower_bound", 8),
        ("wrong_available_incidence", "available_light_incidences_upper_bound", 9),
        ("wrong_weights", "weights", [12]*13),
        ("boolean_in_integer_field", "strict_gap", True),
    ]:
        row = deepcopy(rows[0]); row[field] = value
        try:
            check_row(row, raw_lines, profiles)
        except (ValueError, KeyError, TypeError):
            altered.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted certificate accepted: " + label)
    split = survivor_bytes.splitlines(keepends=True)
    wrong_order = b"".join([split[1], split[0], *split[2:]])
    require(wrong_order != survivor_bytes, "Reordered survivor control did not change data")
    require(b"".join(split[:-1]) != survivor_bytes, "Dropped survivor control did not change data")
    altered += [{"control": "survivor_order_change", "rejected": True},
                {"control": "missing_survivor_line", "rejected": True}]
    return altered


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing deterministic certificate and survivor files")
    args = parser.parse_args()
    started = time.monotonic()
    atomic_write(RECEIPT, json_bytes({"status": "RUNNING", "write_mode": args.write}))
    try:
        raw_lines, profiles = read_inputs()
        expected, survivor_bytes = build_expected(raw_lines, profiles)
        expected_bytes = json_bytes(expected)
        if args.write:
            for path, data in ((CERTIFICATE, expected_bytes), (SURVIVORS, survivor_bytes)):
                require(not path.exists() or path.read_bytes() == data,
                        "Refusing to overwrite a different semantic artifact: " + path.name)
            for path, data in ((CERTIFICATE, expected_bytes), (SURVIVORS, survivor_bytes)):
                if not path.exists():
                    atomic_write(path, data)
        require(CERTIFICATE.read_bytes() == expected_bytes, "Stored certificate differs from exact regeneration")
        stored = json.loads(CERTIFICATE.read_text())
        checked = [check_row(row, raw_lines, profiles) for row in stored["certificates"]]
        require(checked == EXPECTED_LINES and len(set(checked)) == len(checked), "Certificate coverage differs")
        require(SURVIVORS.read_bytes() == survivor_bytes, "Survivor bytes or their original order differ")
        controls = negative_controls(stored["certificates"], raw_lines, profiles, survivor_bytes)
        receipt = {
            "status": "PASS_EXACT_INCIDENCE_PROFILE_REPLAY",
            "profiles_before": 183476,
            "whole_profiles_excluded": 16,
            "profiles_remaining": 183460,
            "coverage": {
                "all_input_profiles_accounted_for": True,
                "every_removed_source_line_has_exact_certificate": True,
                "every_other_source_line_preserved_byte_identically_and_in_order": True,
                "excluded_source_lines": checked,
                "energy_metadata_used_in_exclusion": False,
            },
            "by_support": expected["by_support"],
            "by_maximum": expected["by_maximum"],
            "by_support_and_maximum": expected["by_support_and_maximum"],
            "input_file": SOURCE,
            "input_sha256": SOURCE_SHA256,
            "certificate_file": str(CERTIFICATE.relative_to(ROOT)),
            "certificate_sha256": digest(CERTIFICATE.read_bytes()),
            "survivor_file": str(SURVIVORS.relative_to(ROOT)),
            "survivor_sha256": digest(survivor_bytes),
            "verifier_sha256": digest(Path(__file__).read_bytes()),
            "analytic_proof_pins": PROOF_PINS,
            "negative_controls": controls,
            "scope": expected["scope"],
            "dependency_boundary": "The pinned hand proofs supply the geometry; this replay checks all exact integers and the complete byte-preserving ledger partition. No SAT case is credited here, and the Python implementation is not proof-assistant formalized.",
            "elapsed_seconds": round(time.monotonic()-started, 6),
        }
        atomic_write(RECEIPT, json_bytes(receipt))
        print(json.dumps({key: receipt[key] for key in
                          ("status", "profiles_before", "whole_profiles_excluded", "profiles_remaining", "by_support")}, indent=2))
    except BaseException as error:
        atomic_write(RECEIPT, json_bytes({"status": "FAIL", "exception_type": type(error).__name__,
                                        "message": str(error), "elapsed_seconds": round(time.monotonic()-started, 6)}))
        raise


if __name__ == "__main__":
    main()
