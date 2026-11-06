#!/usr/bin/env python3
"""Replay cumulative matching-threshold exclusions on the sealed R7 frontier.

This stage includes all175 earlier weighted-incidence exclusions and570 new
profiles. Every threshold is bracketed by its exact sorted heavy-capacity
prefix sums. Earlier source/certificate/survivor artifacts remain immutable.
No SAT solver, energy bound, spectrum census or sumset table is used.
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
    "research_round8/incidence/verify_general_incidence_profiles.py":
        "f626689310bbaaeeef5891532a0719bc9c9fde02f40e023d176c72fdbd502adc",
    "research_round8/incidence/GENERAL_INCIDENCE_PROFILE_EXCLUSIONS.json":
        "a188bc1519b8cd6d5a3d206fc215ba9bbbee6ccace9ae72f5732e87b0d414d9f",
    "research_round8/incidence/after_general_incidence_survivors.txt":
        "70bd3c18106c5ea47b7f37dfca52da6121a2bd9440e6c909c5834db06652e27f",
}
PROOF_PINS = {
    "research_round8/geometry/MATCHING_THRESHOLD_LEMMA.md":
        "05967dd3a9756b29e9b473b26673fa4f2d11c6272dccac47d94c55a2b1552750",
    "research_round8/incidence/MISSING_DIRECTION_INCIDENCE.md":
        "4d52fcdb7b60b09cc52934ab3fab575d07b4320789879de664592c3a129c9034",
    "research_round7/dense_encoder/NINE_POINT_DIFFERENCE_ANALYTIC_PROOF.md":
        "cb5671d36c1b857023aee9481491881d56cf9aef27734b104208b6fbbb6b5ba8",
}
CERTIFICATE = HERE / "MATCHING_INCIDENCE_PROFILE_EXCLUSIONS.json"
SURVIVORS = HERE / "after_matching_incidence_survivors.txt"
RECEIPT = HERE / "MATCHING_INCIDENCE_PROFILE_REPLAY.json"
EXPECTED_REMOVED_SUPPORT = {13: 392, 14: 220, 15: 88, 16: 38, 17: 7}
EXPECTED_REMOVED_MAXIMUM = {12: 58, 13: 35, 14: 126, 15: 76, 16: 250, 17: 94, 18: 106}
EXPECTED_SURVIVOR_SHA256 = "1996a016795c5494c29a07558fb1204306cfb081de5257d7668d2c9e377d2cfd"


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
    spec = importlib.util.spec_from_file_location("frozen_round8_incidence175", HERE / "verify_general_incidence_profiles.py")
    previous = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(previous)
    raw, profiles, first16, prior128, intermediate128, older_proof_pins = previous.read_inputs()
    prior_payload, prior_frontier_bytes = previous.build_expected(raw, profiles, first16, prior128, intermediate128)
    require(previous.CERTIFICATE.read_bytes() == json_bytes(prior_payload), "Frozen175 certificate does not reproduce")
    require(previous.SURVIVORS.read_bytes() == prior_frontier_bytes, "Frozen175 frontier does not reproduce")
    prior175 = {previous.check_row(row, raw, profiles, first16, prior128) for row in prior_payload["certificates"]}
    require(len(prior175) == 175 and first16 < prior128 < prior175, "Prior stage nesting differs")
    return raw, profiles, first16, prior128, prior175, prior_frontier_bytes.splitlines(keepends=True), {
        **older_proof_pins, **previous.PROOF_PINS}


def matching_score(profile):
    s, maximum, _, weights = profile
    heavy_weights = sorted((w for w in weights if w >= 4), reverse=True)
    if len(heavy_weights) != 9:
        return None
    n2, n3 = weights.count(2), weights.count(3)
    light_count = n2+n3
    require(light_count == s-9 and 0 <= light_count <= 8, "Nine-heavy matching lemma is outside its light-count scope")
    ceilings = sorted((w//2 for w in heavy_weights), reverse=True)
    require(len(ceilings) == 9 and all(2 <= q <= 9 for q in ceilings), "Invalid heavy pair ceiling")
    prefix = [0]
    for q in ceilings:
        prefix.append(prefix[-1]+q)
    rho = next(k for k in range(1, 10) if prefix[k] >= 16)
    require(1 <= rho <= 8 and prefix[rho-1] < 16 <= prefix[rho], "Matching threshold is not minimal")
    P = maximum//2
    uniform_threshold = (16+P-1)//P
    require(rho >= uniform_threshold, "Matching threshold is weaker than the uniform pair ceiling")
    available = n2+2*n3
    return {"heavy_count": 9, "heavy_weights_descending": heavy_weights,
            "heavy_pair_ceilings_descending": ceilings, "heavy_ceiling_prefix_sums": prefix,
            "light_count": light_count, "light_weight2_count": n2, "light_weight3_count": n3,
            "uniform_maximum_pair_count": P, "uniform_incidence_threshold": uniform_threshold,
            "matching_incidence_threshold_rho": rho,
            "prefix_capacity_with_rho_minus_one_lights": prefix[rho-1],
            "prefix_capacity_with_rho_lights": prefix[rho],
            "coverage_capacity_required_per_direction": 16,
            "heavy_difference_upper_bound": 28, "missing_direction_lower_bound": 3,
            "required_light_incidences_lower_bound": 3*rho,
            "available_light_incidences_upper_bound": available,
            "strict_gap": 3*rho-available}


def make_row(number, raw, profile, first16, prior128, prior175):
    bounds = matching_score(profile)
    require(bounds is not None and bounds["strict_gap"] > 0, "Profile has no strict matching-incidence contradiction")
    s, maximum, energy, weights = profile
    return {"source_line": number, "source_line_sha256": digest(raw), "source_line_ascii": raw.decode("ascii"),
            "support_size": s, "maximum": maximum, "inherited_energy_metadata_not_used": energy,
            "weights": list(weights), "total_weight": sum(weights),
            "heavy_positions_zero_based": [i for i, w in enumerate(weights) if w >= 4],
            **bounds,
            "already_in_first_sixteen_stage": number in first16,
            "already_in_previous128_stage": number in prior128,
            "already_in_previous175_stage": number in prior175}


def check_row(row, raw, profiles, first16, prior128, prior175):
    require(isinstance(row, dict), "Certificate row must be an object")
    number = row.get("source_line")
    require(type(number) is int and 1 <= number <= len(profiles), "Invalid original source-line number")
    expected = make_row(number, raw[number-1], profiles[number-1], first16, prior128, prior175)
    require(json_bytes(row) == json_bytes(expected), "Certificate row differs from exact source-line and prefix derivation")
    return number


def exhaustive_scan(profiles):
    scores = []
    heavy_counts, all_rho, removed_rho, gaps = Counter(), Counter(), Counter(), Counter()
    for profile in profiles:
        heavy_counts[sum(w >= 4 for w in profile[3])] += 1
        row = matching_score(profile)
        scores.append(row)
        if row is not None:
            rho = row["matching_incidence_threshold_rho"]
            all_rho[rho] += 1
            if row["strict_gap"] > 0:
                removed_rho[rho] += 1
                gaps[row["strict_gap"]] += 1
    require(len(profiles) == 183476 and heavy_counts[9] == 2187, "Original scan inventory differs")
    require(all_rho == {2: 91, 3: 1906, 4: 190}, "Nine-heavy matching-threshold distribution differs")
    require(removed_rho == {3: 625, 4: 120} and gaps == {1: 609, 2: 136}, "Matching exclusion distribution differs")
    return scores, {"all_original_profiles_scanned": len(profiles),
                    "source_profiles_by_heavy_count": {str(h): n for h, n in sorted(heavy_counts.items())},
                    "nine_heavy_profiles_checked": 2187, "nine_heavy_profiles_excluded": 745,
                    "nine_heavy_profiles_passing_this_screen": 1442,
                    "all_nine_heavy_profiles_by_rho": {str(k): n for k, n in sorted(all_rho.items())},
                    "excluded_profiles_by_rho": {str(k): n for k, n in sorted(removed_rho.items())},
                    "excluded_profiles_by_strict_gap": {str(k): n for k, n in sorted(gaps.items())},
                    "scope": "Every original profile is inspected; this screen acts only when h=9 and L<=8. Passing does not establish realizability."}


def build_expected(raw, profiles, first16, prior128, prior175, prior_survivors):
    scores, scan = exhaustive_scan(profiles)
    rows = [make_row(i, line, profile, first16, prior128, prior175)
            for i, (line, profile, bounds) in enumerate(zip(raw, profiles, scores), 1)
            if bounds is not None and bounds["strict_gap"] > 0]
    excluded = {row["source_line"] for row in rows}
    require(len(rows) == len(excluded) == 745 and prior175 < excluded and len(excluded-prior175) == 570,
            "Prior175/new570 cumulative exclusion partition differs")
    require(Counter(r["support_size"] for r in rows) == EXPECTED_REMOVED_SUPPORT and
            Counter(r["maximum"] for r in rows) == EXPECTED_REMOVED_MAXIMUM, "Exclusion totals differ")
    final_bytes = b"".join(line for i, line in enumerate(raw, 1) if i not in excluded)
    by_raw = dict(zip(raw, profiles))
    staged = []
    for line in prior_survivors:
        bounds = matching_score(by_raw[line])
        if bounds is None or bounds["strict_gap"] <= 0:
            staged.append(line)
    require(len(staged) == 182731 and b"".join(staged) == final_bytes, "Direct745 and staged570 regeneration differ")
    require(digest(final_bytes) == EXPECTED_SURVIVOR_SHA256, "Independently predicted survivor hash differs")
    before = Counter((p[0], p[1]) for p in profiles)
    removed = Counter((r["support_size"], r["maximum"]) for r in rows)
    old = Counter((profiles[i-1][0], profiles[i-1][1]) for i in prior175)
    after = before-removed
    def aggregate(index):
        return {str(value): {"original": sum(n for cell, n in before.items() if cell[index] == value),
                            "previously_excluded": sum(n for cell, n in old.items() if cell[index] == value),
                            "newly_excluded": sum(n for cell, n in (removed-old).items() if cell[index] == value),
                            "cumulative_excluded": sum(n for cell, n in removed.items() if cell[index] == value),
                            "remaining": sum(n for cell, n in after.items() if cell[index] == value)}
                for value in sorted({cell[index] for cell in before})}
    payload = {"format": "kakeya-round8-matching-threshold-profile-exclusions-v1",
               "original_input_file": SOURCE, "original_input_sha256": SOURCE_SHA256,
               "original_profiles": 183476, "intermediate_profiles": 183301,
               "previously_excluded_profiles": 175, "newly_excluded_profiles": 570,
               "cumulative_excluded_profiles": 745, "remaining_profiles": 182731,
               "earlier_nested_stage_sizes": [16, 128, 175],
               "prior_stage_pins": PRIOR_PINS, "analytic_proof_pins": PROOF_PINS,
               "producer_verifier": str(Path(__file__).resolve().relative_to(ROOT)),
               "producer_verifier_sha256": digest(Path(__file__).read_bytes()),
               "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(final_bytes),
               "scope": "Every placement and actual fibre shape of these745 whole profiles, in both rings. No additional SAT-role credit.",
               "mathematical_dependencies": [
                   "In a missing heavy direction, k active light fibres have capacity at most the sum of the k largest heavy pair ceilings; HL partners are distinct and LL edges can be paid by unused heavy ceilings.",
                   "The least prefix length rho reaching16 is therefore a lower bound on active light incidences per missing direction.",
                   "For nine heavy residues, at least three directions are missing, and their set is plane-free, giving3*rho<=L2+2*L3.",
                   "The criterion uses the actual profile's heavy weights and light2/light3 counts. It uses neither inherited energy metadata nor spectrum/sumset tables.",
                   "The prior175 profiles are included within745, with16 and128 nested inside175; stages are not double-counted."
               ],
               "exhaustive_scan": scan, "by_support": aggregate(0), "by_maximum": aggregate(1),
               "by_support_and_maximum": [{"support_size": s, "maximum": m, "original": before[s, m],
                   "previously_excluded": old[s, m], "newly_excluded": removed[s, m]-old[s, m],
                   "cumulative_excluded": removed[s, m], "remaining": after[s, m]} for s, m in sorted(before)],
               "certificates": rows}
    return payload, final_bytes


def negative_controls(rows, raw, profiles, first16, prior128, prior175):
    original = next(row for row in rows if not row["already_in_previous175_stage"])
    bad_prefix = list(original["heavy_ceiling_prefix_sums"])
    bad_prefix[original["matching_incidence_threshold_rho"]-1] = 16
    mutations = [
        ("invalid_source_line", "source_line", 0),
        ("uncertified_source_line", "source_line", 1),
        ("wrong_source_hash", "source_line_sha256", "0"*64),
        ("wrong_heavy_count", "heavy_count", 10),
        ("wrong_heavy_ceilings", "heavy_pair_ceilings_descending", [9]*9),
        ("false_prefix_bracket", "heavy_ceiling_prefix_sums", bad_prefix),
        ("nonminimal_rho", "matching_incidence_threshold_rho", original["matching_incidence_threshold_rho"]+1),
        ("wrong_lower_prefix", "prefix_capacity_with_rho_minus_one_lights", 16),
        ("wrong_upper_prefix", "prefix_capacity_with_rho_lights", 15),
        ("wrong_available_incidence", "available_light_incidences_upper_bound", -1),
        ("double_counted_previous_stage", "already_in_previous175_stage", True),
        ("boolean_in_integer_field", "heavy_count", True),
    ]
    controls = []
    for label, field, value in mutations:
        altered = deepcopy(original); altered[field] = value
        try:
            check_row(altered, raw, profiles, first16, prior128, prior175)
        except (ValueError, KeyError, TypeError):
            controls.append({"control": label, "rejected": True})
        else:
            raise ValueError("Corrupted certificate accepted: " + label)
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Create missing deterministic matching-incidence artifacts")
    args = parser.parse_args()
    started = time.monotonic()
    atomic_write(RECEIPT, json_bytes({"status": "RUNNING", "write_mode": args.write}))
    try:
        raw, profiles, first16, prior128, prior175, prior_survivors, inherited_proof_pins = read_inputs()
        payload, survivor_bytes = build_expected(raw, profiles, first16, prior128, prior175, prior_survivors)
        payload_bytes = json_bytes(payload)
        if args.write:
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                require(not path.exists() or path.read_bytes() == data,
                        "Refusing to overwrite a different semantic artifact: " + path.name)
            for path, data in ((CERTIFICATE, payload_bytes), (SURVIVORS, survivor_bytes)):
                if not path.exists():
                    atomic_write(path, data)
        require(CERTIFICATE.read_bytes() == payload_bytes, "Stored745 certificate differs from exact regeneration")
        require(SURVIVORS.read_bytes() == survivor_bytes, "Stored745 frontier differs in bytes or order")
        stored = json.loads(CERTIFICATE.read_text())
        checked = [check_row(row, raw, profiles, first16, prior128, prior175) for row in stored["certificates"]]
        require(len(set(checked)) == len(checked) == 745, "Missing or duplicated matching certificate")
        controls = negative_controls(stored["certificates"], raw, profiles, first16, prior128, prior175)
        for path, expected in PRIOR_PINS.items():
            require(digest((ROOT / path).read_bytes()) == expected, "Prior semantic artifact changed during replay")
        receipt = {key: payload[key] for key in (
            "original_input_file", "original_input_sha256", "original_profiles", "intermediate_profiles",
            "previously_excluded_profiles", "newly_excluded_profiles", "cumulative_excluded_profiles", "remaining_profiles",
            "by_support", "by_maximum", "by_support_and_maximum", "prior_stage_pins", "analytic_proof_pins",
            "exhaustive_scan", "scope")}
        receipt.update({"status": "PASS_MATCHING_INCIDENCE_PROFILE_REPLAY",
                        "transitive_prior_analytic_pins": inherited_proof_pins,
                        "coverage": {
                            "every_original_profile_scanned": True,
                            "excluded_original_source_lines": checked,
                            "previously_excluded_original_source_lines": sorted(prior175),
                            "newly_excluded_original_source_lines": sorted(set(checked)-prior175),
                            "all_prefix_threshold_brackets_checked_exactly": True,
                            "every_retained_line_preserved_byte_identically_and_in_order": True,
                            "direct_minus745_and_prior175_minus570_regeneration_identical": True,
                            "all_prior_stage_semantic_artifacts_unchanged": True,
                            "energy_metadata_used_in_exclusion": False},
                        "certificate_file": str(CERTIFICATE.relative_to(ROOT)), "certificate_sha256": digest(CERTIFICATE.read_bytes()),
                        "survivor_file": str(SURVIVORS.relative_to(ROOT)), "survivor_sha256": digest(survivor_bytes),
                        "verifier_sha256": digest(Path(__file__).read_bytes()), "negative_controls": controls,
                        "dependency_boundary": "Pinned analytic proofs supply the geometric implications. This exact integer and byte-coverage replay is not proof-assistant formalized. No SAT case is credited.",
                        "elapsed_seconds": round(time.monotonic()-started, 6)})
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
