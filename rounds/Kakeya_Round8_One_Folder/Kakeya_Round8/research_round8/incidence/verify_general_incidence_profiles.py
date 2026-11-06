#!/usr/bin/env python3
"""Exhaustively replay the weighted-light incidence screen on the R7 ledger.

The cumulative175 certificates include the frozen128 stage and47 additional
profiles. The frozen previous verifier is used only to bind its immutable
input/certificate/frontier; this module computes the general integer screen.
No previous receipt is rewritten and no SAT solver is run.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse
import hashlib
import importlib.util
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
    "research_round8/incidence/verify_extended_incidence_profiles.py":
        "6da613dc592a2b0f55ff08e1d695a66551d254e82f579f9056c4b52ae64fa1f0",
    "research_round8/incidence/EXTENDED_INCIDENCE_PROFILE_EXCLUSIONS.json":
        "51b60f9083281dace3cf6a1aba4099f80caef98c9eaa8548b3d5f2b5ac870d87",
    "research_round8/incidence/after_extended_incidence_survivors.txt":
        "b15dc1e11b2c8f661cc30745e5a40a7239816c8166993f5324209aedeadb5a05",
}
PROOF_PINS = {
    "research_round8/incidence/GENERAL_WEIGHTED_LIGHT_PROFILE_CERTIFICATES.md":
        "2caac5db0f695b6faef6da597925f048fd23dc9f5e39b34641c0df491cfc9359",
    "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md":
        "4d52fcdb7b60b09cc52934ab3fab575d07b4320789879de664592c3a129c9034",
    "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md":
        "cb5671d36c1b857023aee9481491881d56cf9aef27734b104208b6fbbb6b5ba8",
}
CERTIFICATE = HERE / "GENERAL_INCIDENCE_PROFILE_EXCLUSIONS.json"
SURVIVORS = HERE / "after_general_incidence_survivors.txt"
RECEIPT = HERE / "GENERAL_INCIDENCE_PROFILE_REPLAY.json"
EXPECTED_CELLS = {(13, 12): 10, (13, 13): 6, (13, 14): 69, (13, 15): 43,
                  (14, 12): 2, (14, 13): 1, (14, 14): 23, (14, 15): 10,
                  (15, 14): 7, (15, 15): 2, (16, 14): 2}


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
    for path, expected in {**PRIOR_PINS, **PROOF_PINS}.items():
        require(digest((ROOT / path).read_bytes()) == expected, "Changed pinned input: " + path)
    require(digest((ROOT / SOURCE).read_bytes()) == SOURCE_SHA256, "Changed original Round7 frontier")
    # Import only after checking the previous verifier's exact source hash.
    path = HERE / "verify_extended_incidence_profiles.py"
    spec = importlib.util.spec_from_file_location("frozen_round8_incidence128", path)
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    raw_lines, profiles, first16, intermediate16 = previous.read_inputs()
    prior_payload, intermediate128_bytes = previous.build_expected(raw_lines, profiles, first16, intermediate16)
    require(previous.CERTIFICATE.read_bytes() == json_bytes(prior_payload), "Frozen128 certificate does not reproduce")
    require(previous.SURVIVORS.read_bytes() == intermediate128_bytes, "Frozen128 frontier does not reproduce")
    prior128 = {previous.check_row(row, raw_lines, profiles) for row in prior_payload["certificates"]}
    require(len(prior128) == 128 and first16 < prior128, "Earlier stage nesting differs")
    return raw_lines, profiles, first16, prior128, intermediate128_bytes.splitlines(keepends=True), previous.PROOF_PINS


def score(profile):
    s, maximum, _, weights = profile
    h = sum(w >= 4 for w in weights)
    n2, n3 = weights.count(2), weights.count(3)
    require(h+n2+n3 == s, "Profile contains a non-active fibre weight")
    P = maximum//2
    r = (16+P-1)//P
    if h <= 7:
        direction_bound = min(31, h*(h-1)//2)
        available = n2+3*n3
        method = "universal_light_incidence_pair_bound"
    elif h == 8:
        direction_bound = 25
        available = n2+3*n3
        method = "universal_light_incidence_eight_point_bound"
    elif h == 9:
        direction_bound = 28
        available = n2+2*n3
        method = "plane_free_missing_set_nine_point_bound"
    else:
        direction_bound = 31
        available = n2+2*n3
        method = "plane_free_missing_set_trivial_direction_bound"
    missing = 31-direction_bound
    required = r*missing
    return {"heavy_count": h, "light_weight2_count": n2, "light_weight3_count": n3,
            "maximum_pair_count": P, "minimum_active_light_incidences_per_missing_direction": r,
            "heavy_difference_upper_bound": direction_bound, "missing_direction_lower_bound": missing,
            "required_light_incidences_lower_bound": required,
            "available_light_incidences_upper_bound": available,
            "strict_gap": required-available, "method": method}


def make_row(number, raw_line, profile, first16, prior128):
    bounds = score(profile)
    require(bounds["strict_gap"] > 0, "Profile is not excluded by the displayed integer criterion")
    require(bounds["heavy_count"] == 9, "Unexpected additional family needs separate review")
    s, maximum, energy, weights = profile
    return {"source_line": number, "source_line_sha256": digest(raw_line),
            "source_line_ascii": raw_line.decode("ascii"), "support_size": s, "maximum": maximum,
            "inherited_energy_metadata_not_used": energy, "weights": list(weights),
            "total_weight": sum(weights),
            "heavy_positions_zero_based": [i for i, w in enumerate(weights) if w >= 4],
            **bounds,
            "already_in_first_sixteen_stage": number in first16,
            "already_in_previous128_stage": number in prior128}


def check_row(row, raw_lines, profiles, first16, prior128):
    require(isinstance(row, dict), "Certificate row must be an object")
    number = row.get("source_line")
    require(type(number) is int and 1 <= number <= len(profiles), "Invalid original source line")
    expected = make_row(number, raw_lines[number-1], profiles[number-1], first16, prior128)
    require(json_bytes(row) == json_bytes(expected), "Certificate differs from exact original-source derivation")
    return number


def exhaustive_scan(profiles):
    checked, excluded = Counter(), Counter()
    all_scores = []
    for profile in profiles:
        bounds = score(profile)
        all_scores.append(bounds)
        checked[bounds["heavy_count"]] += 1
        if bounds["strict_gap"] > 0:
            excluded[bounds["heavy_count"]] += 1
    require(sum(checked.values()) == 183476 and checked[9] == 2187, "Full scan inventory differs")
    require(excluded == {9: 175}, "The exhaustive screen found an unreviewed exclusion family")
    require(sum(n for h, n in checked.items() if h <= 8) == 0, "Unexpected lower-heavy inherited profile")
    report = {"source_profiles_scanned": len(profiles),
              "by_heavy_count": {str(h): {"checked": checked[h], "excluded": excluded[h],
                                         "passes_this_screen": checked[h]-excluded[h]}
                                 for h in sorted(checked)},
              "nine_heavy_profiles_checked": checked[9], "nine_heavy_profiles_excluded": excluded[9],
              "nine_heavy_profiles_passing_this_screen": checked[9]-excluded[9],
              "universal_h0_through_h8_profiles_checked": 0,
              "universal_h0_through_h8_additional_exclusions": 0,
              "interpretation": "Exhaustive only for the displayed weight-only incidence bounds on this pinned ledger; passing is not an existence certificate."}
    return all_scores, report


def build_expected(raw_lines, profiles, first16, prior128, intermediate128):
    scores, scan = exhaustive_scan(profiles)
    rows = [make_row(i, raw, profile, first16, prior128)
            for i, (raw, profile, bounds) in enumerate(zip(raw_lines, profiles, scores), 1)
            if bounds["strict_gap"] > 0]
    excluded = {row["source_line"] for row in rows}
    cells = Counter((r["support_size"], r["maximum"]) for r in rows)
    require(len(rows) == len(excluded) == 175 and cells == EXPECTED_CELLS, "Cumulative exclusion inventory differs")
    require(prior128 < excluded and len(excluded-prior128) == 47, "Prior128/new47 partition differs")
    require(Counter(r["strict_gap"] for r in rows) == {1: 174, 2: 1}, "Strict-gap distribution differs")
    survivors = b"".join(raw for i, raw in enumerate(raw_lines, 1) if i not in excluded)
    # Reconstruct each prior128 survivor's original profile through its bytes.
    profile_by_raw = dict(zip(raw_lines, profiles))
    staged = b"".join(raw for raw in intermediate128 if score(profile_by_raw[raw])["strict_gap"] <= 0)
    require(len(survivors.splitlines()) == 183301 and staged == survivors,
            "Direct-minus175 and staged-minus47 byte sequences differ")
    before = Counter((p[0], p[1]) for p in profiles)
    previous = Counter((profiles[i-1][0], profiles[i-1][1]) for i in prior128)
    after = before-cells
    def aggregated(index):
        values = sorted({key[index] for key in before})
        return {str(value): {
            "original": sum(n for key, n in before.items() if key[index] == value),
            "previously_excluded": sum(n for key, n in previous.items() if key[index] == value),
            "newly_excluded": sum(n for key, n in (cells-previous).items() if key[index] == value),
            "cumulative_excluded": sum(n for key, n in cells.items() if key[index] == value),
            "remaining": sum(n for key, n in after.items() if key[index] == value)} for value in values}
    support_table = aggregated(0)
    require({int(s): row["remaining"] for s, row in support_table.items()} ==
            {13: 85212, 14: 74337, 15: 19505, 16: 3851, 17: 396}, "Remaining support counts differ")
    payload = {
        "format": "kakeya-round8-general-weighted-light-profile-exclusions-v1",
        "original_input_file": SOURCE, "original_input_sha256": SOURCE_SHA256,
        "original_profiles": 183476, "intermediate_profiles": 183348,
        "previously_excluded_profiles": 128, "newly_excluded_profiles": 47,
        "cumulative_excluded_profiles": 175, "remaining_profiles": 183301,
        "first_sixteen_profiles_included_without_double_counting": 16,
        "prior_stage_pins": PRIOR_PINS, "analytic_proof_pins": PROOF_PINS,
        "producer_verifier": str(Path(__file__).resolve().relative_to(ROOT)),
        "producer_verifier_sha256": digest(Path(__file__).read_bytes()),
        "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(survivors),
        "scope": "Every placement and fibre shape of these175 whole profiles, in both rings. No support-orbit SAT credit is added.",
        "mathematical_dependencies": [
            "For h>=9, the missing heavy-direction set is plane-free and r*|M|<=L2+2*L3.",
            "For h=9, the analytic difference bound gives |M|>=3.",
            "The h<=8 universal screen is evaluated but has no applicable inherited profiles.",
            "No fibre-spectrum census, quotient-sumset table, SAT encoding or solver is a premise of these175 exclusions.",
            "The prior128 are included within175, and the first16 are included within128; neither stage is added again."
        ],
        "exhaustive_scan": scan,
        "by_support": support_table, "by_maximum": aggregated(1),
        "by_support_and_maximum": [{"support_size": s, "maximum": m, "original": before[s, m],
            "previously_excluded": previous[s, m], "newly_excluded": cells[s, m]-previous[s, m],
            "cumulative_excluded": cells[s, m], "remaining": after[s, m]} for s, m in sorted(before)],
        "certificates": rows,
    }
    return payload, survivors


def negative_controls(rows, raw_lines, profiles, first16, prior128):
    new_row = next(row for row in rows if not row["already_in_previous128_stage"])
    controls = []
    for label, field, value in [
        ("invalid_source_line", "source_line", 0),
        ("uncertified_source_line", "source_line", 1),
        ("wrong_source_hash", "source_line_sha256", "0"*64),
        ("wrong_support_size", "support_size", 13),
        ("wrong_heavy_count", "heavy_count", 10),
        ("wrong_light_weight2_count", "light_weight2_count", 0),
        ("wrong_incidence_requirement", "required_light_incidences_lower_bound", 8),
        ("wrong_available_incidence", "available_light_incidences_upper_bound", 9),
        ("double_counted_previous_stage", "already_in_previous128_stage", True),
        ("boolean_in_integer_field", "strict_gap", True),
    ]:
        row = deepcopy(new_row); row[field] = value
        try:
            check_row(row, raw_lines, profiles, first16, prior128)
        except (ValueError, KeyError, TypeError):
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted certificate accepted: " + label)
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing deterministic general-incidence artifacts")
    args = parser.parse_args()
    started = time.monotonic()
    atomic_write(RECEIPT, json_bytes({"status": "RUNNING", "write_mode": args.write}))
    try:
        raw_lines, profiles, first16, prior128, intermediate128, transitive_proofs = read_inputs()
        payload, survivor_bytes = build_expected(raw_lines, profiles, first16, prior128, intermediate128)
        payload_bytes = json_bytes(payload)
        if args.write:
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                require(not path.exists() or path.read_bytes() == data,
                        "Refusing to overwrite a different semantic artifact: " + path.name)
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                if not path.exists():
                    atomic_write(path, data)
        require(CERTIFICATE.read_bytes() == payload_bytes, "Stored general certificate differs from exact regeneration")
        require(SURVIVORS.read_bytes() == survivor_bytes, "Stored general frontier differs in bytes or order")
        stored = json.loads(CERTIFICATE.read_text())
        checked = [check_row(row, raw_lines, profiles, first16, prior128) for row in stored["certificates"]]
        require(len(set(checked)) == len(checked) == 175, "Duplicated or missing certificate row")
        controls = negative_controls(stored["certificates"], raw_lines, profiles, first16, prior128)
        for path, expected in PRIOR_PINS.items():
            require(digest((ROOT / path).read_bytes()) == expected, "Earlier artifact changed during replay")
        receipt = {key: payload[key] for key in (
            "original_input_file", "original_input_sha256", "original_profiles", "intermediate_profiles",
            "previously_excluded_profiles", "newly_excluded_profiles", "cumulative_excluded_profiles", "remaining_profiles",
            "by_support", "by_maximum", "by_support_and_maximum", "prior_stage_pins", "analytic_proof_pins",
            "exhaustive_scan", "scope")}
        receipt.update({
            "status": "PASS_GENERAL_INCIDENCE_PROFILE_REPLAY",
            "transitive_prior_analytic_pins": transitive_proofs,
            "coverage": {
                "every_original_profile_scored": True,
                "excluded_original_source_lines": checked,
                "previously_excluded_original_source_lines": sorted(prior128),
                "newly_excluded_original_source_lines": sorted(set(checked)-prior128),
                "every_retained_line_preserved_byte_identically_and_in_order": True,
                "direct_minus175_and_prior128_minus47_regeneration_identical": True,
                "both_previous_stages_semantically_unchanged": True,
                "energy_metadata_used_in_exclusion": False,
            },
            "certificate_file": str(CERTIFICATE.relative_to(ROOT)), "certificate_sha256": digest(CERTIFICATE.read_bytes()),
            "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(survivor_bytes),
            "verifier_sha256": digest(Path(__file__).read_bytes()),
            "negative_controls": controls,
            "dependency_boundary": "Pinned hand proofs supply the geometry. This exact integer/data replay is not proof-assistant formalized; it counts whole profiles separately from SAT roles.",
            "elapsed_seconds": round(time.monotonic()-started, 6),
        })
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
