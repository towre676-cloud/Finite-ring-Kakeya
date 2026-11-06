#!/usr/bin/env python3
"""Replay the cumulative 128 whole-profile missing-incidence exclusions.

The first16 certificates and their183460-line frontier are immutable inputs.
This extension certifies128 original Round7 lines, including112 new lines,
and verifies both direct and staged byte-identical frontier regeneration.
No spectrum census, capacity table, SAT formula or solver is read.
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
PRIOR_PINS = {
    "research_round8/incidence/verify_incidence_profile_exclusions.py":
        "99b30853580d4372056b9fd5ce89aedbcc33155de3d12ce6b4b9b7ccc96d494e",
    "research_round8/incidence/INCIDENCE_PROFILE_EXCLUSIONS.json":
        "5afcdb87d3711760d6854db2c9a822ce4f43406e606d6b09567ed043f7de156a",
    "research_round8/incidence/after_incidence_survivors.txt":
        "892032e51ecdac50c351759cba7b8b2eb42fa8c3b102583ac687780e7a0a4835",
}
PROOF_PINS = {
    "research_round8/incidence/SUPPORT13_MAX15_HEAVY_COROLLARY.md":
        "80673ba770f061123e9a984e299ec1d3b948650ff268ce84f34c67adc4d4b407",
    "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md":
        "4d52fcdb7b60b09cc52934ab3fab575d07b4320789879de664592c3a129c9034",
    "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md":
        "cb5671d36c1b857023aee9481491881d56cf9aef27734b104208b6fbbb6b5ba8",
}
CERTIFICATE = HERE / "EXTENDED_INCIDENCE_PROFILE_EXCLUSIONS.json"
SURVIVORS = HERE / "after_extended_incidence_survivors.txt"
RECEIPT = HERE / "EXTENDED_INCIDENCE_PROFILE_REPLAY.json"
PRIOR_CERTIFICATE = HERE / "INCIDENCE_PROFILE_EXCLUSIONS.json"
PRIOR_SURVIVORS = HERE / "after_incidence_survivors.txt"
EXPECTED_BY_MAXIMUM = {12: 10, 13: 6, 14: 69, 15: 43}


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


def parse_profile(raw_line):
    values = list(map(int, raw_line.split()))
    require(len(values) >= 4, "Malformed source line")
    s, m, energy, *weights = values
    require(len(weights) == s and 13 <= s <= 17 and 12 <= m <= 18, "Bad profile dimensions")
    require(weights == sorted(weights, reverse=True) and max(weights) == m, "Bad profile sorting or maximum")
    require(all(2 <= w <= m for w in weights) and sum(weights) <= 93, "Bad active-fibre weight domain")
    return s, m, energy, tuple(weights)


def eligible(profile):
    s, maximum, _, weights = profile
    return s == 13 and maximum <= 15 and sum(w >= 4 for w in weights) < 10


def read_inputs():
    original = (ROOT / SOURCE).read_bytes()
    require(digest(original) == SOURCE_SHA256, "Changed original Round7 frontier")
    for path, expected in {**PRIOR_PINS, **PROOF_PINS}.items():
        require(digest((ROOT / path).read_bytes()) == expected, "Changed pinned input: " + path)
    raw_lines = original.splitlines(keepends=True)
    require(len(raw_lines) == 183476 and all(raw.endswith(b"\n") for raw in raw_lines), "Original line inventory differs")
    profiles = [parse_profile(raw) for raw in raw_lines]
    require(len({p[3] for p in profiles}) == len(profiles), "Duplicated original weight profile")
    previous = json.loads(PRIOR_CERTIFICATE.read_text())
    previous_rows = previous["certificates"]
    previous_lines = {row["source_line"] for row in previous_rows}
    expected_previous = {i for i, p in enumerate(profiles, 1) if eligible(p) and p[1] <= 13}
    require(len(previous_rows) == len(previous_lines) == 16 and previous_lines == expected_previous,
            "Prior16 source-line set differs")
    for row in previous_rows:
        i = row["source_line"]
        require(type(i) is int and 1 <= i <= len(profiles), "Invalid prior source line")
        s, m, energy, weights = profiles[i-1]
        require(row["source_line_sha256"] == digest(raw_lines[i-1]) and
                row["source_line_ascii"] == raw_lines[i-1].decode("ascii") and
                row["weights"] == list(weights) and row["support_size"] == s and
                row["maximum"] == m and row["inherited_energy_metadata_not_used"] == energy,
                "Prior certificate is not bound to its original source line")
    intermediate_lines = [raw for i, raw in enumerate(raw_lines, 1) if i not in previous_lines]
    require(len(intermediate_lines) == 183460 and b"".join(intermediate_lines) == PRIOR_SURVIVORS.read_bytes(),
            "Frozen intermediate frontier is not the exact original-minus16 sequence")
    return raw_lines, profiles, previous_lines, intermediate_lines


def make_row(number, raw_line, profile):
    require(eligible(profile), "Profile is outside the analytic corollary")
    s, maximum, energy, weights = profile
    h = sum(w >= 4 for w in weights)
    require(h == 9, "This inherited certificate family should contain only nine-heavy profiles")
    n2, n3 = weights.count(2), weights.count(3)
    P = maximum // 2
    r = (16+P-1)//P
    required, available = 3*r, n2+2*n3
    require(P in (6, 7) and r == 3 and n2+n3 == 4 and required > available,
            "No strict exact incidence contradiction")
    return {
        "source_line": number,
        "source_line_sha256": digest(raw_line),
        "source_line_ascii": raw_line.decode("ascii"),
        "support_size": s,
        "maximum": maximum,
        "inherited_energy_metadata_not_used": energy,
        "weights": list(weights),
        "total_weight": sum(weights),
        "heavy_positions_zero_based": [i for i, w in enumerate(weights) if w >= 4],
        "heavy_count": h,
        "light_weight2_count": n2,
        "light_weight3_count": n3,
        "maximum_pair_count": P,
        "minimum_active_light_incidences_per_missing_direction": r,
        "heavy_difference_upper_bound": 28,
        "missing_direction_lower_bound": 3,
        "required_light_incidences_lower_bound": required,
        "available_light_incidences_upper_bound": available,
        "strict_gap": required-available,
        "already_in_prior_sixteen_stage": maximum <= 13,
        "reason": "Nine heavy fibres leave at least three missing directions; the required light incidences exceed L2+2L3.",
    }


def check_row(row, raw_lines, profiles):
    require(isinstance(row, dict), "Certificate row is not an object")
    i = row.get("source_line")
    require(type(i) is int and 1 <= i <= len(profiles), "Invalid original source-line number")
    expected = make_row(i, raw_lines[i-1], profiles[i-1])
    require(json_bytes(row) == json_bytes(expected), "Certificate row differs from exact source-line derivation")
    return i


def elementary_corollary_controls():
    rows = []
    for maximum in range(2, 16):
        P = maximum//2
        r = (16+P-1)//P
        require(r >= 3 and P*(r-1) < 16 <= P*r, "Integer ceiling for active lights differs")
        gaps = [r*(31-h*(h-1)//2)-3*(13-h) for h in range(8)]
        require(all(gap > 0 for gap in gaps), "Small-heavy incidence exclusion failed")
        eight_gap = 6*r-15
        nine_gap = 3*r-8
        require(eight_gap > 0 and nine_gap > 0, "Eight/nine-heavy incidence exclusion failed")
        require(6//r <= 2 and 2*P < 16, "Further heavy-difference consequences failed")
        rows.append({"maximum": maximum, "P": P, "r": r,
                     "strict_gaps_h0_through_h7": gaps,
                     "strict_gap_h8": eight_gap, "strict_gap_h9": nine_gap})
    return rows


def build_expected(raw_lines, profiles, prior_lines, intermediate_lines):
    rows = [make_row(i, raw, profile)
            for i, (raw, profile) in enumerate(zip(raw_lines, profiles), 1) if eligible(profile)]
    excluded = {row["source_line"] for row in rows}
    require(len(rows) == len(excluded) == 128, "Cumulative exclusion count differs")
    require(Counter(row["maximum"] for row in rows) == EXPECTED_BY_MAXIMUM, "Per-maximum exclusion counts differ")
    require(Counter((r["light_weight2_count"], r["light_weight3_count"]) for r in rows) == {(0, 4): 127, (1, 3): 1},
            "Exact light-weight distribution differs")
    require(prior_lines < excluded and len(excluded-prior_lines) == 112, "Prior16/new112 partition differs")
    kept = [raw for i, raw in enumerate(raw_lines, 1) if i not in excluded]
    survivor_bytes = b"".join(kept)
    staged_kept = [raw for raw in intermediate_lines if not eligible(parse_profile(raw))]
    require(len(kept) == len(staged_kept) == 183348 and b"".join(staged_kept) == survivor_bytes,
            "Direct and staged survivor regeneration disagree")
    before = Counter((p[0], p[1]) for p in profiles)
    removed = Counter((r["support_size"], r["maximum"]) for r in rows)
    old_removed = Counter((profiles[i-1][0], profiles[i-1][1]) for i in prior_lines)
    after = before-removed
    support_table = {str(s): {
        "original": sum(n for (cell_s, _), n in before.items() if cell_s == s),
        "previously_excluded": sum(n for (cell_s, _), n in old_removed.items() if cell_s == s),
        "newly_excluded": sum(n for (cell_s, _), n in (removed-old_removed).items() if cell_s == s),
        "cumulative_excluded": sum(n for (cell_s, _), n in removed.items() if cell_s == s),
        "remaining": sum(n for (cell_s, _), n in after.items() if cell_s == s)}
        for s in sorted({p[0] for p in profiles})}
    require({int(s): row["remaining"] for s, row in support_table.items()} ==
            {13: 85212, 14: 74373, 15: 19514, 16: 3853, 17: 396}, "Final support accounting differs")
    maximum_table = {str(m): {
        "original": sum(n for (_, cell_m), n in before.items() if cell_m == m),
        "previously_excluded": sum(n for (_, cell_m), n in old_removed.items() if cell_m == m),
        "newly_excluded": sum(n for (_, cell_m), n in (removed-old_removed).items() if cell_m == m),
        "cumulative_excluded": sum(n for (_, cell_m), n in removed.items() if cell_m == m),
        "remaining": sum(n for (_, cell_m), n in after.items() if cell_m == m)}
        for m in sorted({p[1] for p in profiles})}
    payload = {
        "format": "kakeya-round8-extended-incidence-whole-profile-exclusions-v1",
        "original_input_file": SOURCE,
        "original_input_sha256": SOURCE_SHA256,
        "original_profiles": 183476,
        "prior_stage_pins": PRIOR_PINS,
        "analytic_proof_pins": PROOF_PINS,
        "producer_verifier": str(Path(__file__).resolve().relative_to(ROOT)),
        "producer_verifier_sha256": digest(Path(__file__).read_bytes()),
        "previously_excluded_profiles": 16,
        "newly_excluded_profiles": 112,
        "cumulative_excluded_profiles": 128,
        "remaining_profiles": 183348,
        "survivor_file": str(SURVIVORS.relative_to(ROOT)),
        "survivor_sha256": digest(survivor_bytes),
        "scope": "All support placements and fibre shapes of these128 profiles, in both Z/4Z and F2[epsilon]/(epsilon^2). No extra SAT role is credited.",
        "mathematical_dependencies": [
            "The analytic support13 maximum<=15 corollary, including the general missing-direction incidence lemma.",
            "The analytic eight/nine-point difference bounds in F2^5; the explicit128 rows use only the nine-point bound.",
            "No fibre-spectrum census, quotient-sumset table, SAT encoding or solver is a premise of these new exclusions.",
            "The older16 artifacts are bound for exact ledger continuity; their counts are included, not added again."
        ],
        "by_support": support_table,
        "by_maximum": maximum_table,
        "by_support_and_maximum": [
            {"support_size": s, "maximum": m, "original": before[s, m],
             "previously_excluded": old_removed[s, m], "newly_excluded": removed[s, m]-old_removed[s, m],
             "cumulative_excluded": removed[s, m], "remaining": after[s, m]}
            for s, m in sorted(before)],
        "certificates": rows,
    }
    return payload, survivor_bytes


def negative_controls(rows, raw_lines, profiles):
    controls = []
    for label, field, value in [
        ("invalid_source_line", "source_line", 0),
        ("uncertified_source_line", "source_line", 1),
        ("wrong_source_hash", "source_line_sha256", "0"*64),
        ("wrong_maximum", "maximum", 16),
        ("wrong_heavy_count", "heavy_count", 10),
        ("wrong_pair_ceiling", "maximum_pair_count", 8),
        ("wrong_incidence_ceiling", "minimum_active_light_incidences_per_missing_direction", 2),
        ("wrong_available_incidence", "available_light_incidences_upper_bound", 9),
        ("double_counted_prior_stage", "already_in_prior_sixteen_stage", True),
        ("boolean_in_integer_field", "strict_gap", True),
    ]:
        row = deepcopy(rows[0]); row[field] = value
        try:
            check_row(row, raw_lines, profiles)
        except (ValueError, KeyError, TypeError):
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted certificate accepted: " + label)
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing deterministic extension artifacts")
    args = parser.parse_args()
    started = time.monotonic()
    atomic_write(RECEIPT, json_bytes({"status": "RUNNING", "write_mode": args.write}))
    try:
        raw_lines, profiles, prior_lines, intermediate_lines = read_inputs()
        payload, survivor_bytes = build_expected(raw_lines, profiles, prior_lines, intermediate_lines)
        payload_bytes = json_bytes(payload)
        if args.write:
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                require(not path.exists() or path.read_bytes() == data,
                        "Refusing to overwrite a different semantic artifact: " + path.name)
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                if not path.exists():
                    atomic_write(path, data)
        require(CERTIFICATE.read_bytes() == payload_bytes, "Stored extension certificate differs from regeneration")
        require(SURVIVORS.read_bytes() == survivor_bytes, "Stored final frontier differs in bytes or order")
        stored = json.loads(CERTIFICATE.read_text())
        checked_lines = [check_row(row, raw_lines, profiles) for row in stored["certificates"]]
        require(len(set(checked_lines)) == len(checked_lines) == 128, "Duplicate or missing exclusion row")
        controls = negative_controls(stored["certificates"], raw_lines, profiles)
        theorem_checks = elementary_corollary_controls()
        for path, expected in PRIOR_PINS.items():
            require(digest((ROOT / path).read_bytes()) == expected, "Prior16 artifact changed during replay")
        receipt = {
            "status": "PASS_EXTENDED_INCIDENCE_PROFILE_REPLAY",
            "original_profiles": 183476,
            "intermediate_profiles": 183460,
            "previously_excluded_profiles": 16,
            "newly_excluded_profiles": 112,
            "cumulative_excluded_profiles": 128,
            "remaining_profiles": 183348,
            "by_support": payload["by_support"],
            "by_maximum": payload["by_maximum"],
            "by_support_and_maximum": payload["by_support_and_maximum"],
            "coverage": {
                "every_original_source_line_accounted_for": True,
                "excluded_original_source_lines": checked_lines,
                "previously_excluded_original_source_lines": sorted(prior_lines),
                "newly_excluded_original_source_lines": sorted(set(checked_lines)-prior_lines),
                "every_retained_original_line_preserved_byte_identically_and_in_order": True,
                "direct_and_intermediate_frontier_regeneration_identical": True,
                "prior_sixteen_semantic_artifacts_unchanged": True,
                "inherited_energy_metadata_used_in_exclusion": False,
            },
            "original_input_file": SOURCE,
            "original_input_sha256": SOURCE_SHA256,
            "prior_stage_pins": PRIOR_PINS,
            "analytic_proof_pins": PROOF_PINS,
            "certificate_file": str(CERTIFICATE.relative_to(ROOT)),
            "certificate_sha256": digest(CERTIFICATE.read_bytes()),
            "survivor_file": str(SURVIVORS.relative_to(ROOT)),
            "survivor_sha256": digest(survivor_bytes),
            "verifier_sha256": digest(Path(__file__).read_bytes()),
            "elementary_corollary_integer_controls": theorem_checks,
            "negative_controls": controls,
            "scope": payload["scope"],
            "dependency_boundary": "Pinned hand proofs supply the geometry. This Python replay verifies exact integers and both complete byte-preserving ledger partitions; it is not a proof-assistant formalization.",
            "elapsed_seconds": round(time.monotonic()-started, 6),
        }
        atomic_write(RECEIPT, json_bytes(receipt))
        print(json.dumps({key: receipt[key] for key in (
            "status", "original_profiles", "previously_excluded_profiles", "newly_excluded_profiles",
            "cumulative_excluded_profiles", "remaining_profiles", "by_support")}, indent=2))
    except BaseException as error:
        atomic_write(RECEIPT, json_bytes({"status": "FAIL", "exception_type": type(error).__name__,
                                        "message": str(error), "elapsed_seconds": round(time.monotonic()-started, 6)}))
        raise


if __name__ == "__main__":
    main()
